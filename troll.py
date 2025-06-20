import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class TrollCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ghosting = {}  # Maps user_id (controller) -> member to mimic
        self.processed_messages = set()  # Track processed messages

    # /ghostping
    @app_commands.command(name="ghostping", description="Ghost ping a user then delete it.")
    async def ghostping(self, interaction: discord.Interaction, member: discord.Member):
        msg = await interaction.channel.send(f"{member.mention}")
        await asyncio.sleep(0.5)
        await msg.delete()
        await interaction.response.send_message("Ghost pinged. 💨", ephemeral=True)

    # /flip
    def flip_text(self, text):
        flip_table = str.maketrans(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.,!?",
            "ɐqɔpǝɟƃɥᴉɾʞʃɯuodbɹsʇnʌʍxʎz∀ᗺƆᗡƎℲ⅁HIſʞ˥WNOԀΌЯS⊥∩ΛMX⅄Z⇂ᄅƐㄣϛ9ㄥ860'˙¡¿"
        )
        return text.translate(flip_table)[::-1]

    @app_commands.command(name="flip", description="Flip your text upside down.")
    async def flip(self, interaction: discord.Interaction, text: str):
        flipped = self.flip_text(text)
        await interaction.response.send_message(flipped)

    # /fakeban
    @app_commands.command(name="fakeban", description="Fake ban someone for fun.")
    async def fakeban(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"{member.mention} has been **banned** from the server. Reason: fucking idiot")
        await asyncio.sleep(2)
        await interaction.followup.send("Just kidding. Or am I?")

    # /scramble
    @app_commands.command(name="scramble", description="Scramble a member's display name.")
    async def scramble(self, interaction: discord.Interaction, member: discord.Member):
        name = member.display_name
        scrambled = ''.join(random.sample(name, len(name)))
        await interaction.response.send_message(f"Your new name is: **{scrambled}** 😜")

    # /trolltype
    @app_commands.command(name="trolltype", description="Pretend the bot is typing forever.")
    async def trolltype(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with interaction.channel.typing():
            await asyncio.sleep(30)
        await interaction.followup.send("Oops, lost my train of thought...")

    # /creepjoin
    @app_commands.command(name="creepjoin", description="Bot joins your VC, then leaves.")
    async def creepjoin(self, interaction: discord.Interaction):
        if interaction.user.voice:
            vc = await interaction.user.voice.channel.connect()
            await interaction.response.send_message("👻")
            await asyncio.sleep(20)
            await vc.disconnect()
        else:
            await interaction.response.send_message("You need to be in a voice channel!")

    # /ghost - start ghost typing as a user
    @app_commands.command(name="ghost", description="Start ghost typing as a mentioned user.")
    async def ghost(self, interaction: discord.Interaction, member: discord.Member):
        self.ghosting[interaction.user.id] = member
        await interaction.response.send_message(
            f"You are now ghost typing as {member.display_name}. Your messages will be sent as them and your originals deleted."
        )

    # /ghost_stop - stop ghost typing
    @app_commands.command(name="ghost_stop", description="Stop ghost typing.")
    async def ghost_stop(self, interaction: discord.Interaction):
        if interaction.user.id in self.ghosting:
            del self.ghosting[interaction.user.id]
            await interaction.response.send_message("Stopped ghost typing.")
        else:
            await interaction.response.send_message("You are not ghost typing anyone.")

    # Mimic ghost typing + original mimic listener
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Create a unique identifier for this message
        message_id = f"{message.id}_{message.channel.id}"
        
        # Check if we've already processed this message
        if message_id in self.processed_messages:
            print(f"DEBUG: Message {message_id} already processed, skipping")
            return
            
        # Add to processed set
        self.processed_messages.add(message_id)
        print(f"DEBUG: Processing message {message_id} from {message.author.name}: {message.content}")
        
        # Clean up old message IDs (keep only last 1000)
        if len(self.processed_messages) > 1000:
            self.processed_messages.clear()

        # Ghost typing mimic using webhook impersonation and delete original message
        if message.author.id in self.ghosting:
            target = self.ghosting[message.author.id]
            if len(message.content) > 0 and message.guild:
                try:
                    # Get or create webhook named "GhostWebhook" for this channel
                    webhooks = await message.channel.webhooks()
                    webhook = discord.utils.get(webhooks, name="GhostWebhook")
                    if webhook is None:
                        webhook = await message.channel.create_webhook(name="GhostWebhook")

                    # Send the message as the target user via webhook
                    await webhook.send(
                        content=message.content,
                        username=target.display_name,
                        avatar_url=target.display_avatar.url,
                    )
                    # Delete original message to keep ghost effect
                    await message.delete()
                except Exception as e:
                    print(f"Error in ghost typing: {e}")

        # Original mimic behavior
        if "?" not in message.content and len(message.content) > 5 and random.random() < 0.1:
            await message.channel.send(f"{message.content.lower()} 🤓")
            
        # Process commands (required for text commands to work)
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(TrollCommands(bot))
