import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from typing import Optional

logger = logging.getLogger('discord_bot')

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _check_role_position(self, interaction: discord.Interaction, role: discord.Role) -> bool:
        return (role.position < interaction.user.top_role.position) or (interaction.user.id == interaction.guild.owner_id)

    @app_commands.command(name="giverole", description="Give a role to a member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def giverole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not self._check_role_position(interaction, role):
            await interaction.response.send_message("You can only assign roles below your highest role.", ephemeral=True)
            return
        try:
            await member.add_roles(role)
            await interaction.response.send_message(f"Added role {role.mention} to {member.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to add roles.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while adding the role.", ephemeral=True)

    @app_commands.command(name="removerole", description="Remove a role from a member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not self._check_role_position(interaction, role):
            await interaction.response.send_message("You can only remove roles below your highest role.", ephemeral=True)
            return
        try:
            await member.remove_roles(role)
            await interaction.response.send_message(f"Removed role {role.mention} from {member.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove roles.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while removing the role.", ephemeral=True)

    @app_commands.command(name="temprole", description="Give a role to a member temporarily.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def temprole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, duration: str):
        if not self._check_role_position(interaction, role):
            await interaction.response.send_message("You can only assign roles below your highest role.", ephemeral=True)
            return
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1].lower()
        if unit not in time_units:
            await interaction.response.send_message("Invalid duration format. Use s/m/h/d (e.g., 1h, 30m)", ephemeral=True)
            return
        try:
            amount = int(duration[:-1])
            seconds = amount * time_units[unit]
            await member.add_roles(role)
            await interaction.response.send_message(f"Added role {role.mention} to {member.mention} for {duration}", ephemeral=True)
            await asyncio.sleep(seconds)
            await member.remove_roles(role)
        except ValueError:
            await interaction.response.send_message("Invalid duration format. Use s/m/h/d (e.g., 1h, 30m)", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to manage roles.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while managing roles.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        else:
            logger.error(f"An error occurred: {error}")
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Roles(bot))
