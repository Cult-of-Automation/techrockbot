import discord
import logging
import os
import yaml

from discord import Embed
from discord.ext import commands
from pathlib import Path

from bot.variables import GuildConfig, _get
from bot.decorators import mod_command, staff_command

log = logging.getLogger(__name__)

class Guilds(commands.Cog, name='Guild Configuration'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        log.info(f'Joined {guild.name}')
        guild_config = GuildConfig.get_config(guild.id)
        if guild_config is None:
            log.info(f'No config file for {guild.name} found')
            guild_config = GuildConfig.initialize_guild(guild.id)
            # Build dictionary of role ids in config
            guild_config.roles = {role.name.lower():role.id for role in guild.roles}
    
            # Remove roles from groups if they do not exist
            for group in guild_config.group.keys():
                for role in guild_config.group[group]:
                    if role not in guild_config.roles.keys():
                        guild_config.group[group].remove(role)

    @commands.command(name = 'reset_config')
    @mod_command()
    async def reset_config(self, ctx):
        """Reset guild configuation to default"""
        if Path(f'configs/{ctx.guild.id}.yml').exists():
            os.remove(f'configs/{ctx.guild.id}.yml')
        await self.on_guild_join(ctx.guild)

    @commands.command(name = 'setprefix')
    @mod_command()
    async def _set_prefix(self, ctx, prefix: str):
        """Set prefix for TRB"""
        guild_config = GuildConfig.get_config(ctx.guild.id)
        guild_config.prefix = prefix
        await ctx.send(f'Set `{prefix}` as the TRB prefix')

    @commands.command(name='toggle')
    @staff_command()
    async def toggle(self, ctx, toggle_name: str, on_off: bool=None):
        """Switch a toggle on/off"""
        guild_config = GuildConfig.get_config(ctx.guild.id)
        try:
            config_toggle = guildconfig.toggle[toggle_name]
        except KeyError:
            response = (
                f'{toggle_name.capitalize()} toggle not found.\n'
                f'Run `toggles` command to view list of toggles'
            )
        else:
            if on_off is None:
                toggle_onoff = 'on' if config_toggle else 'off'
                response = f'{toggle_name.capitalize()} toggle is {toggle_onoff}'
            else:
                guildconfig.toggle[toggle_name] = on_off
                toggle_onoff = 'on' if on_off else 'off'
                response = f'`Welcome to BE` listener is {toggle_onoff}'
        finally:
            await ctx.send(response)

    @commands.command(name='toggles')
    @staff_command()
    async def toggles(self, ctx):
        
        title = f'{ctx.guild.name} Toggles'
        response = Embed(colour=Colours.techrock)
        response.set_author(name=title, icon_url=Icons.techrock)

        guild_toggles = _get(ctx.guild.id, 'toggles')
        for key, value in guild_toggles.items():
            response.add_field(name=key, value=value, inline=False)
        await ctx.send(embed=response)

    @commands.group(name = 'groups')
    @mod_command()
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
    
            mods_roles = '\n'.join(mods)
            staff_roles = '\n'.join(staff)
            others_roles = '\n'.join(others)
    
            group_list = Embed(colour=Colours.techrock)
            group_list.set_author(name=title, icon_url=Icons.techrock)
            group_list.add_field(name='Moderators', value=mods_roles)
            group_list.add_field(name='Staff', value=staff_roles)
            group_list.add_field(name='Others', value=others_roles)
            await ctx.send(embed=group_list)

    @groups.command(name = 'add')
    async def groups_add(self, ctx, role, group=None):
        """Add a role to a group"""

        role = role.lower()
        group = group.lower() if group else None

        # Check if role exists
        for _role in ctx.guild.roles:
            if role==_role.name:
                role_id = _role.id
                break
        else:
            await ctx.send(f'`{role}` role for {ctx.guild.name} cannot be found')
            return

        guild_config = GuildConfig.get_config(ctx.guild.id)
        # Add role_id to guild config dictionary if not already
        if role not in guild_config.roles:
            guild_config.roles.update({role: role_id})

        if group is not None:
            if role in guild_config.group[group]:
                await ctx.send(f'`{role}` role is already in {group}')
            else:
                guild_config.group[group].append(role)
                await ctx.send(f'Added `{role}` role as {group}')

    @groups.command(name = 'remove_role')
    async def groups_remove(self, ctx, role, group):
        """Remove a role from a group"""
        role = role.lower()
        group = group.lower()
        guild_config = GuildConfig.get_config(ctx.guild.id)
        if role in guild_config.group[group]:
            if role=='admin':
                await ctx.send(f'Cannot remove Admin role')
            else:
                guild_config.group[group].remove(role)
                await ctx.send(f'Removed `{role}` role as {group}')
        else:
            await ctx.send(f'`{role}` role is not in {group}')

def setup(bot):
    bot.add_cog(Guilds(bot))