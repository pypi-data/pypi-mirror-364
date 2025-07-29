from .base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType


class SlimSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.SLIM)

    def get_setup_commands(self):
        raise NotImplementedError("Not implemented")