import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

TARGET_CHANNEL_ID = 1384217951317786725

TRAINING_EMOJIS = {
    "Basic Cadet - Trooper Training": "🎓",
    "Spike Training": "📌",
    "FTO Training": "👮",
    "Master FTO Training": "⭐",
}

class AttendButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✅ Attending", style=discord.ButtonStyle.success, custom_id="attend")

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        if not message.embeds:
            await interaction.response.send_message("Error: No embed found.", ephemeral=True)
            return
        embed = message.embeds[0]
        attendees_index = None
        for i, field in enumerate(embed.fields):
            if field.name.startswith(":busts_in_silhouette:"):
                attendees_index = i
                break
        if attendees_index is None:
            await interaction.response.send_message("Error: Attendees field not found.", ephemeral=True)
            return
        attendees_value = embed.fields[attendees_index].value
        if interaction.user.mention in attendees_value:
            await interaction.response.send_message("You are already marked as attending!", ephemeral=True)
            return
        if attendees_value.strip() == "Click the button below to sign up!":
            new_attendees = interaction.user.mention
        else:
            new_attendees = attendees_value + "\n" + interaction.user.mention
        embed.set_field_at(attendees_index, name=":busts_in_silhouette: Attendees:", value=new_attendees, inline=False)
        await message.edit(embed=embed)
        await interaction.response.send_message("You have been marked as attending!", ephemeral=True)

class CancelButton(discord.ui.Button):
    def __init__(self, host_id: int):
        super().__init__(label="❌ Cancel Training", style=discord.ButtonStyle.danger, custom_id="cancel_training")
        self.host_id = host_id
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("Only the host can cancel this training.", ephemeral=True)
            return
        await interaction.message.delete()
        await interaction.response.send_message("Training cancelled and message deleted.", ephemeral=True)

class AttendCancelView(discord.ui.View):
    def __init__(self, host_id: int):
        super().__init__()
        self.add_item(AttendButton())
        self.add_item(CancelButton(host_id))

TRAINING_CHOICES = [
    app_commands.Choice(name="Basic Cadet - Trooper Training", value="Basic Cadet - Trooper Training"),
    app_commands.Choice(name="Spike Training", value="Spike Training"),
    app_commands.Choice(name="FTO Training", value="FTO Training"),
    app_commands.Choice(name="Master FTO Training", value="Master FTO Training"),
]

def get_time_choices():
    now = datetime.now()
    min_start = now + timedelta(hours=1)
    minute = min_start.minute
    if minute == 0:
        start = min_start.replace(minute=0, second=0, microsecond=0)
    elif minute <= 30:
        start = min_start.replace(minute=30, second=0, microsecond=0)
    else:
        start = (min_start + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2)
    options = []
    current = start
    while current <= end:
        label = current.strftime("%I:%M %p").lstrip("0")
        value = current.strftime("%H:%M")
        options.append(app_commands.Choice(name=label, value=value))
        current += timedelta(minutes=30)
    return options

class Training(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Training cog loaded!")
        self.scheduled_trainings = []
        self.cleanup_task.start()

    @app_commands.command(name="training", description="Schedule a training session")
    @app_commands.describe(
        training_type="Select the type of training",
        start_time="Select the start time (at least 1 hour from now, rounded up)"
    )
    @app_commands.choices(training_type=TRAINING_CHOICES)
    async def training(self, interaction: discord.Interaction,
                       training_type: app_commands.Choice[str],
                       start_time: str):
        host_mention = interaction.user.mention
        host_id = interaction.user.id

        now = datetime.now()
        time_obj = datetime.strptime(start_time, "%H:%M")
        start_dt = now.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
        if start_dt < now:
            start_dt += timedelta(days=1)

        min_time = now + timedelta(hours=1)
        max_time = now + timedelta(hours=2, minutes=30)
        if not (min_time <= start_dt <= max_time):
            await interaction.response.send_message(
                f"❌ Please select a start time between "
                f"{min_time.strftime('%I:%M %p').lstrip('0')} and {max_time.strftime('%I:%M %p').lstrip('0')}.",
                ephemeral=True
            )
            return

        display_time = start_dt.strftime("%I:%M %p").lstrip("0")
        discord_relative = f"<t:{int(start_dt.timestamp())}:R>"

        emoji = TRAINING_EMOJIS.get(training_type.value, "")

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=f"{training_type.value} {emoji}")
        embed.add_field(
            name=":busts_in_silhouette: Attendees:",
            value="Click the button below to sign up!",
            inline=False
        )
        embed.add_field(
            name=":arrow_right: Start Time:",
            value=f"{display_time} • {discord_relative}",
            inline=False
        )
        embed.add_field(
            name=":arrow_right: Hosted By:",
            value=host_mention,
            inline=False
        )
        embed.add_field(
            name=":arrow_right: Information:",
            value=(
                "Plan on joining the VC [here](https://discord.com/channels/"
                "1367189109411549364/1384217951791742976) 10–15 minutes in advance.\n"
                "Click below if you are attending."
            ),
            inline=False
        )

        view = AttendCancelView(host_id)

        target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            await interaction.response.send_message("❌ Could not find the training announcements channel.", ephemeral=True)
            return

        try:
            sent_message = await target_channel.send(embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to post training session: {e}", ephemeral=True)
            return

        end_time = start_dt + timedelta(hours=2)

        self.scheduled_trainings.append({
            "message_id": sent_message.id,
            "channel_id": target_channel.id,
            "end_time": end_time,
        })

        await interaction.response.send_message(
            f"✅ Training session posted in {target_channel.mention}. It will be removed after the training ends.",
            ephemeral=True
        )
        # Do not send any more interaction responses after this point!

    @training.autocomplete("start_time")
    async def start_time_autocomplete(self, interaction: discord.Interaction, current: str):
        # Only respond once to the autocomplete interaction
        if interaction.response.is_done():
            return
        await interaction.response.send_autocomplete(get_time_choices())

async def setup(bot: commands.Bot):
    await bot.add_cog(Training(bot)) 