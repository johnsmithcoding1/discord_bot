from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Moderation cog loaded!")

    @app_commands.command(name="nickname", description="Change a member's nickname in every server the bot shares with them.")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nickname(self, interaction: discord.Interaction, member: discord.Member, nickname: Optional[str] = None):
        successes = 0
        failures = 0
        for guild in self.bot.guilds:
            try:
                target = guild.get_member(member.id)
                if not target:
                    continue
                bot_member = guild.me
                if not bot_member.guild_permissions.manage_nicknames:
                    failures += 1
                    continue
                if target.top_role >= bot_member.top_role:
                    failures += 1
                    continue
                await target.edit(nick=nickname)
                successes += 1
            except Exception:
                failures += 1
        await interaction.response.send_message(
            f"Nickname changed in {successes} server(s). Failed in {failures} server(s).",
            ephemeral=True
        )

    @app_commands.command(name="ban", description="Ban a member from all servers the bot shares with them.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        successes = 0
        failures = 0
        for guild in self.bot.guilds:
            try:
                target = guild.get_member(member.id)
                if not target:
                    continue
                await target.ban(reason=reason)
                successes += 1
            except Exception:
                failures += 1
        await interaction.response.send_message(
            f"Banned {member.mention} in {successes} server(s). Failed in {failures} server(s).",
            ephemeral=True
        )

    @app_commands.command(name="kick", description="Kick a member from all servers the bot shares with them.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        successes = 0
        failures = 0
        for guild in self.bot.guilds:
            try:
                target = guild.get_member(member.id)
                if not target:
                    continue
                await target.kick(reason=reason)
                successes += 1
            except Exception:
                failures += 1
        await interaction.response.send_message(
            f"Kicked {member.mention} in {successes} server(s). Failed in {failures} server(s).",
            ephemeral=True
        )

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            if interaction.response.is_done():
                await interaction.followup.send("You don't have permission to use this command!", ephemeral=True)
            else:
                await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        else:
            # If you want logging, import logging and set up a logger, or just print
            print(f"An error occurred: {error}")
            if interaction.response.is_done():
                await interaction.followup.send("An error occurred while processing the command.", ephemeral=True)
            else:
                await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 