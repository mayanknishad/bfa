"""
CONFIGURATION FILES
"""

import os

class BaseConfig(object):
    """
    Base configuration
    """
    DEBUG = True
    FILE = 'local.cfg'

class DevelopmentConfig(BaseConfig):
    """
    Staging configuration
    """
    FILE = 'dev.cfg'
    DEBUG = True

class ProductionConfig(BaseConfig):
    """
    Production configuration
    """
    FILE = 'prod.cfg'
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': BaseConfig,
}

def configure_app(app):
    """
    Configures app depending on the environmental variable or uses default
    """
    env_config = os.getenv('FLASK_CONFIGURATION', 'default')
    app.config.from_pyfile(config[env_config].FILE)



