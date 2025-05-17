from main import redis
import shortuuid
from datetime import datetime
import main.modules.remove_redis_data as remove_redis_data
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, decode_token
import uuid
from ..models.sport import Sport
from ..utils.redis_list_manager import RedisListManager
import json

def new_event_service(sport_id):

    sport_dict = Sport.get_sport_by_id(sport_id)
    if not sport_dict:
        return {"error": "Sport not found"}, 404

    user_id = str(uuid.uuid4())
    user_role = "creator"
    sport_id = sport_dict.get("id")
    sport_name = sport_dict.get("name")
    sport_slug = sport_dict.get("slug")
    sport_scoreboard = sport_dict.get("scoreboard")
    event_id = str(shortuuid.uuid())

    redis.set(f"{event_id}-user-{user_id}", user_id.encode('utf-8'))
    redis.set(f"{event_id}-user-{user_id}-role", user_role.encode('utf-8'))
    redis.set(f"{event_id}-user-{user_id}-id_event", event_id.encode('utf-8'))

    redis.set(f'{event_id}-event_id', event_id.encode('utf-8'))
    redis.set(f'{event_id}-sport_name', sport_name.encode('utf-8'))
    redis.set(f'{event_id}-sport_slug', sport_slug.encode('utf-8'))
    redis.set(f'{event_id}-sport_id', sport_id)
    redis.set(f'{event_id}-creator_user_id', user_id.encode('utf-8'))
    redis.set(f'{event_id}-scoreboard', json.dumps(sport_scoreboard).encode('utf-8'))
    redis.set(f"{event_id}-selected_source", "default".encode('utf-8'))
    claims = {"role": user_role , "event_id": event_id}
    additional_data = {"claims": claims}

    access_token = create_access_token(identity=str(user_id), additional_claims=additional_data)

    redis.set(f"{event_id}-user-{user_id}-token", access_token.encode('utf-8'))

    event_video_source_list_key = f'{event_id}-video_sources_list'

    RedisListManager(redis).add_to_list(key=event_video_source_list_key, value="default", to_end=True)

    # Key to start EventManager process related to this event
    redis.lpush('start_event', event_id)
    # channel = f"{event_id}-event_manager"
    # event_manager_msg = {"action": "new_client", "data": {"client_id": "morsi"}}
    # redis.publish(channel, json.dumps(event_manager_msg).encode('utf-8'))
    return {"token": access_token, "event_id": event_id}

def validate_ws_client():
    current_user = get_jwt_identity()
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    request_data = request.get_json()
    ws_id = request_data.get('ws_id')
    if not ws_id:
        return {"error": "ws_id is required"}, 400
    redis.publish(f"{event_id}-event_manager", json.dumps({"action": "new_client", "data": {"client_id": ws_id}}).encode('utf-8'))
    add_video_source(event_id, ws_id)
    return {"ws_id": ws_id, "event_id": event_id}

def start_event_manager(event_id):
    redis.lpush('start_event', event_id)

def play_event(event_id):
    value = int(True)
    redis.set(f'{event_id}-play', value)
    return "done"

def pause_event(event_id):
    value = int(False)
    redis.set(f'{event_id}-play', value)
    return "done"

#cambio stop a True, matara al streaming
def stop_event():
    current_user = get_jwt_identity()
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    channel = f"{event_id}-event_manager"
    redis.publish(channel, json.dumps({"action": "stop_event"}).encode('utf-8'))
    # remove_redis_data.delete_event(event_id, current_user)
    return {f'{event_id} Status': "Stopped and removed"}

#Implementar logica para comenzar stream
def start_event():
    pass

def get_sports_list():
    from ..models.sport import Sport
    sports_list = Sport.get_sports_list()
    return jsonify({"sports": sports_list})

def change_socket_video_source(video_name):
    pass

def start_youtube_streaming():
    pass
def stop_youtube_streaming():
    pass

def video_source_list():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    print(claims)
    print(event_id)
    video_source_list_key = f'{event_id}-video_sources_list'
    video_source_list = RedisListManager(redis).get_all(video_source_list_key)
    if video_source_list:
        return video_source_list
    else:
        video_source_list = []

def add_video_source(event_id, video_source_name):
    if not video_source_name:
        return {"error": "video_source_name is required"}, 400
    video_source_list_key = f'{event_id}-video_sources_list'
    RedisListManager(redis).add_to_list(key=video_source_list_key, value=video_source_name, to_end=True)
    return {"message": "Video source added successfully"}

def video_source_select():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    print(data)
    video_source_name = data.get('video_source_name')
    if not video_source_name:
        return {"error": "video_source_name is required"}, 400

    video_source_list = RedisListManager(redis).get_all(f'{event_id}-video_sources_list')
    if video_source_name not in video_source_list:
        return {"error": "video source not found"}, 404
    name_selected_source_key = f"{event_id}-selected_source"
    redis.set(name_selected_source_key, video_source_name.encode('utf-8'))
    return {"message": "Video source selected successfully", "video_source_name": video_source_name}

def video_source_remove():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    video_source_name = data.get('video_source_name')

    if video_source_name == "default":
        return {"error": "Cannot remove default video source"}, 400

    if not video_source_name:
        return {"error": "video_source_name is required"}, 400



    video_source_list_key = f'{event_id}-video_sources_list'
    status = RedisListManager(redis).remove_value(key=video_source_list_key, value=video_source_name)
    name_selected_source_key = f"{event_id}-selected_source"
    selected_source_name = redis.get(name_selected_source_key).decode('utf-8')
    if selected_source_name == video_source_name:
        video_source_list_key = f'{event_id}-video_sources_list'
        video_source_list = RedisListManager(redis).get_all(video_source_list_key)
        new_selected_source = video_source_list[-1] if video_source_list  else "default"
        redis.set(name_selected_source_key, new_selected_source.encode('utf-8'))

    redis.set(f"{event_id}-video_source-{video_source_name}-process_alive", int(False))
    redis.delete(f"{event_id}-video_source-{video_source_name}")
    redis.delete(f"{event_id}-video_source_thumbnail-{video_source_name}")
    if status:
        return {"message": "Video source removed successfully"}, 200
    else:
        return {"error": "Video source not found"}, 404

