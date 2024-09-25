import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:ppsdkos!df9495@localhost/tododb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    JWT_SECRET_KEY = "asdfosij3438fuov938hfou38rf32f0sfsdfj"  # change this for prod

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    JWT_SECRET_KEY = 'k4mfgnd84v49fn349fsfjas0102dfwqazpnebyvg'