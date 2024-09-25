from flask import Blueprint, jsonify, request
from .models import User, Todo
from .extensions import db, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user



main = Blueprint('main', __name__)

### JWT set up  ###

@jwt.user_lookup_loader
def user_identity_lookup(user):
    return user.id 

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


### Routes ###

# helpder functions

def isOwner(todo):
    user_id = current_user.id
    if user_id is None or user_id != todo.user_id:
        return False
    return True
    

# /register -> register as a user  -- POST
@main.route('/register', methods=['POST'])
def register():
    #user data
    data = request.json
    username =  data.get("username", None)
    email = data.get("email", None)
    password = data.get("password", None)

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
    
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback in case of error
        # Optionally, log the error
        return jsonify({"msg": "Database error", "error1": str(e)}), 500
    
    except Exception as e:
        return jsonify({"msg": "server error", "error2": str(e)}), 500
    
    except:
        return jsonify({"msg":"somryhin else"})


# /login -> login as a user and receive jwt token --POST
@main.route('/login', methods=['POST'])
def login():
    #user data
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username is None or password is None:
        return jsonify({"msg": "you must provide a username and a password"}), 400

    #get user and validation
    user = User.query.filter_by(username=username).first()

    if  user is None or not user.check_password(password):
        return jsonify({'msg' : 'incorrect details'}), 400

    #provide access token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# /todos -> create new todo --POST
@main.route('/', methods=['POST'])
@jwt_required()
def create_todo():
    #user id from jwt token
    user_id = current_user.id
    if user_id is None:
        return jsonify({"msg":"Authorisation token did not return a valid user"}), 401
    #user data
    title = request.json.get("title", None)
    description = request.json.get("description", None)

    if title is None or description is None:
        return jsonify({"msg":"you must provide a title and a description"}), 400

    #adding to db
    new_todo = Todo(title=title, description=description, status="ACTIVE", user_id= user_id)
    db.session.add(new_todo)
    db.session.commit()
    todo = Todo.query.filter_by(title=title, user_id = user_id).first_or_404()
    return jsonify(todo.to_dict()), 201

# /todos -> get all todos for a user --GET
@main.route('/', methods=['GET'])
@jwt_required()
def get_items():
    # get user id and then return todos from that user
    user_id = current_user.id   
    if user_id is None:
        return jsonify({"msg":"Authorisation token did not return a valid user"}), 400
    # query params
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search', "")

    #filtering to user's items
    userTodos = Todo.query.filter_by(user_id = user_id)
    #search results
    search_result = userTodos.filter(or_(
        Todo.title.like(f"%{search}%"),
        Todo.description.like(f"%{search}%")
        )
    )
    # paginate results
    paginated_result = search_result.paginate(page=page, per_page=limit, error_out=False)
    #return final data
    todoData = [todo.to_dict() for todo in paginated_result]
    return jsonify({
        'todos': todoData,  # Serialized todo items
        'total': paginated_result.total,  # Total number of todos
        'pages': paginated_result.pages,  # Total number of pages
        'current_page': paginated_result.page  # Current page number
    }), 200


# /todos/id -> update existing todo --PUT
@main.route('/<id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
    todo = Todo.query.filter_by(id = int(id)).first_or_404()
    if isOwner(todo):
        data = request.json
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.status = data.get('status', todo.status)
        db.session.commit()
        updated_todo = Todo.query.filter_by(id = int(id)).first_or_404()
        return jsonify(updated_todo.to_dict()), 201
    return jsonify({"msg": "you do not have permission for this action"}), 401



# /todos/id -> delete existing todo --DELETE
@main.route('/<id>', methods = ["DELETE"])
@jwt_required()
def delete_todo(id):
    todo = Todo.query.filter_by(id = id).first_or_404()
    if isOwner(todo):
        db.session.delete(todo)
        db.session.commit()
        return '', 204
    return jsonify({"msg": "You do not have authorisation for this item"}), 401
