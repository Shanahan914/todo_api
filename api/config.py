import os

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:ppsdkos!df9495@localhost/tododb')
SQLALCHEMY_TRACK_MODIFICATIONS = False 

JWT_SECRET_KEY = "asdfosij3438fuov938hfou38rf32f0sfsdfj"  # change this for prod