from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import request, jsonify
from main import redis

    #     default_keys = {
    #         f"{self.event_id}-scoreboard-local_team": "BOCA",
    #         f"{self.event_id}-scoreboard-visitor_team": "RIVER",
    #         f"{self.event_id}-scoreboard-local_points": 0,
    #         f"{self.event_id}-scoreboard-visitor_points": 0,
    #         f"{self.event_id}-scoreboard-period": 1,
    #         f"{self.event_id}-scoreboard-timer": 10 * 60 * 1000,
    #         f"{self.event_id}-scoreboard-timer_status": 0,
    #         f"{self.event_id}-scoreboard-24_timer": 24 * 1000,
    #         f"{self.event_id}-scoreboard-24_timer_status": 0,
    # }

def modify_points():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    request_data = request.get_json()
    team = request_data.get('team')
    points = request_data.get('points')
    try:
        current_points = redis.get(f'{event_id}-scoreboard-{team}_points')
        current_points = int(current_points)
        current_points += int(points)
        current_points = max(current_points, 0)
        redis.set(f'{event_id}-scoreboard-{team}_points', current_points)
        return{f'{team}_points': current_points}
    except Exception as e:
        return {"error": str(e)}, 500
    
def set_team():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    try:
        team = data.get('team')
        if team in ['local', 'visitor']:
            team_name = data.get('team_name')
            redis.set(f'{event_id}-scoreboard-{team}_team', team_name.encode('utf-8'))
            return {"team_status": "setted"}
        else:
            return {"error": "Invalid team"}, 400
    except Exception as e:
        return {"error": str(e)}, 500

def set_teams():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        teams_data = request.get_json()
        for key in teams_data:
            redis.set(f'{event_id}-scoreboard-{key}', teams_data[key])
        return {"teams_status": "setted"}
    except Exception as e:
        return {"error": str(e)}, 500


def set_time(ms_time):
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    redis.set(f'{event_id}-scoreboard-timer', int(ms_time))
    return {"time": "setted"}

def set_time24(ms_time):
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    redis.set(f'{event_id}-scoreboard-24time', int(ms_time))
    return {"time24": "setted"}

def toogle_timer_status():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    timer_status = int(redis.get(f'{event_id}-scoreboard-timer_status'))
    if timer_status: 
        redis.set(f'{event_id}-scoreboard-timer_status', int(False))
    else: 
        redis.set(f'{event_id}-scoreboard-timer_status', int(True))
    return {"timer_status" : int(redis.get(f'{event_id}-scoreboard-timer_status'))}

def toogle_timer24_status():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    timer_status = int(redis.get(f'{event_id}-scoreboard-24_timer_status'))
    if timer_status: 
        redis.set(f'{event_id}-scoreboard-24_timer_status', int(False))
    else: 
        redis.set(f'{event_id}-scoreboard-24_timer_status', int(True))
    return {"timer24_status" : int(redis.get(f'{event_id}-scoreboard-24_timer_status'))}