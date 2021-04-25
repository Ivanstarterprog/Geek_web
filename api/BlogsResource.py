from data import db_session
from data.blogs import Blogs
from flask_restful import Resource, reqparse
from flask import jsonify
from api.aborts import abort_if_thing_not_found

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('previue', required=False)
parser.add_argument('user_id', required=True, type=int)

class BlogResource(Resource):
    def get(self, blog_id, secret_key):
        if secret_key == 'geeks_are_cool':
            abort_if_thing_not_found(blog_id, Blogs)
            session = db_session.create_session()
            blog = session.query(Blogs).get(blog_id)
            return jsonify({'blog': blog.to_dict(
                only=('title', 'content', 'previue', 'user_id', 'photo'))})

    def delete(self, blog_id, secret_key):
        if secret_key == 'geeks_are_cool':
            abort_if_thing_not_found(blog_id, Blogs)
            session = db_session.create_session()
            blog = session.query(Blogs).get(blog_id)
            session.delete(blog)
            session.commit()
            return jsonify({'success': 'OK'})

class BlogsListResource(Resource):
    def get(self, secret_key):
        if secret_key == 'geeks_are_cool':
            session = db_session.create_session()
            blogs = session.query(Blogs).all()
            return jsonify({'blogs': [item.to_dict(
                only=('title', 'content', 'previue', 'user_id', 'photo')) for item in blogs]})

    def post(self, secret_key):
        if secret_key == 'geeks_are_cool':
            args = parser.parse_args()
            session = db_session.create_session()
            blog = Blogs(
                title=args['title'],
                content=args['content'],
                user_id=args['user_id'],
                photo='none',
                previue=args['previue'],
                type='blog'
            )
            session.add(blog)
            session.commit()
            return jsonify({'success': 'OK'})