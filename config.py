import os

# Define base directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """A class that stores configurations as class variables."""
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'keep-it-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'messenger.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    DEBUG = False
    DEVELOPMENT = False


class DevConfig(Config):
    """A class that stores development configurations as class variables."""
    DEVELOPMENT = True
    DEBUG = True


config = {
    'dev': DevConfig,
    'default': Config
    }
