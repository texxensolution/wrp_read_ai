from rq import Queue
from redis import Redis
import os

class Q:
    redis: Redis = Redis(host=os.getenv('REDIS_HOST'))
    q: Queue = Queue(connection=redis)

    def push(self, callback_func, args):
        job = self.q.enqueue(callback_func, args=args)
        return job