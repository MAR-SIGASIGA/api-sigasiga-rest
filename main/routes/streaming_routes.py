from flask import Blueprint, Response, request, jsonify
from flask import render_template
from main.services.streaming_services import ( new_event_service , start_event_manager,
                                              start_rtmp_streaming, video_source_list,
                                              stop_rtmp_streaming, validate_ws_client,
                                              video_source_remove, video_source_select,
                                              stop_event, get_sports_list, toogle_rtmp_status)

from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt_header, decode_token

streaming_bp = Blueprint('streaming', __name__, url_prefix='/streaming')

@streaming_bp.route('/new_event/<sport_id>', methods=['POST'])
def new_event(sport_id):
    return new_event_service(sport_id)

#Devuelve un diccionario que contiene como clave/valor el indice correspondiente al nombre del deporte en la lista de los deportes disponibles.
@streaming_bp.route('/get_sports', methods=['GET'])
def get_sports():
    data = get_sports_list()
    return data

@streaming_bp.route('/stop_event', methods=['POST'])
@jwt_required(optional=True)
def stop():
    return stop_event()

@streaming_bp.route('/start_rtmp_streaming', methods=['POST'])
@jwt_required(optional=True)
def start_rtmp_streaming_event():
    return start_rtmp_streaming()

@streaming_bp.route('/stop_rtmp_streaming', methods=['POST'])
@jwt_required(optional=True)
def stop_rtmp_streaming_event():
    return stop_rtmp_streaming()

@streaming_bp.route('/toogle_rtmp_status', methods=['POST'])
@jwt_required(optional=True)
def toogle_rtmp_status_event():
    return toogle_rtmp_status()

@streaming_bp.route('/validate_ws_client', methods=['POST'])
@jwt_required(optional=False)
def validate_ws_client_event():
    return validate_ws_client()

@streaming_bp.route('/video_source_list', methods=['GET'])
@jwt_required(optional=False)
def event_video_source_list():
    return video_source_list()

@streaming_bp.route('/video_source_select', methods=['POST'])
@jwt_required(optional=False)
def event_video_source_select():
    return video_source_select()

@streaming_bp.route('/video_source_remove', methods=['POST'])
@jwt_required(optional=False)
def event_video_source_remove():
    return video_source_remove()

@streaming_bp.route('/start_manager/<event_id>', methods=['POST'])
def start_manager(event_id):
    start_event_manager(event_id)
    return {'message': 'Event manager started'}, 200