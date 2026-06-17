import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import json
import os

WARNINGS_FILE = "data/warnings.json"

def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r") as f:
        return json.load(f)

def save_warnings(data):
    os.makedirs("data", exist_ok=True)
    with open(WARNINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def ok(title, desc):
    return discord.Embed(title=f"✅ {title}", description=desc, color=discord.Color.green())

def err(title, desc):
    return discord.Embed(title=f"❌ {title}", description=desc, color=discord.Color.red())

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(embed=err("Permission Denied", "You cannot kick someone with an equal or higher role."), ephemeral=True)
        await member.kick(reason=reason)
        await interaction.response.send_message(embed=ok("Member Kicked", f"**{member}** has been kicked.\n**Reason:** {reason}"))

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(embed=err("Permission Denied", "You cannot ban someone with an equal or higher role."), ephemeral=True)
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=ok("Member Banned", f"**{member}** has been banned.\n**Reason:** {reason}"))

    @app_commands.command(name="unban", description="Unban a user by their ID")
    @app_commands.describe(user_id="The ID of the user to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(embed=ok("Member Unbanned", f"**{user}** has been unbanned."))
        except discord.NotFound:
            await interaction.response.send_message(embed=err("Not Found", "No banned user found with that ID."), ephemeral=True)
        except ValueError:
            await interaction.response.send_message(embed=err("Invalid ID", "Please provide a valid user ID."), ephemeral=True)

    @app_commands.command(name="mute", description="Timeout (mute) a member")
    @app_commands.describe(member="Member to mute", duration="Duration in minutes (default: 10)", reason="Reason for the mute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(embed=err("Permission Denied", "You cannot mute someone with an equal or higher role."), ephemeral=True)
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await interaction.response.send_message(embed=ok("Member Muted", f"**{member}** muted for **{duration} minutes**.\n**Reason:** {reason}"))

    @app_commands.command(name="unmute", description="Remove a timeout from a member")
    @app_commands.describe(member="Member to unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(embed=ok("Member Unmuted", f"**{member}** has been unmuted."))

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        warnings = load_warnings()
        gid = str(interaction.guild.id)
        uid = str(member.id)
        warnings.setdefault(gid, {}).setdefault(uid, [])
        warnings[gid][uid].append({"reason": reason, "warned_by": str(interaction.user), "warned_by_id": str(interaction.user.id)})
        save_warnings(warnings)
        count = len(warnings[gid][uid])
        await interaction.response.send_message(embed=ok("Member Warned", f"**{member}** warned. (Total: **{count}**)\n**Reason:** {reason}"))

    @app_commands.command(name="warnings", description="View a member's warnings")
    @app_commands.describe(member="Member to check")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        warnings = load_warnings()
        user_warnings = warnings.get(str(interaction.guild.id), {}).get(str(member.id), [])
        if not user_warnings:
            return await interaction.response.send_message(embed=discord.Embed(description=f"**{member}** has no warnings.", color=discord.Color.blurple()), ephemeral=True)
        embed = discord.Embed(title=f"⚠️ Warnings for {member}", color=discord.Color.orange())
        for i, w in enumerate(user_warnings, 1):
            embed.add_field(name=f"Warning #{i}", value=f"**Reason:** {w['reason']}\n**By:** {w['warned_by']}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarnings", description="Clear all warnings for a member")
    @app_commands.describe(member="Member to clear warnings for")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        warnings = load_warnings()
        gid, uid = str(interaction.guild.id), str(member.id)
        if gid in warnings and uid in warnings[gid]:
            warnings[gid][uid] = []
            save_warnings(warnings)
        await interaction.response.send_message(embed=ok("Warnings Cleared", f"All warnings for **{member}** cleared."))

    @app_commands.command(name="purge", description="Bulk delete messages (1–200)")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 200:
            return await interaction.response.send_message(embed=err("Invalid Amount", "Please specify between 1 and 200."), ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(embed=ok("Messages Purged", f"Deleted **{len(deleted)}** messages."), ephemeral=True)

    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        msg = "Slowmode disabled." if seconds == 0 else f"Slowmode set to **{seconds} seconds**."
        await interaction.response.send_message(embed=ok("Slowmode Updated", msg))

    @app_commands.command(name="lock", description="Lock the current channel")
    @app_commands.describe(reason="Reason for locking")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        ow = interaction.channel.overwrites_for(interaction.guild.default_role)
        ow.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
        await interaction.response.send_message(embed=ok("Channel Locked", f"🔒 Channel locked.\n**Reason:** {reason}"))

    @app_commands.command(name="unlock", description="Unlock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        ow = interaction.channel.overwrites_for(interaction.guild.default_role)
        ow.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=ow)
        await interaction.response.send_message(embed=ok("Channel Unlocked", "🔓 Channel unlocked."))

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(embed=err("Missing Permissions", "You don't have permission to use this command."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=err("Error", str(error)), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
