from .base import BaseFrameworkSetup
from php_framework_detector.core.models import FrameworkType


class FastRouteSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.FASTROUTE)

    def get_setup_commands(self):
        raise NotImplementedError("Not implemented")