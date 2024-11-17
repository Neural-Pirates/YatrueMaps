import redis


class RedisServer:
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379, db=0)

    def add_blacklist(self, token):
        self.r.sadd("blacklist", token)

    def check_blacklist(self, token):
        return self.r.sismember("blacklist", token)


r_server = RedisServer()
