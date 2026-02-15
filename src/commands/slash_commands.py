"""
Slash commands for the Auto-Kick Bot
"""
import discord
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional
from src.config import COLOR_INFO, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING


def register_slash_commands(bot):
    """Register all slash commands"""
    
    @bot.tree.command(name="setup", description="Configure auto-kick settings for this server")
    @app_commands.describe(
        role_name="The name of the unverified role",
        kick_after_minutes="Minutes before kicking (minimum 1)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setup(
        interaction: discord.Interaction,
        role_name: Optional[str] = None,
        kick_after_minutes: Optional[int] = None
    ):
        """Slash command for setup"""
        guild_id = interaction.guild.id
        config = bot.get_guild_config(guild_id)
        
        # If no parameters, show current config
        if role_name is None and kick_after_minutes is None:
            embed = discord.Embed(
                title="⚙️ Auto-Kick Configuration",
                description=f"Current settings for **{interaction.guild.name}**",
                color=COLOR_INFO
            )
            embed.add_field(name="Target Role", value=f"`{config['role_name']}`", inline=False)
            embed.add_field(name="Kick After", value=f"`{config['kick_after_minutes']}` minutes", inline=False)
            
            dm_status = "✅ Enabled" if config.get('send_dm', False) else "❌ Disabled"
            embed.add_field(name="DM Notifications", value=dm_status, inline=False)
            
            log_channel = interaction.guild.get_channel(config.get('log_channel_id')) if config.get('log_channel_id') else None
            log_status = log_channel.mention if log_channel else "❌ Not set"
            embed.add_field(name="Log Channel", value=log_status, inline=False)
            
            tracked_count = len(bot.unverified_members.get(guild_id, {}))
            embed.add_field(name="Currently Tracking", value=f"{tracked_count} member(s)", inline=False)
            
            role = discord.utils.get(interaction.guild.roles, name=config['role_name'])
            if role:
                embed.add_field(name="Role Status", value=f"✅ {role.mention}", inline=False)
            else:
                embed.add_field(name="Role Status", value=f"⚠️ Role not found!", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update configuration
        if role_name is not None:
            config['role_name'] = role_name
        
        if kick_after_minutes is not None:
            if kick_after_minutes < 1:
                await interaction.response.send_message("❌ Kick time must be at least 1 minute.", ephemeral=True)
                return
            config['kick_after_minutes'] = kick_after_minutes
        
        bot.guild_configs[guild_id] = config
        bot.save_data()
        
        embed = discord.Embed(
            title="✅ Configuration Updated",
            description=f"Settings for **{interaction.guild.name}**",
            color=COLOR_SUCCESS
        )
        embed.add_field(name="Target Role", value=f"`{config['role_name']}`", inline=False)
        embed.add_field(name="Kick After", value=f"`{config['kick_after_minutes']}` minutes", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Rescan
        bot.unverified_members[guild_id] = {}
        from src.tasks import scan_existing_members
        await scan_existing_members(bot)
    
    @bot.tree.command(name="status", description="View all tracked unverified members")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_status(interaction: discord.Interaction):
        """Slash command for status"""
        guild_id = interaction.guild.id
        config = bot.get_guild_config(guild_id)
        
        if guild_id not in bot.unverified_members or not bot.unverified_members[guild_id]:
            await interaction.response.send_message("✅ No unverified members currently being tracked.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Auto-Kick Status",
            description=f"Members with `{config['role_name']}` role",
            color=COLOR_WARNING
        )
        
        now = datetime.now()
        kick_threshold = timedelta(minutes=config['kick_after_minutes'])
        
        tracked_count = 0
        for member_id, join_timestamp in bot.unverified_members[guild_id].items():
            member = interaction.guild.get_member(member_id)
            
            if member:
                join_time = datetime.fromtimestamp(join_timestamp)
                time_elapsed = now - join_time
                time_remaining = kick_threshold - time_elapsed
                
                if time_remaining.total_seconds() > 0:
                    minutes_remaining = int(time_remaining.total_seconds() / 60)
                    seconds_remaining = int(time_remaining.total_seconds() % 60)
                    embed.add_field(
                        name=f"{member.name}",
                        value=f"⏱️ {minutes_remaining}m {seconds_remaining}s",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"{member.name}",
                        value=f"⚠️ Overdue",
                        inline=True
                    )
                
                tracked_count += 1
                if tracked_count >= 25:
                    break
        
        from src.config import CHECK_INTERVAL_MINUTES
        embed.set_footer(text=f"Total: {len(bot.unverified_members[guild_id])} | Next check in ~{CHECK_INTERVAL_MINUTES} min")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="setlogchannel", description="Set the channel for kick logs")
    @app_commands.describe(channel="The channel where kick logs will be sent")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the log channel for kick notifications"""
        guild_id = interaction.guild.id
        config = bot.get_guild_config(guild_id)
        
        config['log_channel_id'] = channel.id
        bot.guild_configs[guild_id] = config
        bot.save_data()
        
        embed = discord.Embed(
            title="✅ Log Channel Set",
            description=f"Kick logs will now be sent to {channel.mention}",
            color=COLOR_SUCCESS
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send test log
        test_embed = discord.Embed(
            description="✅ **Log channel configured successfully**\nKick logs will appear here.",
            color=COLOR_SUCCESS,
            timestamp=datetime.now()
        )
        test_embed.set_footer(text="Auto-Kick System")
        
        try:
            await channel.send(embed=test_embed)
        except:
            await interaction.followup.send("⚠️ Make sure I have permissions to send messages!", ephemeral=True)
    
    @bot.tree.command(name="toggledm", description="Enable or disable DM notifications before kicking")
    @app_commands.describe(enabled="Turn DM notifications on or off")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_toggledm(interaction: discord.Interaction, enabled: bool):
        """Toggle DM notifications"""
        guild_id = interaction.guild.id
        config = bot.get_guild_config(guild_id)
        
        config['send_dm'] = enabled
        bot.guild_configs[guild_id] = config
        bot.save_data()
        
        status = "enabled ✅" if enabled else "disabled ❌"
        embed = discord.Embed(
            title="📬 DM Notifications",
            description=f"DM notifications are now **{status}**",
            color=COLOR_SUCCESS if enabled else COLOR_ERROR
        )
        
        if not enabled:
            embed.add_field(
                name="Note",
                value="Members will be kicked silently without warning.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="help", description="Show all available commands")
    async def slash_help(interaction: discord.Interaction):
        """Show help message"""
        embed = discord.Embed(
            title="🤖 Auto-Kick Bot Commands",
            description="Automatically kick members who don't verify in time",
            color=COLOR_INFO
        )
        
        embed.add_field(
            name="/setup",
            value="Configure role name and kick timer",
            inline=False
        )
        
        embed.add_field(
            name="/status",
            value="View all tracked members and time remaining",
            inline=False
        )
        
        embed.add_field(
            name="/setlogchannel",
            value="Set channel for kick logs",
            inline=False
        )
        
        embed.add_field(
            name="/toggledm",
            value="Enable/disable DM warnings (optional)",
            inline=False
        )
        
        embed.add_field(
            name="/help",
            value="Show this help message",
            inline=False
        )
        
        embed.set_footer(text="⚠️ Admin commands require Administrator permission")
        await interaction.response.send_message(embed=embed, ephemeral=True)
