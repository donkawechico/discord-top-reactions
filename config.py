import os 

class Config:
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# choose the right config based on the environment
if os.getenv('ENV') == 'dev':
    config = DevelopmentConfig()
else:
    config = ProductionConfig()