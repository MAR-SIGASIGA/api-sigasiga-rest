from flask_jwt_extended import get_jwt_identity
from main import redis


def add_point_team(team, points):
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    team_points = redis.get(f'{event_id}-scoreboard-{team}_points')
    team_points = int(team_points)
    team_points += int(points)
    if team_points < 0 : team_points = 0
    redis.set(f'{event_id}-scoreboard-{team}_points', team_points)
    return{f'{team}_points': team_points}

def sub_point_team(team, points):
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    team_points = redis.get(f'{event_id}-scoreboard-{team}_points')
    team_points = int(team_points)
    team_points -= int(points)
    if team_points < 0 : team_points = 0
    redis.set(f'{event_id}-scoreboard-{team}_points', team_points)
    return{f'{team}_points': team_points}

def set_teams(teams_data):
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    for key in teams_data:
        redis.set(f'{event_id}-scoreboard-{key}', teams_data[key])
    return {"teams_status": "setted"}

def get_scoreboard():
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    sport_id = int(redis.get(f'{event_id}-sport_id'))
    sport_name = sports_name_list[sport_id]
    sport = sports[sport_id]
    scoreboard = sport[sport_name]["scoreboard"]
    # print(scoreboard)
    for attribute in scoreboard:
    #    print(attribute)
       scoreboard[attribute] = redis.get(f'{event_id}-scoreboard-{attribute}').decode("utf-8")
    return scoreboard

def set_time(ms_time):
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    redis.set(f'{event_id}-scoreboard-time', int(ms_time))
    return {"time": "setted"}

def set_time24(ms_time):
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    redis.set(f'{event_id}-scoreboard-24time', int(ms_time))
    return {"time24": "setted"}

def change_play_pause_time():
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    timer_status = int(redis.get(f'{event_id}-scoreboard-play_time'))
    print(timer_status)
    if timer_status: 
        redis.set(f'{event_id}-scoreboard-play_time', int(False))
    else: 
        redis.set(f'{event_id}-scoreboard-play_time', int(True))
    return {"timer_status" : int(redis.get(f'{event_id}-scoreboard-play_time'))}

def change_play_pause_time24():
    current_user = get_jwt_identity()
    key = f"user-{current_user}-id_event"
    event_id = (redis.get(key)).decode('utf-8')
    timer_status = int(redis.get(f'{event_id}-scoreboard-play_24time'))
    print(timer_status)
    if timer_status: 
        redis.set(f'{event_id}-scoreboard-play_24time', int(False))
    else: 
        redis.set(f'{event_id}-scoreboard-play_24time', int(True))
    return {"timer24_status" : int(redis.get(f'{event_id}-scoreboard-play_24time'))}