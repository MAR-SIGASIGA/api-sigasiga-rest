from main import redis
import shortuuid
from datetime import datetime
from ..utils.remove_redis_data import delete_event_redis
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, decode_token
import uuid
from ..models.sport import Sport
from ..utils.redis_list_manager import RedisListManager
import json
from ..utils.sio_pubsub_redis import publish_to_redis

def new_event_service(sport_id):
    try:
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
        redis.set(f"{event_id}-rtmp_url", "rtmp://a.rtmp.youtube.com/live2/".encode('utf-8'))
        redis.set(f"{event_id}-rtmp_key", "".encode('utf-8'))
        redis.set(f"{event_id}-rtmp_status", int(False))

        claims = {"role": user_role , "event_id": event_id}
        additional_data = {"claims": claims}

        access_token = create_access_token(identity=user_id, additional_claims=additional_data)

        redis.set(f"{event_id}-user-{user_id}-token", access_token.encode('utf-8'))

        event_video_source_list_key = f'{event_id}-video_sources_list'

        RedisListManager(redis).add_to_list(key=event_video_source_list_key, value="default", to_end=True)

        # Key to start EventManager process related to this event
        redis.lpush('start_event', event_id)
        json_response = {
            "token": access_token,
            "event_id": event_id
        }
        return json_response, 200

    except Exception as e:
        return {"error starting new event": str(e)}, 500

def validate_ws_client():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        request_data = request.get_json()
        ws_id = request_data.get('ws_id')
        if not ws_id:
            return {"error": "ws_id is required"}, 400
        redis.publish(f"{event_id}-event_manager", json.dumps({"action": "new_client", "data": {"client_id": ws_id}}).encode('utf-8'))
        add_video_source(event_id, ws_id)
        json_response = {
            "ws_id": ws_id,
            "event_id": event_id
        }
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500

def add_video_source(event_id, video_source_name):
    try:
        if not video_source_name:
            return {"error": "video_source_name is required"}, 400
        video_source_list_key = f'{event_id}-video_sources_list'
        RedisListManager(redis).add_to_list(key=video_source_list_key, value=video_source_name, to_end=True)
        return {"message": "Video source added successfully"}
    except Exception as e:
        return {"error": str(e)}, 500
    
def start_event_manager(event_id):
    redis.lpush('start_event', event_id)
    json_response = {
        "message": "Event manager started successfully"
    }
    return json_response, 200

def stop_event():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        channel = f"{event_id}-event_manager"
        redis.publish(channel, json.dumps({"action": "stop_event"}).encode('utf-8'))
        delete_event_redis(event_id)
        json_response = {
            f'{event_id} Status': "Stopped and removed"
        }
        publish_to_redis(event_id=event_id, 
                         event_type="config_room-stop_event", 
                         data_dict=json_response)
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500

def sports_list():
    from ..models.sport import Sport
    sports_list = Sport.get_sports_list()
    json_response = {
        "sports": sports_list
    }
    return json_response, 200

def start_rtmp_streaming():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        rtmp_url = redis.get(f"{event_id}-rtmp_url").decode('utf-8')
        rtmp_key = redis.get(f"{event_id}-rtmp_key").decode('utf-8')
        if not rtmp_url or not rtmp_key:
            return {"error": "RTMP URL or RTMP Key not found"}, 400
        redis.publish(f"{event_id}-event_manager", json.dumps({"action": "start_rtmp_emitter"}).encode('utf-8'))
        redis.set(f"{event_id}-rtmp_status", int(True))

        json_response = {
            "message": "RTMP streaming started",
            "status": True
        }
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def stop_rtmp_streaming():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        redis.set(f"{event_id}-rtmp_status", int(False))
        json_response = {
            "message": "RTMP streaming stopped",
            "status": False
        }
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def toogle_rtmp_status():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        current_status = int(redis.get(f"{event_id}-rtmp_status"))
        status = not current_status
        redis.set(f"{event_id}-rtmp_status", int(status))
        if status:
            rtmp_url = redis.get(f"{event_id}-rtmp_url").decode('utf-8')
            rtmp_key = redis.get(f"{event_id}-rtmp_key").decode('utf-8')
            if not rtmp_url or not rtmp_key:
                return {"error": "RTMP URL or RTMP Key not found"}, 400
            # Start RTMP streaming on EventManager
            redis.publish(f"{event_id}-event_manager", json.dumps({"action": "start_rtmp_emitter"}).encode('utf-8'))
            json_response = {
                "message": "RTMP streaming started",
                "status": True
            }       
        else:
            # Stop RTMP streaming on EventManager, if status is False, RTMP process auto stop
            json_response = {
                "message": "RTMP streaming stopped",
                "status": False
            }

        publish_to_redis(event_id=event_id, 
                         event_type="config_room-rtmp_status", 
                         data_dict=json_response)
        
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def video_source_list():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    video_source_list_key = f'{event_id}-video_sources_list'
    video_source_list = RedisListManager(redis).get_all(video_source_list_key)
    json_response = {
        "video_source_list": video_source_list if video_source_list else []
    }
    return json_response, 200

def video_source_select():
    try:
        claims = get_jwt().get('claims')
        event_id = claims.get('event_id')
        data = request.get_json()
        video_source_name = data.get('video_source_name')
        if not video_source_name:
            return {"error": "video_source_name is required"}, 400

        video_source_list = RedisListManager(redis).get_all(f'{event_id}-video_sources_list')
        if video_source_name not in video_source_list:
            return {"error": "video source not found"}, 404
        name_selected_source_key = f"{event_id}-selected_source"
        redis.set(name_selected_source_key, video_source_name.encode('utf-8'))
        json_response = {
            "message": "Video source selected successfully",
            "video_source_name": video_source_name
        }
        return json_response, 200
    except Exception as e:
        return {"error": str(e)}, 500

def video_source_remove():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    video_source_name = data.get('video_source_name')

    if video_source_name == "default":
        json_response = {
            "error": "Cannot remove default video source"
        }
        return json_response, 400

    if not video_source_name:
        json_response = {
            "error": "video_source_name is required"
        }
        return json_response, 400


    try:
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
            json_response = {
                "message": "Video source removed successfully"
            }
            return json_response, 200
        else:
            json_response = {
                "error": "Video source not found"
            }
            return json_response, 404
    except Exception as e:
        return {"error": str(e)}, 500

