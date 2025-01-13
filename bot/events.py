import discord
import wavelink
import config
import traceback
import sys
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
from discord.ext import tasks


def setup_events(bot: commands.Bot):
    player_idle_times = {}

    @tasks.loop(seconds=60)
    async def check_player_idle():
        try:
            for guild_id, node in wavelink.Pool.nodes.items():
                player = node.get_player(guild_id)

                if not player or not player.connected:
                    continue

                if not player.playing:
                    if guild_id not in player_idle_times:
                        player_idle_times[guild_id] = 0
                    player_idle_times[guild_id] += 1

                    if player_idle_times[guild_id] >= 5:
                        try:
                            channel = player.channel
                            if channel:
                                await channel.send("🚪 Đã rời khỏi kênh voice do không hoạt động.")

                            await player.disconnect()

                            del player_idle_times[guild_id]
                        except Exception as e:
                            print(f"Lỗi khi rời khỏi voice channel: {e}")
                else:
                    if guild_id in player_idle_times:
                        del player_idle_times[guild_id]
        except Exception as e:
            print(f"Lỗi trong task kiểm tra player: {e}")

    @bot.event
    async def on_ready():
        check_player_idle.start()
        print("Task kiểm tra player idle đã được bắt đầu")

        try:
            node = wavelink.Node(
                uri=f'{config.LAVALINK_HOST}:{config.LAVALINK_PORT}',
                password=config.LAVALINK_PASSWORD,
                identifier=config.INDENTIFIER
            )
            await wavelink.Pool.connect(nodes=[node], client=bot)
            print(f'Lavalink đã kết nối: {
                  config.LAVALINK_HOST}:{config.LAVALINK_PORT}')
        except Exception as e:
            print(f"Lỗi kết nối Lavalink: {e}")
            traceback.print_exc()

        try:
            synced = await bot.tree.sync()
            print(f"Đã đồng bộ {len(synced)} slash command")
        except Exception as e:
            print(f"Lỗi đồng bộ slash command: {e}")
            traceback.print_exc()

    @bot.event
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        logging.info("Wavelink Node connected: %r | Resumed: %s",
                     payload.node, payload.resumed)

    @bot.event
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player: wavelink.Player | None = payload.player
        if not player:
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: discord.Embed = discord.Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += f"\n\n`This track was recommended via {
                track.source}`"

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        await player.home.send(embed=embed)

    @bot.event
    async def on_member_join(member: discord.Member):
        try:
            channel = member.guild.system_channel or member.guild.text_channels[0]

            embed = discord.Embed(
                title="🎉 Chào mừng thành viên mới!",
                description=f"Xin chào {
                    member.mention}! Chào mừng bạn đến với server của chúng tôi.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)

            await channel.send(embed=embed)
        except Exception as e:
            print(f"Lỗi khi chào mừng thành viên mới: {e}")
            traceback.print_exc()

    @bot.event
    async def on_member_remove(member: discord.Member):
        try:
            channel = member.guild.system_channel or member.guild.text_channels[0]

            embed = discord.Embed(
                title="👋 Tạm biệt!",
                description=f"**{member.name}** đã rời khỏi server.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)

            await channel.send(embed=embed)
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn tạm biệt: {e}")
            traceback.print_exc()

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """Xử lý lỗi chung cho các lệnh"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Lệnh không tồn tại. Sử dụng `$help` để xem danh sách lệnh.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Thiếu tham số. Chi tiết: {error}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Tham số không hợp lệ. Chi tiết: {error}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bạn không có quyền thực hiện lệnh này.")
        else:
            print(f"Lỗi không xác định: {error}")
            traceback.print_exc()
            await ctx.send("❌ Đã xảy ra lỗi không mong muốn.")

    @bot.event
    async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Xử lý lỗi cho Slash Commands"""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"❌ Lệnh đang trong thời gian chờ. Thử lại sau {
                    error.retry_after:.2f} giây.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Bạn không có quyền thực hiện lệnh này.",
                ephemeral=True
            )
        else:
            print(f"Lỗi Slash Command: {error}")
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Đã xảy ra lỗi không mong muốn.",
                ephemeral=True
            )

    @bot.event
    async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id == bot.user.id:
            return

        try:
            for guild_id, node in wavelink.Pool.nodes.items():
                player = node.get_player(guild_id)

                if player and player.connected:
                    if guild_id in player_idle_times:
                        del player_idle_times[guild_id]
        except Exception as e:
            print(f"Lỗi trong on_voice_state_update: {e}")

    @bot.event
    async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload):
        player = payload.player

        if player and player.guild.id in player_idle_times:
            del player_idle_times[player.guild.id]
