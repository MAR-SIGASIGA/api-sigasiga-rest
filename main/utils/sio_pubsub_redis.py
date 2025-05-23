from main import redis
import pickle

def publish_to_redis(event_id, event_type, data_dict):
    channel = "socket_io_data"
    final_dict = {
    "event_id": event_id,
    "event_type": event_type,
    "data": data_dict
    }
    redis.publish(channel, pickle.dumps(final_dict))