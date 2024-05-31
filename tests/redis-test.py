from redis import Redis

redis = Redis('172.20.0.252')

test = redis.get('test')

print(test)