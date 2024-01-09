
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators 
from src.database import User, db
from datetime import datetime
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token,get_jwt_identity
from src.database import User, db


auth = Blueprint("auth",__name__,url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    
    
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
    
    if len(username) < 3:
        return jsonify({'Message':'Username is too short !!'}), 400
    
    if not username.isalnum() or " " in username :
        return jsonify({'Message':'Username should be Alphanumeric and should carry no spaces !!'}), 400
    
    if User.query.filter_by(username = username).first() is not None: 
        return jsonify({'Message':'Email already exist. Try a different one !! '}) , 409
    
    if len(password) < 6:
        return jsonify({'Message':'Password is too short !! '}), 400

    
    if not validators.email(email):
        return jsonify({'Message':'Email is not valid !!'}) , 400
    if User.query.filter_by(email=email).first() is not None: 
        return jsonify({'Message':'Email already exist. Try a different one !! '}) , 409

    pwd_hash = generate_password_hash(password)
    user = User(username = username, password=pwd_hash, email=email)
    user.updated_at = datetime.now()
    db.session.add(user)
    db.session.commit()
    
        
    return jsonify({
        'Message':'User Created Successfully !!',
        'user':{
            'username':username, 
            'email':email
        }
    }), 201 


@auth.post('/login')
def login():

    email = request.json.get('email','')
    password = request.json.get('password','')

    user = User.query.filter_by(email=email).first()
    
    if user:
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            
            
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)
            
            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,  
                    'username':user.username,
                    'email':user.email
                }
            }), 200
    
    return jsonify({
        'Message':'Invalid Credentials !!'
    })

@auth.get('/me')
@jwt_required() 
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email':user.email
    }), 200
    
    
@auth.post('/token/refresh')
@jwt_required(refresh=True) 
def refresh_users_token():
    identity = get_jwt_identity()  
    access = create_access_token(identity=identity)
    
    return jsonify({
        'access':access
    }), 200