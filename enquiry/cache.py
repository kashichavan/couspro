from django.core.cache import cache

def get_or_set_cache(key, fetch_function, timeout=600):
    data = cache.get(key)
    if data is None:
        print(f"[Cache MISS] {key}")
        data = fetch_function()
        cache.set(key, data, timeout)
    else:
        print(f"[Cache HIT] {key}")
    return data
