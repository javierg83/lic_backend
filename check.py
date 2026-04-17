import os
import sys
import redis
from collections import Counter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD

def check():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        username=REDIS_USERNAME,
        decode_responses=True
    )
    
    try:
        r.ping()
        print("Connected to Redis")
    except Exception as e:
        print("Could not connect to Redis", e)
        return
        
    info = r.info('memory')
    print("Memory used:", info['used_memory_human'])
    
    keyspaces = r.info('keyspace')
    print("Keyspaces:", keyspaces)
    
    keys = r.keys('*')
    print("Total Keys:", len(keys))
    
    print("Sample keys:")
    for k in keys[:20]:
        print("  -", k)
        
    prefixes = Counter()
    for k in keys:
        prefixes[k.split(':')[0]] += 1
        
    print("\nPrefix frequencies:")
    for prefix, count in prefixes.most_common():
        print(f"  {prefix}: {count}")

if __name__ == "__main__":
    check()
