from .base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType


class DrupalSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.DRUPAL)

    def get_setup_commands(self):
        raise NotImplementedError("Not implemented")