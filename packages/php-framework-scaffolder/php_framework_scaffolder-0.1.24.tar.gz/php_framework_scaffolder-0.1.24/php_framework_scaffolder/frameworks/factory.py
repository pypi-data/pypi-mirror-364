from php_framework_detector.core.models import FrameworkType
from php_framework_scaffolder.frameworks.laravel import LaravelSetup
from php_framework_scaffolder.frameworks.symfony import SymfonySetup
from php_framework_scaffolder.frameworks.codeigniter import CodeIgniterSetup
from php_framework_scaffolder.frameworks.cakephp import CakePHPSetup
from php_framework_scaffolder.frameworks.yii import YiiSetup
from php_framework_scaffolder.frameworks.thinkphp import ThinkPHPSetup
from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_scaffolder.frameworks.slim import SlimSetup
from php_framework_scaffolder.frameworks.fatfree import FatFreeSetup
from php_framework_scaffolder.frameworks.fastroute import FastRouteSetup
from php_framework_scaffolder.frameworks.fuel import FuelSetup
from php_framework_scaffolder.frameworks.phalcon import PhalconSetup
from php_framework_scaffolder.frameworks.phpixie import PhPixieSetup
from php_framework_scaffolder.frameworks.popphp import PopPHPSetup
from php_framework_scaffolder.frameworks.laminas import LaminasSetup
from php_framework_scaffolder.frameworks.zendframework import ZendFrameworkSetup
from php_framework_scaffolder.frameworks.drupal import DrupalSetup
from php_framework_scaffolder.frameworks.drush import DrushSetup


def get_framework_handler(framework: FrameworkType) -> BaseFrameworkSetup:
    handlers = {
        FrameworkType.LARAVEL: LaravelSetup(),
        FrameworkType.SYMFONY: SymfonySetup(),
        FrameworkType.CODEIGNITER: CodeIgniterSetup(),
        FrameworkType.CAKEPHP: CakePHPSetup(),
        FrameworkType.YII: YiiSetup(),
        FrameworkType.THINKPHP: ThinkPHPSetup(),
        FrameworkType.SLIM: SlimSetup(),
        FrameworkType.FATFREE: FatFreeSetup(),
        FrameworkType.FASTROUTE: FastRouteSetup(),
        FrameworkType.FUEL: FuelSetup(),
        FrameworkType.PHALCON: PhalconSetup(),
        FrameworkType.PHPIXIE: PhPixieSetup(),
        FrameworkType.POPPHP: PopPHPSetup(),
        FrameworkType.LAMINAS: LaminasSetup(),
        FrameworkType.ZENDFRAMEWORK: ZendFrameworkSetup(),
        FrameworkType.DRUPAL: DrupalSetup(),
        FrameworkType.DRUSH: DrushSetup(),
    }
    return handlers[framework]
