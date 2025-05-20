from base64 import encodebytes
from io import BytesIO
import uuid
import qrcode
from flask import jsonify, send_file, request
from main import redis
from flask_jwt_extended import create_access_token, get_jwt
from ..utils.redis_list_manager import RedisListManager


def set_rtmp_key():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    rtmp_key = data.get('rtmp_key')
    redis.set(f"{event_id}-rtmp_key", rtmp_key.encode('utf-8'))
    redis.set(f"{event_id}-rtmp_url", "rtmp://a.rtmp.youtube.com/live2")
    return {"rtmp_key": rtmp_key}

def add_new_participant():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    request_role = claims.get('role')
    participant_role = "participant"
    data = request.get_json()
    web_url = data['web_url']
    if request_role == 'creator':
        new_user_id = str(uuid.uuid4())
        redis.set(f"user-{new_user_id}", new_user_id)
        redis.set(f"user-{new_user_id}-role", participant_role)
        redis.set(f"user-{new_user_id}-id_event", event_id)

        new_user_identity = new_user_id
        claims = {"role": participant_role , "event_id": event_id}
        additional_data = {"claims": claims}

        access_token = create_access_token(identity=new_user_identity, additional_claims=additional_data)
        redis.set(f"user-{new_user_id}-token", access_token)


        join_url = web_url + f'/join-event?token={str(access_token)}'
        redis.set(f"user-{new_user_id}-join_url", join_url)

        join_qr_img = qr_generate(join_url)
        redis.set(f"user-{new_user_id}-join_qr_img", join_qr_img)

        event_participants_list_key = f'{event_id}-participants_list'

        RedisListManager(redis).add_to_list(key=event_participants_list_key, value=new_user_id, to_end=True)

        return {"token": access_token, "event_id": event_id, "role": participant_role,
                "user_id": new_user_id, "join_url": join_url, "join_qr_img": join_qr_img}
    
    return {"error": "Este usuario no puede modificar participantes"}


def event_participant(user_id):
    participant_role = redis.get(f"user-{user_id}-role").decode('utf-8')
    event_id = redis.get(f"user-{user_id}-id_event").decode('utf-8')
    access_token = redis.get(f"user-{user_id}-token").decode('utf-8')
    join_url = redis.get(f"user-{user_id}-join_url").decode('utf-8')
    join_qr_img = redis.get(f"user-{user_id}-join_qr_img").decode('utf-8')

    return {"token": access_token, "event_id": event_id, "role": participant_role,
            "user_id": user_id, "join_url": join_url, "join_qr_img": join_qr_img}

def event_participants():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    event_participants_list_key = f'{event_id}-participants_list'
    participants = RedisListManager(redis).get_all(key=event_participants_list_key)
    return {"participants": participants}



def scan_keys(pattern):
    print(pattern)
    cursor = '0'
    keys = []
    while cursor != 0:
        cursor, batch_keys = redis.scan(cursor=cursor, match=pattern)
        keys.extend(batch_keys)
    print(keys)
    return keys

def join_event(participant_user_id):
    access_token = redis.get(f"user-{participant_user_id}-token").decode('utf-8')
    event_id = redis.get(f"user-{participant_user_id}-id_event").decode('utf-8')
    return {"token": access_token, "event_id": event_id}

def get_some_parameter(current_user, parameter):
    try:
        event_id = redis.get(f"user-{current_user}-id_event")
        event_id = event_id.decode('utf-8')
        pattern = f"{event_id}-{parameter}"
        print(pattern)
        result = redis.get(pattern).decode('utf-8')
        print(result)
        return {f"{parameter}": str(result)}
    except Exception as e:
        print(e)
        return {f"{parameter}": "", "error": "error al obtener el parametro"}

def qr_generate(join_url):
    buffer = BytesIO()
    data = str(join_url)
    img = qrcode.make(data)
    img.save(buffer)
    buffer.seek(0)
    send_file(buffer, mimetype='image/png')
    encoded_img_qr = encodebytes(buffer.getvalue()).decode('ascii')
    return encoded_img_qr