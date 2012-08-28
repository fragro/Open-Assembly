import redis
import settings

def redis_client():
    """Get a redis client."""
    if settings.BROKER_PASSWORD != '':
    	return redis.Redis(settings.BROKER_HOST, settings.BROKER_PORT, settings.BROKER_DB,
                 password=settings.BROKER_PASSWORD, socket_timeout=0.5)
    else:
    	return redis.Redis(settings.BROKER_HOST, settings.BROKER_PORT, settings.BROKER_DB,
             	 socket_timeout=0.5)



