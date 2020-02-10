import discord
import logging
import os
import yaml

from discord.ext import commands
from pathlib import Path

from tests.variables import GuildConfig, _get
from tests.utils.checks import mod_command_check

log = logging.getLogger(__name__)

class Guilds(commands.Cog, name='Guild Configuration'):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return mod_command_check(ctx)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        log.info(f'Joined {guild.name}')
        if Path(f'configs/{guild.id}.yml').exists():
            log.info(f'Config file for {guild.name} found')
            return

        log.info(f'No config for {guild.name} found, creating {guild.id}.yml')
        # Load default config file as template
        with open('configs/default.yml', encoding='utf-8') as f:
            default = yaml.safe_load(f)

        # Build dictionary of role ids in config
        default['roles'] = {role.name.lower():role.id for role in guild.roles}

        # Remove roles from groups if they do not exist
        for group in default['group'].keys():
            for role in default['group'][group]:
                if role not in default['roles'].keys():
                    default['group'][group].remove(role)

        # Create guild config file
        with open(f'configs/{guild.id}.yml', 'w', encoding='utf-8') as f:
            yaml.dump(default, f, default_flow_style=False, indent=4)

    @commands.command(name = 'reset_config')
    async def reset_config(self, ctx):
        """Reset guild configuation to default"""
        if Path(f'configs/{ctx.guild.id}.yml').exists():
            os.remove(f'configs/{ctx.guild.id}.yml')
        await self.on_guild_join(ctx.guild)

    @commands.command(name = 'setprefix')
    async def _set_prefix(self, ctx, prefix: str):
        """Set prefix for TRB"""
        with GuildConfig(ctx.guild.id) as guildconfig:
            guildconfig['prefix'] = prefix
        await ctx.send(f'Set `{prefix}` as the TRB prefix')

    @commands.group(name = 'groups')
    async def groups(self, ctx):
        """List permission groups for TRB commands"""

        if ctx.invoked_subcommand is None:

            groups = _get(ctx.guild.id, 'group')
            mods = groups['mods']
            staff = groups['staff']
            others = []
    
            # Combine groups without duplicates
            unique = set(mods + staff)
            
            for role in ctx.guild.roles:
                if role.name.lower() not in unique:
                    others.append(role.name.lower())
    
            mods_roles = '\n-'.join(mods)
            staff_roles = '\n-'.join(staff)
            others_roles = '\n-'.join(others)
    
            group_list = discord.Embed(title=f'{ctx.guild.name} Role Groups',colour=0x4b4740)
            group_list.add_field(name='Moderators',value=f'-{mods_roles}')
            group_list.add_field(name='Staff',value=f'-{staff_roles}')
            group_list.add_field(name='Others',value=f'-{others_roles}')
            await ctx.send(embed=group_list)

    @groups.command(name = 'add')
    async def groups_add(self, ctx, role, group=None):
        """Add a role to a group"""

        # Check if role exists
        roleid = None
        for r in ctx.guild.roles:
            if role==r.name:
                roleid = r.id
                break
        if roleid==None:
            await ctx.send(f'`{role}` role for {ctx.guild.name} cannot be found')
            return

        role = role.lower()
        group = group.lower() if group is not None else None

        with GuildConfig(ctx.guild.id) as guildconfig:
            # Add roleid to guild config dictionary if not already
            if role not in guildconfig['roles']:
                guildconfig['roles'].update({role: roleid})
            if group is None:
                return
            if role in guildconfig['group'][group]:
                await ctx.send(f'`{role}` role is already in {group}')
                return
            guildconfig['group'][group].append(role)
        await ctx.send(f'Added `{role}` role as {group}')

    @groups.command(name = 'remove_role')
    async def groups_remove(self, ctx, role, group):
        """Remove a role from a group"""
        role = role.lower()
        group = group.lower()
        with GuildConfig(ctx.guild.id) as guildconfig:
            if role not in guildconfig['group'][group]:
                await ctx.send(f'`{role}` role is not in {group}')
                return
            if role=='admin':
                await ctx.send(f'Cannot remove Admin role')
                return
            guildconfig['group'][group].remove(role)
        await ctx.send(f'Removed `{role}` role as {group}')

def setup(bot):
    bot.add_cog(Guilds(bot))