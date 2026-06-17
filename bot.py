import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        COGS = ["cogs.moderation", "cogs.hire", "cogs.embeds", "cogs.misc"]
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        synced = await self.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")

    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/ commands"
        ))

bot = Bot()

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Bot Commands", description="All commands are slash commands.", color=discord.Color.blurple())
    embed.add_field(name="🔨 Moderation", value=(
        "`/kick` `/ban` `/unban` `/mute` `/unmute`\n"
        "`/warn` `/warnings` `/clearwarnings`\n"
        "`/purge` `/slowmode` `/lock` `/unlock`"
    ), inline=False)
    embed.add_field(name="💼 Hiring", value="`/hire` — Interactive hire wizard", inline=False)
    embed.add_field(name="🖼️ Embeds", value="`/embed` `/announce` `/say`", inline=False)
    embed.add_field(name="🛠️ Misc", value=(
        "`/ping` `/serverinfo` `/userinfo`\n"
        "`/avatar` `/roleinfo` `/membercount` `/uptime`"
    ), inline=False)
    embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
