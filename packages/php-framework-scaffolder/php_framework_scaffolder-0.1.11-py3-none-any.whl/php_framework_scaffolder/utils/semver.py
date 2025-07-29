import re
from packaging import version


def select_php_version(php_requirement: str, default_version: str = "8.4") -> str:
    """
    Select the PHP version based on the requirement.

    Args:
        php_requirement (str): The PHP requirement.
        default_version (str): The default version to use if the requirement is not found.

    Returns:
        str: The selected PHP version.

    >>> select_php_version("^8.4")
    '8.4'

    >>> select_php_version("8.4")
    '8.4'

    >>> select_php_version("*")
    '8.4'

    >>> select_php_version("^8.3")
    '8.3'

    >>> select_php_version("^8.2")
    '8.2'

    >>> select_php_version(">= 8.3.0")
    '8.3.0'

    >>> select_php_version("^8.2")
    '8.2'

    >>> select_php_version("^8.1")
    '8.1'
    """
    
    if not php_requirement or php_requirement.strip() == '*':
        return default_version
    try:
        versions = re.findall(r'(\d+(?:\.\d+)*)', php_requirement)
        if not versions:
            return default_version
        if '^' in php_requirement:
            versions.sort(key=lambda v: version.parse(v))
        else:
            versions.sort(key=lambda v: version.parse(v), reverse=True)
        return versions[0]
    except Exception:
        return default_version
