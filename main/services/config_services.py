from base64 import encodebytes
from io import BytesIO
import uuid
import qrcode
from flask import jsonify, send_file, request, Response
from main import redis
from flask_jwt_extended import create_access_token, get_jwt, decode_token
from ..utils.redis_list_manager import RedisListManager
from ..utils.qr_gen import generate_qr_code

def set_rtmp_key():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    data = request.get_json()
    rtmp_key = data.get('rtmp_key')
    redis.set(f"{event_id}-rtmp_key", rtmp_key.encode('utf-8'))
    redis.set(f"{event_id}-rtmp_url", "rtmp://a.rtmp.youtube.com/live2")
    json_response = {
        "rtmp_key": rtmp_key
    }
    return json_response, 200

def add_new_participant():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    request_role = claims.get('role')
    participant_role = "participant"
    data = request.get_json()
    web_url = data.get('web_url')
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

        bytes_join_qr_img = generate_qr_code(join_url)
        redis.set(f"user-{new_user_id}-join_qr_img_bytes", bytes_join_qr_img)

        event_participants_list_key = f'{event_id}-participants_list'

        RedisListManager(redis).add_to_list(key=event_participants_list_key, value=new_user_id, to_end=True)

        json_response = {
            "token": access_token,
            "event_id": event_id,
            "role": participant_role,
            "user_id": new_user_id,
            "join_url": join_url,
            "join_qr_img": join_qr_img
        }
        return json_response, 200
    
    return {"error": "Este usuario no puede modificar participantes"}, 403


def event_participant(user_id):
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    event_participants_list_key = f'{event_id}-participants_list'
    participants = RedisListManager(redis).get_all(key=event_participants_list_key)
    if user_id not in participants:
        return {"message": "Participante no encontrado para este evento"}, 404
    participant_role = redis.get(f"user-{user_id}-role").decode('utf-8')
    access_token = redis.get(f"user-{user_id}-token").decode('utf-8')
    join_url = redis.get(f"user-{user_id}-join_url").decode('utf-8')
    join_qr_img = redis.get(f"user-{user_id}-join_qr_img").decode('utf-8')

    json_response = {
        "token": access_token,
        "event_id": event_id,
        "role": participant_role,
        "user_id": user_id,
        "join_url": join_url,
        "join_qr_img": join_qr_img
    }

    return json_response, 200

def event_participants():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    event_participants_list_key = f'{event_id}-participants_list'
    participants = RedisListManager(redis).get_all(key=event_participants_list_key)
    participants_list = []
    for participant in participants:
        participant_data = {
            "user_id": participant,
            "join_url": redis.get(f"user-{participant}-join_url").decode('utf-8'),
        }
        participants_list.append(participant_data)
    json_response = {
        "participants": participants_list
    }
    return json_response, 200

def scan_keys(pattern):
    print(pattern)
    cursor = '0'
    keys = []
    while cursor != 0:
        cursor, batch_keys = redis.scan(cursor=cursor, match=pattern)
        keys.extend(batch_keys)
    print(keys)
    return keys

def join_event():
    claims = get_jwt().get('claims')
    event_id = claims.get('event_id')
    participant_user_id = claims.get('user_id')
    event_participants_list_key = f'{event_id}-participants_list'
    event_participants_list = RedisListManager(redis).get_all(key=event_participants_list_key)
    access_token = redis.get(f"user-{participant_user_id}-token").decode('utf-8')
    if participant_user_id in event_participants_list:
        json_response = {
            "token": access_token,
            "event_id": event_id
        }
        return json_response, 200
    else:
        return {"message": "Participante no encontrado para este evento"}, 404

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

def join_qr_img_bytes():
    url_params = request.args
    token = url_params.get('token')
    user_id = url_params.get('user_id')
    try:
        decoded_token = decode_token(token)
    except Exception as e:
        print(e)
        return {"message": "Token invalido"}, 401
    if user_id is None:
        return {"message": "User id is required"}, 400
    claims = decoded_token.get('claims')
    event_id = claims.get('event_id')
    participants_list_key = f"{event_id}-participants_list"
    participants_list = RedisListManager(redis).get_all(key=participants_list_key)
    print(participants_list)
    print(user_id)
    if user_id not in participants_list:
        return {"message": "Participante no encontrado para este evento"}, 404
    img_bytes = redis.get(f"user-{user_id}-join_qr_img_bytes")
    return Response(img_bytes, mimetype='image/png')

def qr_generate(join_url):
    buffer = BytesIO()
    data = str(join_url)
    img = qrcode.make(data)
    img.save(buffer)
    buffer.seek(0)
    send_file(buffer, mimetype='image/png')
    encoded_img_qr = encodebytes(buffer.getvalue()).decode('ascii')
    return encoded_img_qr