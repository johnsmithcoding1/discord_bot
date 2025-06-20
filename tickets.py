import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import asyncio

# Transcript log channel ID
TRANSCRIPT_LOG_CHANNEL_ID = 1383649876427931689

class TicketDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class TicketTypeSelect(discord.ui.Select):
    ticket_counter = 1

    def __init__(self):
        options = [
            discord.SelectOption(label="Support", value="support", description="Get help from our team", emoji="🛠️"),
            discord.SelectOption(label="General Question", value="general", description="Ask a general question", emoji="❓"),
            discord.SelectOption(label="Report User", value="report", description="Report a user to staff", emoji="🚨"),
        ]
        super().__init__(placeholder="Select your ticket type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        ticket_number = TicketTypeSelect.ticket_counter
        TicketTypeSelect.ticket_counter += 1
        thread_name = f"ticket-{ticket_number:03d}-{interaction.user.name}"

        thread = await interaction.channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread
        )

        support_mention = "<@&1360780843945033919>"
        ticket_type = self.values[0].replace('_', ' ').title()
        await thread.send(
            f"Thank you for opening a ticket! {support_mention} will be with you shortly.\n**Ticket Type:** {ticket_type}",
            view=TicketControls()
        )
        await interaction.response.send_message(f"Ticket created: {thread.mention}", ephemeral=True)

class CloseOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Transcript & Close Ticket", style=discord.ButtonStyle.red, custom_id="close_transcript")
    async def transcript_and_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        messages = []
        async for msg in interaction.channel.history(limit=500, oldest_first=True):
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = msg.author.display_name
            content = msg.content or ''
            messages.append(f"[{timestamp}] {author}: {content}")
        transcript_text = "\n".join(messages) or "No messages found."
        filename = f"transcript_{interaction.channel.id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        log_channel = interaction.guild.get_channel(TRANSCRIPT_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                content=f"Transcript for {interaction.channel.mention}:",
                file=discord.File(filename)
            )
        os.remove(filename)

        await interaction.followup.send("📄 Transcript delivered. This ticket is now closed (locked).", ephemeral=True)
        await asyncio.sleep(2)
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(archived=True, locked=True)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.red, custom_id="close_delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ Deleting ticket...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed = False

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.blurple, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed:
            return await interaction.response.send_message("This ticket has already been claimed.", ephemeral=True)
        self.claimed = True
        button.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"Ticket claimed by {interaction.user.mention}.", ephemeral=False)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="show_close_options")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Close Ticket Options",
            description="Click an action below to process this ticket:",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=CloseOptionsView(), ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_publish_time = {}  # Track last publish time per user

    @commands.command(name="publish")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 2, commands.BucketType.user)  # 1 use per 2 seconds per user
    async def publish(self, ctx):
        """Publicly post the ticket panel using a message command."""
        embed = discord.Embed(
            title="🎫 Need Help? Open a Ticket!",
            description=(
                "Welcome to the support center!\n"
                "Select your ticket type below.\n\n"
                "**Options:**\n"
                "🛠️ Support — Get help from our team\n"
                "❓ General Question — Ask anything about our server\n"
                "🚨 Report User — Report a user to staff"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Our team will respond as soon as possible.")
        await ctx.send(embed=embed, view=TicketDropdown())

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        else:
            print(f"Cog error: {error}")
            await interaction.response.send_message("An error occurred.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
