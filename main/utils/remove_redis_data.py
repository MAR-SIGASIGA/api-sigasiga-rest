from main import redis
from .redis_list_manager import RedisListManager

def delete_event_redis(event_id):

    participants_list = RedisListManager(redis).get_all(f'{event_id}-participants_list')
    for participant in participants_list:
        pattern = f'user-{participant}*'
        keys_to_delete = redis.keys(pattern)
        if keys_to_delete:
            redis.delete(*keys_to_delete)
            print(f"Se han eliminado {len(keys_to_delete)} claves que coinciden con el patrón '{pattern}'.")
        else:
            print(f"No se encontraron claves que coincidan con el patrón '{pattern}'.")

    pattern = f'{event_id}*'
    keys_to_delete = redis.keys(pattern)
    if keys_to_delete:
        redis.delete(*keys_to_delete)
        print(f"Se han eliminado {len(keys_to_delete)} claves que coinciden con el patrón '{pattern}'.")
    else:
        print(f"No se encontraron claves que coincidan con el patrón '{pattern}'.")


