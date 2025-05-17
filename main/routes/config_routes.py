from flask import Blueprint
from flask import render_template
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.services.config_services import  (set_yt_rtmp_key,
                                            add_new_participant, get_event_participants,
                                            join_event, get_some_parameter, get_event_participant)

config_bp = Blueprint('config', __name__, url_prefix='/config')

@config_bp.route('/set_yt_rtmp_key', methods=['POST'])
@jwt_required(optional=True)
def set_yt_rtmp_key_event():
    data = request.get_json()
    youtube_rtmp_key = data['youtube_rtmp_key']
    return set_yt_rtmp_key(youtube_rtmp_key)

@config_bp.route('/add_new_participant', methods=['POST'])
@jwt_required(optional=True)
def add_new_participant_event():
    data = request.get_json()
    web_url = data['web_url']
    current_user = get_jwt_identity()
    return add_new_participant(current_user, web_url)

@config_bp.route('/get_participant_list', methods=['GET'])
@jwt_required(optional=True)
def get_event_participants_event():
    # data = request.get_json()
    current_user = get_jwt_identity()
    return get_event_participants(current_user)

@config_bp.route('/get_participant/<user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_event_participant_event(user_id):
    # data = request.get_json()
    return get_event_participant(user_id)

@config_bp.route('/join_event/<user_id>', methods=['POST'])
def join_eventevent(user_id):
    return join_event(user_id)

@config_bp.route('/get_parameter/<parameter>', methods=['GET'])
@jwt_required(optional=True)
def get_some_parameter_event(parameter):
    current_user = get_jwt_identity()
    return get_some_parameter(current_user, parameter)