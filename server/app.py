#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        all_campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]
        return all_campers, 200
    
    def post(self):
        try: 
            data = request.get_json()
            new_camper = Camper(**data)
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(rules=("-signups",)), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

api.add_resource(Campers, '/campers')

class CampersById(Resource):
    def get(self, id):
        if camper := db.session.get(Camper, id):
            return camper.to_dict(), 200
        return {'error': 'Camper not found'}, 404
    
    def patch(self, id):
        if camper := db.session.get(Camper, id):
            try:
                data = request.get_json()
                for k, v in data.items():
                    setattr(camper, k, v)
                db.session.commit()
                return camper.to_dict(rules=("-signups",)), 200
            except Exception as e:
                db.session.rollback()
                return {'error': ['validation errors']}, 400
                # return {'error': str(e)}, 400
        return {'error': 'Camper not found'}, 404

api.add_resource(CampersById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        all_activities = [activity.to_dict(rules=("-signups",)) for activity in Activity.query.all()]
        return all_activities, 200

api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    def delete(self, id):
        if activity := db.session.get(Activity, id):
            try:
                db.session.delete(activity)
                db.session.commit()
                return {}, 204
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400
        return {'error': 'Activity not found'}, 404

api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_signup = Signup(**data)
            db.session.add(new_signup)
            db.session.commit()
            return new_signup.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': ['validation errors']}, 400
            # return {'error': str(e)}

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
