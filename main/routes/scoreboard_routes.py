from flask import Blueprint
from flask import render_template
from flask_jwt_extended import jwt_required
from main.services.scoreboard_services import (set_time24, set_teams, set_time, 
                                               modify_points, set_team, toogle_timer_status,
                                               toogle_timer24_status)
from flask import request

scoreboard_bp = Blueprint('scoreboard', __name__, url_prefix='/scoreboard')

@scoreboard_bp.route('/modify_points', methods=['POST'])
@jwt_required(optional=True)
def modify_points_event():
    return modify_points()

@scoreboard_bp.route('/set_team', methods=['POST'])
@jwt_required(optional=True)
def set_team_event():
    return set_team()

@scoreboard_bp.route('/set_teams', methods=['POST'])
@jwt_required(optional=True)
def set_teams_event():
    return set_teams()

@scoreboard_bp.route('/set_time/<ms_time>', methods=['POST'])
@jwt_required(optional=True)
def set_time_event(ms_time):
    return set_time(ms_time)

@scoreboard_bp.route('/set_time24/<ms_time>', methods=['POST'])
@jwt_required(optional=True)
def set_time24_event(ms_time):
    return set_time24(ms_time)

@scoreboard_bp.route('/toogle_timer_status', methods=['POST'])
@jwt_required(optional=True)
def toogle_timer_status_event():
    return toogle_timer_status()

@scoreboard_bp.route('/toogle_timer24_status', methods=['POST'])
@jwt_required(optional=True)
def toogle_timer24_status_event():
    return toogle_timer24_status()