import logging
import time

from discord.ext.commands import BucketType
from bot.variables import _get

log = logging.getLogger(__name__)

class TriCooldown(object): -> Callable:
    """
    Custom cooldown class which returns a tribool.
    Retrieves the value under the cd_name argument from the guilds YAML
    on initialization. When called with a discord.Message object, context
    will be read to determine the guild ID, increment a counter integer
    and return False until the int equals the set limit where it will return
    a None value. Further calls will return True until counter is reset.

    At every call, the datetime will be summed with a duration value retrieved
    at init. If this value is exceeded by datetime.now() on call, the counter
    will be reset to 0.
    """
    def __init__(self, cd_name):
        self.cd_name = cd_name
        self.storage = {}

    def __call__(self, msg):

        guild_id = msg.guild.id
        guild_config = _get(guild_id, 'cooldown', self.cd_name)

        # Cooldown is disabled
        if guild_config['enabled'] is False:
            return False

        now_int = int(time.time())
        dur_seconds = guild_config['duration'] * 60

        # Get guild storage or initialize
        guild_storage = self.storage.get(guild_id, {})

        key = self.get_bucket_id(msg, guild_config['bucket'])

        # Get bucket status and increment count
        try:
            bucket_stat = guild_storage[key]
        except KeyError:
            # Initialize bucket status
            bucket_stat = {
                'count': 0,
                'reset_time': now_int + dur_seconds
            }
        else:
            if now_int > bucket_stat['reset_time']:
                # Reset count
                bucket_stat['count'] = 0
                bucket_stat['reset_time'] = now_int + dur_seconds
            else:
                bucket_stat['count'] += 1
        finally:
            guild_storage.update({key: bucket_stat})

        self.storage.update({guild_id: guild_storage})

        if guild_config['limit'] == bucket_stat['count']:
            return None
        elif guild_config['limit'] > bucket_stat['count']:
            return False
        else:
            return True

    def get_bucket_id(self, msg, type):
        """Get the bucket id from Discord message"""
        try:
            bucket = getattr(BucketType, type)
        except AttributeError:
            log.error(f'Invalid bucket type in {guild_id}.cooldown.{self.cd_name}')
            raise
        return bucket.get_key(msg)