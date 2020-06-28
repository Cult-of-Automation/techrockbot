import logging
import yaml
import os

log = logging.getLogger(__name__)

CFPATH = 'configs/'

class GuildConfig:
    """
    Container for guild configuration dictionary saved to yaml
    Instances are stored within the class and accessable through
    the get_config() class method.
    First level yaml entries can be accessed as instance attributes
    Example usage:
        guild_id = ctx.guild.id
        guild_config = GuildConfig.get_config(guild.id)
        if guild_config.cooldown['memes']['enabled']:
            guild_config.cooldown['memes'] = new_settings
    """

    location = CFPATH
    library = {}

    def __init__(self, file_name):
        self.file_name = file_name
        self.full_path = self.location + self.file_name
        self.id, self.file_type = file_name.split('.')
        self.storage = self.load_yaml()
        self.add_to_library(self.id, self)

    @property
    def has_been_modified(self):
        return self.storage != self.load_yaml()

    def load_yaml(self):
        try:
            with open(self.full_path, 'r', encoding='UTF-8') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError: # Load default configuration file
            default_config = self.get_config('default')
            config = default_config.storage
        finally:
            return config

    def save_yaml(self):
        if self.has_been_modified:
            log.info(f'Saving {self} to disk')
            with open(self.full_path, 'w', encoding='UTF-8') as f:
                yaml.dump(self.storage, f, default_flow_style=False, indent=4)
                f.truncate()

    def __getattr__(self, name):
        try:
            value = self.storage[name]
        except KeyError:
            value = None
            log.critical(f"Tried accessing configuration variable at `{self.id}.{name}`, but it could not be found.")
            raise
        finally:
            return value

    def __str__(self):
        return f'{self.id} Guild Configuration'

    def __repr__(self):
        return f'GuildConfig("{self.file_name}")'

    @classmethod
    def add_to_library(cls, id, instance):
        cls.library.update({id: instance})

    @classmethod
    def get_config(cls, id):
        return cls.library.get(str(id), None)

    @classmethod
    def save_all(cls):
        log.info('Saving all configs to disk')
        for config in cls.library.values():
            config.save_yaml()

    @classmethod
    def initialize_guild(cls, guild_id):
        return cls(f'{guild_id}.yml')


log.info('Loading guild configurations...')
for config_file in os.listdir(CFPATH):
    GuildConfig(config_file)

def _get(guild_id, *keys):
    guild_config = GuildConfig.get_config(guild_id)
    value = guild_config.storage
    for key in keys:
        value = value[key]
    return value

def _prefix(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('trb ')
    else:
        guild_id = msg.guild.id
        guild_config = GuildConfig.get_config(guild_id)
        base.append(guild_config.prefix)
    return base