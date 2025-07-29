import re
from packaging import version


def select_php_version(php_requirement: str, default_version: str = "8.4") -> str:
    if not php_requirement or php_requirement.strip() == '*':
        return default_version
    try:
        versions = re.findall(r'(\d+\.\d+)', php_requirement)
        if not versions:
            return default_version
        if '^' in php_requirement:
            versions.sort(key=lambda v: version.parse(v))
        else:
            versions.sort(key=lambda v: version.parse(v), reverse=True)
        return versions[0]
    except Exception:
        return default_version
