import pytest
import jwt
from flask_jwt_extended import create_access_token
from api import create_app, db
from api.models import User, Todo

### setting up app instance for testing

@pytest.fixture(scope='session')
def app():
    #initialise app with testing config
    app = create_app(config_name='testing')

    with app.app_context():
        db.create_all() #create testing db
        #creates app instance without returning
        yield app
      

@pytest.fixture(scope='session')
def client(app):
    return app.test_client() 

@pytest.fixture(scope='function', autouse=True)
def session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()

### helper functions

def create_test_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def create_post(title, description, id):
    post = Todo(title = title, 
    description = description,
    user_id = id,
    status = "ACTIVE")
    db.session.add(post)
    db.session.commit()
    return post

### api tests

# ---------------------------------------------------------------#
## 1.        /register           [post] ##
# ---------------------------------------------------------------#

#correct post request
def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['msg'] == 'user added successfully.'


#incorrect use of an already taken username
def test_register_repeat_username(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser_2@example.com',
        'password': 'password123'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['msg'] == 'Username already taken'

#incorrect use of an already used email
def test_register_repeat_email(client):
    response = client.post('/register', json={
        'username': 'testuser2',
        'email': 'testuser@example.com',
        'password': 'password123'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['msg'] == 'this email is already linked to an account'

#incorrect password - too short
def test_register_short_password(client):
    response = client.post('/register', json={
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'password': 'pass'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['msg'] == 'password must be at least 6 characters.'

# ---------------------------------------------------------------#
##  2.          /login          [post] ##
# ---------------------------------------------------------------#

#correct login attempt
def test_login(client):
    response = client.post('/login', json={
        'username' : 'testuser',
        'password' : 'password123'
    })

    assert response.status_code == 200

#bad request - incorrect password
def test_login(client):
    response = client.post('/login', json={
        'username' : 'testuser',
        'password' : 'wrong'
    })

    assert response.status_code == 400

#bad request - missing username
def test_login_missing_username(client):
    response = client.post('/login', json={
        'password' : 'password123'
    })

    assert response.status_code == 400

#bad request - missing password
def test_login_missing_password(client):
    response = client.post('/login', json={
        'username' : 'testuser',
    })

    assert response.status_code == 400

#bad request - incorrect username
def test_login_unknown_user(client):
    response = client.post('/login', json={
        'username' : 'testuser555',
        'password' : 'password123'
    })

    assert response.status_code == 400


# ---------------------------------------------------------------#
## 3.           /           [post] ##
# ---------------------------------------------------------------#


#bad request - no jwt
def test_create_todo_no_token(client):
    response = client.post('/', json={
	    "title":"my third todo",
	    "description": "decide on my plans for next week"
    })

    assert response.status_code == 401

def test_create_todo(client):
    #creating test user
    user = create_test_user(
        username='createUser', 
        email='create@gmail.com',
        password='password1')

    #generating the access token for the post request
    access_token = create_access_token(identity=user.id)

    #test data
    title = "my test todo"
    description = "finish all these tests"

    response = client.post('/', json={
	    "title": title,
	    "description": description
    },
    headers = {
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == title
    assert data['description'] == description


# ---------------------------------------------------------------#
## 4.           /           [get] ##
# ---------------------------------------------------------------#

## TODO - need to add tests for filtering and search terms.

#correct - no todos
def test_get_posts_empty(client):
    user = create_test_user(
        username='getUser', 
        email='get@gmail.com',
        password='password1')

    #generating the access token for the post request
    access_token = create_access_token(identity=user.id) 

    response = client.get('/', headers ={
      'Authorization': f'Bearer {access_token}'  
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['todos'] == []

#correct - list of todos
def test_get_posts_empty(client):
    user = create_test_user(
        username='getUser2', 
        email='get2@gmail.com',
        password='password1')
    
    #test data
    title = "my test todo"
    description = "finish all these tests"
    
    #creating a post
    post = create_post(title = title, description = description, id= user.id)
   
    #generating the access token for the post request
    access_token = create_access_token(identity=user.id) 

    response = client.get('/', headers ={
      'Authorization': f'Bearer {access_token}'  
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['todos']) == 1
    assert data['todos'][0]['title'] == title


# ---------------------------------------------------------------#
## 5.           /id           [put] ##
# ---------------------------------------------------------------#

#correct - change the title
def test_put_title(client):
    #create user and token
    user = create_test_user(username='putUser', 
        email='put@gmail.com',
        password='password1')
    
    access_token = create_access_token(identity=user.id)
    
    #create a post
    title = 'original title'
    new_title = 'amended title'
    description = 'original description'
    post = create_post(title=title, description=description, id=user.id)

    response = client.put(f'/{post.id}', json={
        'title': new_title
    }, headers = {
        'Authorization': f'Bearer {access_token}'  
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == new_title
    assert data['description'] == description

#no auth - no auth token
def test_put_no_auth(client):
    #create user and token
    user = create_test_user(username='putUse2', 
        email='put2@gmail.com',
        password='password1')
    
    #create a post
    title = 'original title'
    new_title = 'amended title'
    description = 'original description'
    post = create_post(title=title, description=description, id=user.id)

    response = client.put(f'/{post.id}', json={
        'title': new_title
    }, headers = {
        # 'Authorization': f'Bearer thisIsNotAToken'  
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['msg'] == 'Missing Authorization Header'

#bad request - attempt to update todo that is not linked to the current user
def test_put_not_owned(client):
    #create user who owns the todo
    todoOwner = create_test_user(username='putUser3', 
        email='put3@gmail.com',
        password='password1')
    
    #create a post for todoOwner
    title = 'original title'
    new_title = 'amended title'
    description = 'original description'
    post = create_post(title=title, description=description, id=todoOwner.id)

    #create a third party
    user = create_test_user(username='putUser4', 
        email='put4@gmail.com',
        password='password1')
    access_token = create_access_token(identity=user.id)

    #request to access the todo from the third party
    response = client.put(f'/{post.id}', json={
        'title': new_title
    }, headers = {
        'Authorization': f'Bearer {access_token}'  
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['msg'] == 'you do not have permission for this action'

# ---------------------------------------------------------------#
## 6.           /id           [put] ##
# ---------------------------------------------------------------#

#correct - change the title
def test_delete(client):
    #create user and token
    user = create_test_user(username='deleteUser', 
        email='delete@gmail.com',
        password='password1')
    
    access_token = create_access_token(identity=user.id)
    
    #create a post
    title = 'original title'
    description = 'original description'
    post = create_post(title=title, description=description, id=user.id)

    response = client.delete(f'/{post.id}', headers = {
        'Authorization': f'Bearer {access_token}'  
    })

    assert response.status_code == 204

#bad request - attempt to update todo that is not linked to the current user
def test_delete_not_owned(client):
    #create user who owns the todo
    todoOwner = create_test_user(username='deleteUser2', 
        email='delete2@gmail.com',
        password='password1')
    
    #create a post for todoOwner
    title = 'original title'
    description = 'original description'
    post = create_post(title=title, description=description, id=todoOwner.id)

    #create a third party
    user = create_test_user(username='deleteUser3', 
        email='delete3@gmail.com',
        password='password1')
    access_token = create_access_token(identity=user.id)

    #request to delete the todo from the third party
    response = client.delete(f'/{post.id}', headers = {
        'Authorization': f'Bearer {access_token}'  
    })

    data = response.get_json()
    assert data['msg'] == "You do not have authorisation for this item"
    assert response.status_code == 401