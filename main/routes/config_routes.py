from flask import Blueprint
from flask import render_template
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.services.config_services import  (set_rtmp_key,
                                            add_new_participant, event_participants,
                                            join_event, event_participant)

config_bp = Blueprint('config', __name__, url_prefix='/config')

@config_bp.route('/set_rtmp_key', methods=['POST'])
@jwt_required(optional=True)
def set_rtmp_key_event():
    return set_rtmp_key()

@config_bp.route('/add_new_participant', methods=['POST'])
@jwt_required(optional=True)
def add_new_participant_event():
    return add_new_participant()

@config_bp.route('/participant_list', methods=['GET'])
@jwt_required(optional=True)
def event_participants_event():
    return event_participants()

@config_bp.route('/participant/<user_id>', methods=['GET'])
@jwt_required(optional=True)
def event_participant_event(user_id):
    return event_participant(user_id)

@config_bp.route('/join_event/<user_id>', methods=['POST'])
def join_event_event(user_id):
    return join_event(user_id)
