from flask_restful import abort
from data import db_session

def abort_if_thing_not_found(thing_id, thing):
    session = db_session.create_session()
    things = session.query(thing).get(thing_id)
    if not things:
        abort(404, message=f"{thing.type} под номером {thing_id} не был найден")