import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address 


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
       
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "40 per hour"],
    storage_uri='redis://127.0.0.1:6379/0'
)