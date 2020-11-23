from app.api import api
from flask import jsonify, request
from app.models import User, Post, Like
from flask_jwt_extended import (
    create_access_token, create_refresh_token, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
)


@api.route('/', methods=['GET'])
def home():
    return jsonify({'msg': 'Hello world'})


@api.route('/signup', methods=['POST'])
def signup_user():
    User.signup(request.json)
    return jsonify({'mas': 'Created'})


@api.route('/login', methods=['POST'])
def login():
    user = User.login(request.json)
    if user:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp
    return jsonify({'msg': 'Sms wrong'})


@api.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@api.route('/users', methods=['GET'])
@jwt_required
def users_page():
    return jsonify({'msg': 'users page', 'items': User.get_objects_list(**request.args)})


@api.route('/users/', methods=['POST'])
@jwt_required
def create_user():
    user = User(**request.json)
    return jsonify({'msg': f'User created with id: {user.id}'})


@api.route('/profile', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def user_page():
    user_id = get_jwt_identity()
    if request.method == 'PUT':
        User.update(user_id, request.json)
        return jsonify({'msg': 'Put method'})
    elif request.method == 'DELETE':
        User.delete(user_id)
        return jsonify({'msg': 'DELETE method'})
    else:
        return jsonify({'items': User.get_object(user_id)})


@api.route('/posts', methods=['GET'])
@jwt_required
def posts_page():
    return jsonify({'msg': 'posts page', 'items': Post.get_objects_list(**request.args)})


@api.route('/posts/', methods=['POST'])
@jwt_required
def create_page():
    user = User.get_object(get_jwt_identity(), to_dict=False)
    user.create_post(**request.json)
    return jsonify({'msg': 'Post created'})


@api.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def post_page(post_id):
    if request.method == 'PUT':
        Post.update(post_id, request.json)
        return jsonify({'msg': 'Put method'})
    elif request.method == 'DELETE':
        Post.delete(post_id)
        return jsonify({'msg': 'DELETE method'})
    else:
        return jsonify({'items': Post.get_object(post_id)})


@api.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required
def like_post(post_id):
    user = User.get_object(get_jwt_identity(), to_dict=False)
    post = Post.get_object(post_id, to_dict=False)
    user.like_post(post)
    return jsonify({"status": "ok"})


@api.route('/posts/<int:post_id>/unlike', methods=['POST'])
@jwt_required
def unlike_post(post_id):
    user = User.get_object(get_jwt_identity(), to_dict=False)
    post = Post.get_object(post_id, to_dict=False)
    user.unlike_post(post)
    return jsonify({"status": "ok"})


@api.route('/posts/<int:post_id>/analitics', methods=['GET'])
@jwt_required
def get_post_analitics(post_id):
    return jsonify({'analitics': Post.get_analytics(post_id, **request.args)})


@api.route('/my-analitics/', methods=['GET'])
@jwt_required
def get_user_analitics():
    user_id = get_jwt_identity()
    return jsonify({'analitics': User.get_analytics(user_id, **request.args)})


@api.route('/analitics/', methods=['GET'])
def get_analitics():
    return jsonify(Like.get_global_analitics(**request.args))