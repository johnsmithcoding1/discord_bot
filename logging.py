import discord
from discord.ext import commands
import logging
import datetime
from typing import Optional

log = logging.getLogger('event_logger')

class EventTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def format_account_age(self, created_at: datetime.datetime) -> str:
        now = datetime.datetime.now(tz=created_at.tzinfo)  # Use the same tz as created_at
        age = now - created_at
        years, remainder = divmod(age.days, 365)
        months, days = divmod(remainder, 30)
        return f"{years} years, {months} months, {days} days"

    def build_user_embed(self, *, member: discord.abc.User, action: str, emoji_title: str, emoji_desc: str, color: discord.Color) -> discord.Embed:
        now = datetime.datetime.utcnow()
        account_age = self.format_account_age(member.created_at)

        embed = discord.Embed(
            title=f"{emoji_title} Member {action}",
            description=f"{emoji_desc} {member.mention} has {action.lower()}.",
            color=color,
            timestamp=now
        )
        embed.add_field(name=":Info: Account Age", value=account_age, inline=False)
        embed.add_field(name=":member: User Tag", value=member.name, inline=False)
        embed.set_footer(text=f"🆔 ID: {member.id} • {now.strftime('%I:%M %p')}")
        if hasattr(member, 'display_avatar'):
            embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    def get_log_channel(self, guild: discord.Guild):
        log_channels = self.bot.CONFIG.get("log_channels", {})
        channel_id = log_channels.get(str(guild.id))
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    async def log_embed(self, guild, title, description, color=discord.Color.blurple()):
        channel = self.get_log_channel(guild)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.log_embed(
            member.guild,
            "Member Joined",
            f"{member.mention} joined the server.",
            discord.Color.green()
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.log_embed(
            member.guild,
            "Member Left",
            f"{member.mention} left the server.",
            discord.Color.red()
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await self.log_embed(
            guild,
            "Member Banned",
            f"{user.mention} was banned.",
            discord.Color.dark_red()
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await self.log_embed(
            guild,
            "Member Unbanned",
            f"{user.mention} was unbanned.",
            discord.Color.green()
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel != after.channel:
            if before.channel is None:
                info = f"User: {user.mention} ({user.id})\nJoined: {after.channel.mention}"
                await self.log_embed(user.guild, "Voice Connect", info, discord.Color.green())
            elif after.channel is None:
                info = f"User: {user.mention} ({user.id})\nLeft: {before.channel.mention}"
                await self.log_embed(user.guild, "Voice Disconnect", info, discord.Color.red())
            else:
                info = f"User: {user.mention} ({user.id})\nFrom: {before.channel.mention}\nTo: {after.channel.mention}"
                await self.log_embed(user.guild, "Voice Moved", info, discord.Color.blurple())

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        await self.log_embed(
            message.guild,
            "Message Deleted",
            f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content}",
            discord.Color.red()
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return
        await self.log_embed(
            before.guild,
            "Message Edited",
            f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}\n**Before:** {before.content}\n**After:** {after.content}",
            discord.Color.orange()
        )

    @commands.Cog.listener()
    async def on_member_update(self, old: discord.Member, new: discord.Member):
        if old.nick != new.nick:
            info = f"User: {old.mention} ({old.id})\nOld Nick: {old.nick}\nNew Nick: {new.nick}"
            await self.log_embed(old.guild, "Nickname Changed", info, discord.Color.blue())

        if old.roles != new.roles:
            gained = set(new.roles) - set(old.roles)
            lost = set(old.roles) - set(new.roles)

            if gained:
                info = f"User: {new.mention} ({new.id})\nGained: {', '.join(r.mention for r in gained)}"
                await self.log_embed(new.guild, "Roles Added", info, discord.Color.green())

            if lost:
                info = f"User: {new.mention} ({new.id})\nRemoved: {', '.join(r.mention for r in lost)}"
                await self.log_embed(new.guild, "Roles Removed", info, discord.Color.red())

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        await self.log_embed(
            channel.guild,
            "Channel Created",
            f"{channel.mention} was created.",
            discord.Color.green()
        )

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        await self.log_embed(
            channel.guild,
            "Channel Deleted",
            f"{channel.name} was deleted.",
            discord.Color.red()
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if before.name != after.name:
            await self.log_embed(
                before.guild,
                "Channel Renamed",
                f"{before.name} renamed to {after.name}.",
                discord.Color.blue()
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(EventTracker(bot))
