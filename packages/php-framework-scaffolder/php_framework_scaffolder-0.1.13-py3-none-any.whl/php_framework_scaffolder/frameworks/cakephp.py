from .base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType
from typing import List


class CakePHPSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.CAKEPHP)

    def get_setup_commands(self) -> List[str]:
        return [
            "docker compose down -v",
            "docker compose build",
            "docker compose up -d",
            "docker compose exec -w /app app php bin/cake.php migrations migrate --no-interaction --no-ansi"
        ]

    def get_routes_command(self) -> str:
        return "docker compose exec -w /app app php bin/cake.php routes --format json --no-interaction --no-ansi"
