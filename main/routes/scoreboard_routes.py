from flask import Blueprint
from flask import render_template
from flask_jwt_extended import jwt_required
from main.services.scoreboard_services import add_point_team, change_play_pause_time24, set_time24, sub_point_team, set_teams, get_scoreboard, set_time, change_play_pause_time
from flask import request

scoreboard_bp = Blueprint('scoreboard', __name__, url_prefix='/scoreboard')

@scoreboard_bp.route('/add_point/<team>/<points>', methods=['POST'])
@jwt_required(optional=True)
def add_points_event(team, points):
    return add_point_team(team, points)
      

@scoreboard_bp.route('/sub_point/<team>/<points>', methods=['POST'])
@jwt_required(optional=True)
def sub_points_event(team, points):
    return sub_point_team(team, points)

@scoreboard_bp.route('/set_teams', methods=['POST'])
@jwt_required(optional=True)
def set_teams_event():
    data = request.get_json()
    return set_teams(data)


@scoreboard_bp.route('/set_time/<ms_time>', methods=['POST'])
@jwt_required(optional=True)
def set_time_event(ms_time):
    return set_time(ms_time)

@scoreboard_bp.route('/set_time24/<ms_time>', methods=['POST'])
@jwt_required(optional=True)
def set_time24_event(ms_time):
    return set_time24(ms_time)

@scoreboard_bp.route('/change_play_pause_time', methods=['POST'])
@jwt_required(optional=True)
def change_play_pause_time_event():
    return change_play_pause_time()

@scoreboard_bp.route('/change_play_pause_time24', methods=['POST'])
@jwt_required(optional=True)
def change_play_pause_time24_event():
    return change_play_pause_time24()

@scoreboard_bp.route('/get', methods=['GET'])
@jwt_required(optional=True)
def get_scoreboard_event():
    return get_scoreboard()