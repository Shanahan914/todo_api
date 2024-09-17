from .extensions import db
from sqlalchemy import Integer, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import enum 


class Todo_status(enum.Enum):
    ACTIVE = "Active"
    COMPLETED = "Complete"


class User(db.Model):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(String(128), nullable=False)
    email : Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    #relationship with todo
    todo: Mapped[list['Todo']] = relationship('Todo', back_populates='user')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<username: {self.username}, user id: {self.id}>'


class Todo(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(nullable=False)
    description : Mapped[str] = mapped_column(nullable=False)
    status : Mapped[Todo_status] = mapped_column(Enum(Todo_status))

    #foreign key to User table
    user_id : Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user : Mapped['User'] = relationship('User', back_populates='Todo')

    def __repr__(self):
        return f'<title: {self.title}, task id: {self.id}>'
    
    def to_dict(self):
        return {
            'id' : self.id,
            'title': self.title,
            'description' : self.description,
            'status': self.status
        }


