import discord
from discord.ext import commands
from discord import app_commands
import os

HIRE_LOG_CHANNEL = os.getenv("HIRE_LOG_CHANNEL", "hire-log")

class HireModal(discord.ui.Modal, title="Hire a Member"):
    role_name = discord.ui.TextInput(label="Role they are being hired for", placeholder="e.g. Moderator, Staff, Manager...", max_length=100)

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        role_input = self.role_name.value.strip()

        # Try to find an actual Discord role matching the input
        role = discord.utils.find(lambda r: r.name.lower() == role_input.lower(), interaction.guild.roles)

        # Assign role if found
        role_assigned = False
        if role:
            try:
                await self.member.add_roles(role, reason=f"Hired by {interaction.user}")
                role_assigned = True
            except discord.Forbidden:
                pass

        # Confirmation embed
        embed = discord.Embed(title="✅ Hire Successful", color=discord.Color.green())
        embed.add_field(name="👤 Hired User", value=self.member.mention, inline=True)
        embed.add_field(name="🏷️ Role", value=role.mention if role else f"`{role_input}`", inline=True)
        embed.add_field(name="📋 Hired By", value=interaction.user.mention, inline=True)
        if role and not role_assigned:
            embed.add_field(name="⚠️ Note", value="Could not assign the Discord role (missing permissions).", inline=False)
        elif not role:
            embed.add_field(name="⚠️ Note", value="No matching Discord role found — hire logged without role assignment.", inline=False)
        embed.set_thumbnail(url=self.member.display_avatar.url)
        embed.set_footer(text=f"User ID: {self.member.id}")
        await interaction.response.send_message(embed=embed)

        # Log embed
        log_channel = None
        if HIRE_LOG_CHANNEL.isdigit():
            log_channel = interaction.guild.get_channel(int(HIRE_LOG_CHANNEL))
        else:
            log_channel = discord.utils.get(interaction.guild.text_channels, name=HIRE_LOG_CHANNEL.lstrip("#"))

        if log_channel:
            log_embed = discord.Embed(title="📋 New Hire Log", color=discord.Color.gold())
            log_embed.add_field(name="👤 Hired User", value=f"{self.member} ({self.member.mention})", inline=True)
            log_embed.add_field(name="🏷️ Role", value=role.mention if role else f"`{role_input}`", inline=True)
            log_embed.add_field(name="📋 Hired By", value=f"{interaction.user} ({interaction.user.mention})", inline=False)
            log_embed.add_field(name="📍 Channel", value=interaction.channel.mention, inline=True)
            log_embed.set_thumbnail(url=self.member.display_avatar.url)
            log_embed.set_footer(text=f"User ID: {self.member.id} | {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
            await log_channel.send(embed=log_embed)

class Hire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hire", description="Hire a member — assigns a role and logs it")
    @app_commands.describe(member="The member you want to hire")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def hire(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_modal(HireModal(member))

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ You need **Manage Roles** permission.", color=discord.Color.red()),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Hire(bot))
