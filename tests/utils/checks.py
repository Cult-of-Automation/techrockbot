import logging
from typing import Callable

from discord.ext.commands import Cog, Command, Context
from tests.variables import _get

log = logging.getLogger(__name__)

def staff_command_check(ctx: Context) -> bool:
    if not ctx.guild:  # Return False in a DM
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
            log.info(f"'{ctx.guild.name}' '{role.name}' {ctx.author} passes check for '{ctx.command.name}'.")
            return True

    log.info(f"{ctx.author} does not have the required role to use "
              f"the '{ctx.command.name}' command, so the request is rejected.")
    return False

def mod_command_check(ctx: Context) -> bool:
    if not ctx.guild:  # Return False in a DM
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
            log.info(f"'{ctx.guild.name}' '{role.name}' {ctx.author} passes check for '{ctx.command.name}'.")
            return True

    log.info(f"{ctx.author} does not have the required role to use "
              f"the '{ctx.command.name}' command, so the request is rejected.")
    return False