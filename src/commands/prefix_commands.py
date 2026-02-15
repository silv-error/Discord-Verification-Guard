"""
Legacy prefix commands for backward compatibility
"""
import discord
from discord.ext import commands
from src.config import COLOR_INFO


def register_prefix_commands(bot):
    """Register all prefix commands"""
    
    @bot.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup_autokick(ctx, role_name: str = None, kick_after_minutes: int = None):
        """Legacy prefix command for setup"""
        guild_id = ctx.guild.id
        config = bot.get_guild_config(guild_id)
        
        if role_name is None and kick_after_minutes is None:
            embed = discord.Embed(
                title="⚙️ Auto-Kick Configuration",
                description=f"Current settings for **{ctx.guild.name}**\n\n💡 **Tip:** Use `/setup` for slash commands!",
                color=COLOR_INFO
            )
            embed.add_field(name="Target Role", value=f"`{config['role_name']}`", inline=False)
            embed.add_field(name="Kick After", value=f"`{config['kick_after_minutes']}` minutes", inline=False)
            
            dm_status = "✅ Enabled" if config.get('send_dm', False) else "❌ Disabled"
            embed.add_field(name="DM Notifications", value=dm_status, inline=False)
            
            log_channel = ctx.guild.get_channel(config.get('log_channel_id')) if config.get('log_channel_id') else None
            log_status = log_channel.mention if log_channel else "❌ Not set"
            embed.add_field(name="Log Channel", value=log_status, inline=False)
            
            tracked_count = len(bot.unverified_members.get(guild_id, {}))
            embed.add_field(name="Currently Tracking", value=f"{tracked_count} member(s)", inline=False)
            
            await ctx.send(embed=embed)
            return
        
        if role_name is not None:
            config['role_name'] = role_name
        
        if kick_after_minutes is not None:
            if kick_after_minutes < 1:
                await ctx.send("❌ Kick time must be at least 1 minute.")
                return
            config['kick_after_minutes'] = kick_after_minutes
        
        bot.guild_configs[guild_id] = config
        bot.save_data()
        
        await ctx.send(f"✅ Configuration updated! Role: `{config['role_name']}`, Kick after: `{config['kick_after_minutes']}` minutes")
        
        bot.unverified_members[guild_id] = {}
        from src.tasks import scan_existing_members
        await scan_existing_members(bot)
    
    @bot.command(name='autokick_help')
    async def autokick_help(ctx):
        """Show help message"""
        embed = discord.Embed(
            title="🤖 Auto-Kick Bot Commands",
            description="💡 **Tip:** Use slash commands by typing `/` for a better experience!",
            color=COLOR_INFO
        )
        
        embed.add_field(
            name="Slash Commands (Recommended)",
            value="`/setup` `/status` `/setlogchannel` `/toggledm` `/help`",
            inline=False
        )
        
        embed.add_field(
            name="Legacy Commands",
            value="`!setup` `!autokick_help`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @bot.event
    async def on_command_error(ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permissions to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument. Use `!autokick_help` to see command usage.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument. Use `!autokick_help` to see command usage.")
