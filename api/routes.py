from flask import Blueprint, jsonify, request
from .models import User, Todo
from .extensions import db, jwt


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user


main = Blueprint('main', __name__)

### JWT set up  ###

@jwt.user_lookup_loader
def user_identity_lookup(user):
    return user.id 

def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

### Routes ###

# /register -> register as a user  -- POST
@main.route('/register', methods=['POST'])
def register():
    #user data
    data = request.user
    username =  data.get("username", None)
    email = data.get("email", None)
    password = data.json.get("password", None)

    #validation
    if username is None or password is None or email is None:
        return jsonify({"msg": "you must provide a username, email and password."}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"msg":"Username already taken"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg":"this email is already linked to an account"}), 400

    if len(password) < 6:
        return jsonify({"msg":"password must be at least 6 characters."}), 400
    
    #creating new user
    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "user added successfully."}), 201
    except:
        return jsonify({"msg": "server error"}), 500


# /login -> login as a user and receive jwt token --GET
@main.route('/login', methods=['POST'])
def login():
    #user data
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    #get user and validation
    user = User.query.filter_by(username=username).first()

    if  user is None or not User.check_password(password):
        return jsonify({'msg' : 'incorrect password'})

    #provide access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# /todos -> create new todo --POST
@main.route('/', methods=['POST'])
@jwt_required()
def create_todo():
    #user id from jwt token
    user_id = current_user.id
    if user_id is None:
        return jsonify({"msg":"Authorisation token did not return a valid user"})
    #user data
    title = request.json.get("title", None)
    description = request.json.get("description", None)
    #adding to db
    new_todo = Todo(title=title, description=description, status="Active", user_id= user_id)
    db.session.add(new_todo)
    db.session.commit()
    todo = Todo.query.filter_by(title=title).first_or_404()
    return jsonify(todo.to_dict())

# /todos -> get all todos for a user --GET
@main.route('/', methods=['GET'])
@jwt_required()
def get_items():
    # get user id and then return todos from that user
    user_id = current_user.id
    if user_id is None:
        return jsonify({"msg":"Authorisation token did not return a valid user"})
    TodoData = User.query.filter_by(user_id = user_id)
    return jsonify([todo.to_dict() for todo in TodoData])


# /todos/id -> update existing todo --PUT


# /todos/id -> delete existing todo --DELETE

