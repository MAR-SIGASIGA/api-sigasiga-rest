from main import redis

def delete_event(event_id, user_id):

    delete__participants(event_id)
    
    pattern = f'{event_id}*'
    keys_to_delete = redis.keys(pattern)
    if keys_to_delete:
        redis.delete(*keys_to_delete)
        print(f"Se han eliminado {len(keys_to_delete)} claves que coinciden con el patrón '{pattern}'.")
    else:
        print(f"No se encontraron claves que coincidan con el patrón '{pattern}'.")
    
    pattern = f'user-{user_id}*'
    keys_to_delete = redis.keys(pattern)
    if keys_to_delete:
        redis.delete(*keys_to_delete)
        print(f"Se han eliminado {len(keys_to_delete)} claves que coinciden con el patrón '{pattern}'.")
    else:
        print(f"No se encontraron claves que coincidan con el patrón '{pattern}'.")
    
def delete__participants(event_id):
    pattern = f"{event_id}-participant-*"
    keys_to_delete = redis.keys(pattern)
    print("borrar participantes")
    print(keys_to_delete)
    for key in keys_to_delete:
        key = key.decode('utf-8')
        print("key ", key)
        user_id = redis.get(key).decode('utf-8')
        sub_pattern = f"user-{user_id}*" 
        sub_keys_to_delete = redis.keys(sub_pattern)
        if sub_keys_to_delete:
            redis.delete(*sub_keys_to_delete)
            print(f"Se han eliminado {len(sub_keys_to_delete)} claves que coinciden con el patrón '{pattern}'.")
        else:
            print(f"No se encontraron claves que coincidan con el patrón '{pattern}'.")

