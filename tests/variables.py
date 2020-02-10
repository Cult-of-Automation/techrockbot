import logging
import yaml

log = logging.getLogger(__name__)

with open('configs/default.yml', encoding='UTF-8') as f:
    _DEFAULT_YAML = yaml.safe_load(f)

# Context Manager for updating guild config
class GuildConfig:

    def __init__(self, gid):
        self.gid = gid

    def __enter__(self):
        self.f = open(f'configs/{self.gid}.yml', 'r+')
        self.guildconfig = yaml.safe_load(self.f)
        return self.guildconfig

    def __exit__(self, exception_type, exception_value, traceback):
        self.f.seek(0)
        yaml.dump(self.guildconfig, self.f, default_flow_style=False, indent=4)
        self.f.truncate()

# Read-only function for retrieving guild configs
def _get(gid, key, subkey=None):
    with open(f'configs/{gid}.yml', encoding='UTF-8') as f:
        _GUILD_YAML = yaml.safe_load(f)
    try:
        if subkey is not None:
            return _GUILD_YAML[key][subkey]
        return _GUILD_YAML[key]
    except KeyError:
        dotted_path = '.'.join(
            (str(gid), key, subkey)
            if subkey is not None else (str(gid), key)
        )
        log.critical(f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found.")
        raise

def _prefix(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('trb ')
    else:
        base.append(_get(msg.guild.id, 'prefix'))
    return base