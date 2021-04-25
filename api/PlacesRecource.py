from data import db_session
from data.Places import Places
from flask_restful import Resource, reqparse
from flask import jsonify
from api.aborts import abort_if_thing_not_found

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('adress', required=False)
parser.add_argument('user_id', required=True, type=int)

class PlaceResource(Resource):
    def get(self, place_id, secret_key):
        if secret_key == 'geeks_are_cool':
            abort_if_thing_not_found(place_id, Places)
            session = db_session.create_session()
            place = session.query(Places).get(place_id)
            return jsonify({'place': place.to_dict(
                only=('name', 'content', 'adress', 'user_id', 'photo'))})

    def delete(self, place_id, secret_key):
        if secret_key == 'geeks_are_cool':
            abort_if_thing_not_found(place_id, Places)
            session = db_session.create_session()
            place = session.query(Places).get(place_id)
            session.delete(place)
            session.commit()
            return jsonify({'success': 'OK'})

class PlacesListResource(Resource):
    def get(self, secret_key):
        if secret_key == 'geeks_are_cool':
            session = db_session.create_session()
            places = session.query(Places).all()
            return jsonify({'places': [item.to_dict(
                only=('name', 'content', 'adress', 'user.name', 'created_date')) for item in places]})

    def post(self, secret_key):
        if secret_key == 'geeks_are_cool':
            args = parser.parse_args()
            session = db_session.create_session()
            place = Places(
                name=args['name'],
                content=args['content'],
                user_id=args['user_id'],
                photo='none',
                adress=args['adress'],
                type='place'
            )
            session.add(place)
            session.commit()
            return jsonify({'success': 'OK'})