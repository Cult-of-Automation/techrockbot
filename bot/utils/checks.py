import logging

from discord.ext.commands import Cog, Command, Context
from bot.constants import Bot as BotConfig
from bot.variables import _get

log = logging.getLogger(__name__)

def home_discord_check(ctx: Context) -> bool:
    return BotConfig.home_discord == ctx.guild.id

def staff_command_check(ctx: Context) -> bool:
    # Supress logging on help check
    help_check = ctx.command.name == 'help'

    if not ctx.guild:  # Return False in a DM
        if not help_check:
            log.info(f"{ctx.author} tried to use the '{ctx.command.name}'command from a DM. "
                      "This command is restricted by the staff_command decorator. Rejecting request.")
        return False

    # Is owner
    if ctx.author==ctx.guild.owner:
        return True

    # Get guild configured staff roles
    staff_roles = []
    for role in _get(ctx.guild.id, 'group', 'staff'):
        staff_roles.append(_get(ctx.guild.id, 'roles', role))

    for role in ctx.author.roles:
        if role.id in staff_roles:
            if not help_check:
                log.info(f"'{ctx.guild.name}' '{role.name}' {ctx.author} passes check for '{ctx.command.name}'.")
            return True

    if not help_check:
        log.info(f"{ctx.author} does not have the required role to use "
                f"the '{ctx.command.name}' command, so the request is rejected.")
    return False

def mod_command_check(ctx: Context) -> bool:
    # Supress logging on help check
    help_check = ctx.command.name == 'help'
    if not ctx.guild:  # Return False in a DM
        if not help_check:
            log.info(f"{ctx.author} tried to use the '{ctx.command.name}'command from a DM. "
                      "This command is restricted by the mod_command decorator. Rejecting request.")
        return False

    # Is owner
    if ctx.author==ctx.guild.owner:
        return True

    # Get guild configured staff roles
    mod_roles = []
    for role in _get(ctx.guild.id, 'group', 'mods'):
        mod_roles.append(_get(ctx.guild.id, 'roles', role))

    for role in ctx.author.roles:
        if role.id in mod_roles:
            if not help_check:
                log.info(f"'{ctx.guild.name}' '{role.name}' {ctx.author} passes check for '{ctx.command.name}'.")
            return True

    if not help_check:
        log.info(f"{ctx.author} does not have the required role to use "
                 f"the '{ctx.command.name}' command, so the request is rejected.")
    return False