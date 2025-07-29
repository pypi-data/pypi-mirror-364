import os
import shutil
import string
import json
import uuid
import git
import tempfile
import secrets
from pathlib import Path
from typing import Dict, Union, List, Optional, Any
from packaging import version
from php_framework_detector.core.models import FrameworkType
from php_framework_scaffolder.utils.semver import select_php_version
from php_framework_scaffolder.utils.template import copy_and_replace_template
from php_framework_scaffolder.utils.logger import get_logger
from php_framework_scaffolder.utils.docker import run_docker_compose_command, run_docker_compose_command_realtime
from php_framework_scaffolder.utils.composer import read_composer_json

logger = get_logger(__name__)


class BaseFrameworkSetup:
    def __init__(self, framework_type: FrameworkType):
        self.framework_type = framework_type
        self.template_dir = Path(f"templates/{framework_type.value}")
        self.target_folder = Path(tempfile.mkdtemp(), "SpecPHP", str(uuid.uuid4()))

    def setup(self, repository_path: Path, apk_packages: List[str] = [], php_extensions: List[str] = []) -> None:
        composer_data = read_composer_json(os.path.join(repository_path, "composer.json"))
        php_requirement = composer_data.get("require", {}).get("php", "")
        logger.info(f"PHP requirement: {php_requirement}")
        php_version = select_php_version(php_requirement)
        logger.info(f"Selected PHP version: {php_version}")
        
        apk_packages = list(set(apk_packages + [
            "$PHPIZE_DEPS",
            "git",
            "gmp-dev",
            "icu-dev",
            "libffi-dev",
            "librdkafka-dev",
            "libssh2-dev",
            "libssh2",
            "libxml2-dev",
            "libxslt-dev",
            "libzip-dev",
            "linux-headers",
            "mariadb-client",
            "mysql-client",
            "openldap-dev",
            "postgresql-client",
            "postgresql-dev",
            "yarn",
            "zlib-dev",
        ]))
        apk_packages.sort()
        
        php_extensions = list(set(php_extensions + [
            "bcmath",
            "calendar",
            "exif",
            "ffi",
            "ftp",
            "gd",
            "gmp",
            "intl",
            "ldap",
            "pcntl",
            "pdo_mysql",
            "pdo_pgsql",
            "pgsql",
            "rdkafka",
            "redis",
            "soap",
            "sockets",
            "sodium",
            "xsl",
            "zip",
        ]))
        php_extensions.sort()

        context = {
            "php_version": php_version,
            "db_database": "app",
            "db_username": "user",
            "db_password": secrets.token_hex(8),
            "apk_packages": apk_packages,
            "php_extensions": php_extensions,
        }
        template_path = Path(os.path.dirname(__file__)).parent / Path(f"templates/{self.framework_type.value}")
        logger.info(f"Template path: {template_path}")

        logger.info(f"Created target folder: {self.target_folder}")

        copy_and_replace_template(template_path, self.target_folder, context)
        logger.info(f"Copied template to {self.target_folder}")

        git.Repo.clone_from(repository_path, self.target_folder / "src")
        logger.info(f"Cloned repository to {self.target_folder / 'src'}")

        build_command = self.get_docker_build_command()
        logger.info(f"Executing build command: {build_command}")
        run_docker_compose_command_realtime(build_command, self.target_folder)

        up_command = self.get_docker_up_command()
        logger.info(f"Executing up command: {up_command}")
        run_docker_compose_command_realtime(up_command, self.target_folder)

        setup_commands = self.get_setup_commands()
        logger.info("Starting Docker containers setup", total_commands=len(setup_commands))

        for i, command in enumerate(setup_commands, 1):
            logger.info(f"Executing setup command {i} of {len(setup_commands)}", command=command)
            run_docker_compose_command_realtime(command, self.target_folder)
        logger.info("Docker containers setup completed")
        
    def extract_swagger(self, swagger_json_path: Path) -> None:
        swagger_command = self.get_swagger_php_openapi_command()
        logger.info(f"Executing swagger command: {swagger_command}")
        run_docker_compose_command_realtime(swagger_command, self.target_folder)

        copy_swagger_command = self.get_copy_swagger_php_openapi_output_command(swagger_json_path)
        logger.info(f"Executing copy swagger command: {copy_swagger_command}")
        run_docker_compose_command_realtime(copy_swagger_command, self.target_folder)
        logger.info(f"Swagger command completed")

    def extract_routes(self, routes_json_path: Path) -> None:
        routes_command = self.get_routes_command()
        logger.info(f"Executing routes command: {routes_command}")
        _, routes, _ = run_docker_compose_command(routes_command, self.target_folder)
        logger.warning(routes)
        with open(routes_json_path, "w") as f:
            f.write(routes)
        logger.info(f"Routes command completed")


    def shutdown(self) -> None:
        cleanup_command = self.get_docker_down_command()
        logger.info(f"Executing cleanup command: {cleanup_command}")
        run_docker_compose_command_realtime(cleanup_command, self.target_folder)

        shutil.rmtree(self.target_folder)
        logger.info(f"Removed target folder: {self.target_folder}")


    def get_docker_build_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "build",
        ]
    
    def get_docker_up_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "up",
            "--detach"
        ]

    def get_docker_down_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "down",
            "-v"
        ]

    def get_setup_commands(self) -> List[List[str]]:
        raise NotImplementedError("Not implemented")

    def get_routes_command(self) -> List[str]:
        raise NotImplementedError("Not implemented")

    def get_swagger_php_openapi_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "exec",
            "-w",
            "/app",
            "app",
            "php",
            "-d",
            "error_reporting=~E_DEPRECATED",
            "/root/.composer/vendor/bin/openapi",
            "--output",
            "/app/swagger.json",
            "--exclude",
            "vendor",
            "/app"
        ]

    def get_copy_swagger_php_openapi_output_command(self, swagger_json_path: Path) -> List[str]:
        return [
            "docker",
            "compose",
            "cp",
            "app:/app/swagger.json",
            str(swagger_json_path)
        ]   
