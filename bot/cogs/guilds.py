import discord
import logging
import os

from discord.ext import commands
from pathlib import Path
from typing import Dict, List

import yaml

log = logging.getLogger(__name__)

class Guilds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        log.info(f'Joined {guild.name}')
        if Path(f'configs/{guild.id}.yml').exists():
            log.info(f'Config file for {guild.name} found')
            return

        log.info(f'No config for {guild.name} found, creating {guild.id}.yml')
        with open('configs/default.yml', encoding='utf-8') as f:
            default = yaml.safe_load(f)

        default['guild']['id'] = guild.id

        # Build Dict for parsing id from roles
        roleids = {}
        for role in guild.roles:
            roleids[role.name.lower] = role.id

        for role in default['guild']['roles']:
            try:
                default['guild']['roles'][role] = roleids[role]
            except:
                log.info(f'Role {role} not found')

        with open(f'configs/{guild.id}.yml', 'w', encoding='utf-8') as f:
            yaml.dump(default, f, default_flow_style=False, indent=4)

    @commands.command()
    async def mockjoin(self, ctx):
    
        guild = ctx.guild
        
        os.remove(f'configs/{guild.id}.yml')

        log.info(f'No config for {guild.name} found, creating {guild.id}.yml')
        with open('configs/default.yml', encoding='utf-8') as f:
            default = yaml.safe_load(f)

        default['guild']['id'] = guild.id

        # Build Dict for parsing id from roles
        guildroles = {}
        for role in guild.roles:
            guildroles[role.name.lower()] = role.id
        
        for role in default['guild']['roles']:
            try:
                default['guild']['roles'][role] = guildroles[role]
            except:
                log.info(f'Role {role} not found')

        with open(f'configs/{guild.id}.yml', 'w', encoding='utf-8') as f:
            yaml.dump(default, f, default_flow_style=False, indent=4)

    @commands.command(name = 'add_prefix')
    async def add_prefix(self, ctx, prefix):
        with open(f'configs/{ctx.guild.id}.yml', 'r+') as f:
            guildconfig = yaml.safe_load(f)
            if prefix in guildconfig['bot']['prefix']:
                await ctx.send(f'`{prefix}` is already a prefix')
                return
            guildconfig['bot']['prefix'].append(prefix)
            await ctx.send(f'Added `{prefix}` as a prefix')
            f.seek(0)
            yaml.dump(guildconfig, f, default_flow_style=False, indent=4)
            f.truncate()

    @commands.command(name = 'remove_prefix')
    async def remove_prefix(self, ctx, prefix):
        with open(f'configs/{ctx.guild.id}.yml', 'r+') as f:
            guildconfig = yaml.safe_load(f)
            if prefix not in guildconfig['bot']['prefix']:
                await ctx.send(f'`{prefix}` is not a prefix')
                return
            guildconfig['bot']['prefix'].remove(prefix)
            await ctx.send(f'Removed `{prefix}` as a prefix')
            if len(guildconfig['bot']['prefix'])==0:
                await ctx.send('Note: TRB commands can be invoked by mentioning')
            f.seek(0)
            yaml.dump(guildconfig, f, default_flow_style=False, indent=4)
            f.truncate()

def setup(bot):
    bot.add_cog(Guilds(bot))