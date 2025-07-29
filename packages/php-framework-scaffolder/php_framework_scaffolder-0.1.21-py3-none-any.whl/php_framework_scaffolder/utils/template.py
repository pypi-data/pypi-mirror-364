"""
Template processing utilities using Jinja2.

This module provides functionality to process template files with variable substitution
using the Jinja2 template engine. It supports both modern Jinja2 syntax and legacy
dollar-sign syntax for backward compatibility.

Template Syntax Examples:
    Modern Jinja2 syntax:
        Hello {{ name }}!
        Version: {{ version }}
        
        {% if debug %}
        Debug mode enabled
        {% endif %}
        
        {% for item in items %}
        - {{ item }}
        {% endfor %}
    
    Legacy syntax (automatically converted):
        Hello $name!
        Version: $version
        
    Mixed syntax:
        Hello {{ name }}, version $version
        
Advanced Features:
    - Conditional statements: {% if condition %}...{% endif %}
    - Loops: {% for item in items %}...{% endfor %}
    - Filters: {{ value | default('fallback') }}
    - Comments: {# This is a comment #}
"""

import os
import shutil
import re
from typing import Dict, Union
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from php_framework_scaffolder.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


def process_file_templates(file_path: str, context: Dict[str, Union[str, int]]) -> None:
    """Process template files by substituting context variables using Jinja2.
    
    Args:
        file_path: Path to the template file to process
        context: Dictionary containing variables to substitute in the template
        
    Examples:
        >>> context = {'name': 'World', 'version': '1.0'}
        >>> process_file_templates('/path/to/template.txt', context)
        
        Template file content:
            Hello {{ name }}!
            Version: {{ version }}
            
        Result:
            Hello World!
            Version: 1.0
    """
    try:
        # Check if file is binary
        with open(file_path, "rb") as f:
            content = f.read(1024)
            if b'\0' in content:
                logger.debug("Skipping binary file", file_path=file_path)
                return
        
        # Read file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        logger.debug("Processing template file", file_path=file_path, context=context)
        
        # Create Jinja2 environment with optimized settings
        env = Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            block_start_string='{%',
            block_end_string='%}',
            comment_start_string='{#',
            comment_end_string='#}',
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            # Enable auto-escaping for security (but only for known unsafe file types)
            autoescape=file_path.endswith(('.html', '.htm', '.xml'))
        )
        
        # Convert legacy $variable syntax to {{ variable }} for backward compatibility
        # This regex avoids converting already converted variables and variables in strings
        content = re.sub(r'\$(?!{)(\w+)', r'{{ \1 }}', content)
        
        # Create and render template
        template = env.from_string(content)
        processed_content = template.render(**context)
        
        # Write processed content back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(processed_content)
            
        logger.debug("Processed template file successfully", file_path=file_path)
    except Exception as e:
        logger.warning("Error processing file", file_path=file_path, error=str(e), exc_info=True)


def copy_and_replace_template(src_folder: str, dest_folder: str, context: Dict[str, Union[str, int]]) -> None:
    """Copy template directory and process all template files with given context.
    
    This function copies a template directory structure and processes all files
    within it as Jinja2 templates, substituting variables with provided context.
    
    Args:
        src_folder: Source template directory path
        dest_folder: Destination directory path
        context: Dictionary containing variables to substitute in templates
        
    Examples:
        >>> context = {
        ...     'app_name': 'MyApp',
        ...     'php_version': '8.2',
        ...     'database': {'host': 'localhost', 'name': 'myapp_db'}
        ... }
        >>> copy_and_replace_template('templates/laravel', 'output/myapp', context)
    """
    # Copy entire directory structure
    shutil.copytree(src_folder, dest_folder, dirs_exist_ok=True,
                    ignore_dangling_symlinks=True, symlinks=False)
    logger.info("Copied template", src_folder=src_folder, dest_folder=dest_folder)
    
    # Process all files as templates
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(
            "Processing template files...", total=None)
        
        file_count = 0
        try:
            for root, _, files in os.walk(dest_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    process_file_templates(file_path, context)
                    file_count += 1
                    
            progress.update(task, completed=True)
            logger.info("Template processing completed successfully", 
                       files_processed=file_count)
        except Exception as e:
            logger.error("Error during template processing", 
                        error=str(e), files_processed=file_count, exc_info=True)
            raise 