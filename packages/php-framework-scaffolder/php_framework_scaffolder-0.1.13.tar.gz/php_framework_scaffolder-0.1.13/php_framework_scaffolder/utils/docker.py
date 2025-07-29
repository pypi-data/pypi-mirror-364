"""
Docker utilities for running Docker commands and managing containers.

This module provides functionality to execute Docker and Docker Compose commands
with proper error handling and logging.
"""

import subprocess
import sys
from typing import List, Tuple
from php_framework_scaffolder.utils.logger import get_logger

logger = get_logger(__name__)

def run_docker_compose_command_realtime(command: List[str], cwd: str) -> bool:
    """Execute a Docker Compose command in the specified directory and display output in real-time.

    Args:
        command: The Docker Compose command to execute as a list of strings
        cwd: The working directory where the command should be executed
        
    Returns:
        True if the command executed successfully, False if failed
    """
    try:
        logger.info(f"Running command: {' '.join(command)} in {cwd}")
        
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=None,
            stderr=None,
            text=True
        )
        
        exit_code = process.wait()

        return exit_code == 0
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False

def run_docker_compose_command(command: List[str], cwd: str) -> Tuple[bool, str, str]:
    """Execute a Docker Compose command in the specified directory.
    
    Args:
        command: The Docker Compose command to execute as a list of strings
        cwd: The working directory where the command should be executed
        
    Returns:
        A tuple containing:
        - bool: True if the command executed successfully, False if failed
        - str: The stdout output captured from the command
        - str: The stderr output captured from the command
        
    Examples:
        >>> success, stdout, stderr = run_docker_compose_command(["docker", "compose", "up", "-d"], "/path/to/project")
        >>> if success:
        ...     print("Command executed successfully")
        ...     print(f"Output: {stdout}")
    """
    try:
        logger.info(f"Running command: {' '.join(command)} in {cwd}")
        
        # Use Popen to capture and display output in real-time
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        stdout_lines = []
        stderr_lines = []
        
        # Read stdout and stderr in real-time
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if stdout_line:
                print(stdout_line.rstrip())  # Display to console in real-time
                stdout_lines.append(stdout_line)
                
            if stderr_line:
                print(stderr_line.rstrip(), file=sys.stderr)  # Display to console in real-time
                stderr_lines.append(stderr_line)
                
            # Check if process has finished
            if process.poll() is not None:
                # Read remaining output
                remaining_stdout, remaining_stderr = process.communicate()
                if remaining_stdout:
                    print(remaining_stdout.rstrip())
                    stdout_lines.append(remaining_stdout)
                if remaining_stderr:
                    print(remaining_stderr.rstrip(), file=sys.stderr)
                    stderr_lines.append(remaining_stderr)
                break
                
            if not stdout_line and not stderr_line:
                break
        
        # Merge all output
        stdout_output = ''.join(stdout_lines)
        stderr_output = ''.join(stderr_lines)
        
        # Check exit code
        exit_code = process.returncode
        if exit_code == 0:
            return True, stdout_output, stderr_output
        else:
            logger.error(f"Command failed with exit code {exit_code}", stdout=stdout_output, stderr=stderr_output)
            return False, stdout_output, stderr_output
            
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False, "", str(e) 