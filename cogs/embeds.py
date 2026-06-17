import discord
from discord.ext import commands
from discord import app_commands

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Send a custom embed in this channel")
    @app_commands.describe(title="Embed title", description="Embed description", color="Hex color (e.g. ff0000)", ephemeral="Only you can see this?")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, interaction: discord.Interaction, title: str, description: str, color: str = "5865f2", ephemeral: bool = False):
        try:
            clr = discord.Color(int(color.strip("#"), 16))
        except ValueError:
            clr = discord.Color.blurple()
        embed = discord.Embed(title=title, description=description, color=clr)
        embed.set_footer(text=f"Sent by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.command(name="announce", description="Send an announcement embed with @everyone to a channel")
    @app_commands.describe(channel="Target channel", title="Announcement title", message="Announcement body")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, message: str):
        embed = discord.Embed(title=f"📢 {title}", description=message, color=discord.Color.gold())
        embed.set_footer(text=f"Announcement by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        await channel.send("@everyone", embed=embed)
        await interaction.response.send_message(
            embed=discord.Embed(description=f"✅ Announcement sent to {channel.mention}", color=discord.Color.green()),
            ephemeral=True
        )

    @app_commands.command(name="say", description="Make the bot send a message to a channel")
    @app_commands.describe(message="What to say", channel="Channel to send it in (defaults to current)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
        target = channel or interaction.channel
        await target.send(message)
        await interaction.response.send_message(
            embed=discord.Embed(description=f"✅ Message sent to {target.mention}", color=discord.Color.green()),
            ephemeral=True
        )

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ You don't have permission to use this command.", color=discord.Color.red()),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(description=f"❌ Error: {error}", color=discord.Color.red()),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Embeds(bot))
