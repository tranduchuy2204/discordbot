import discord
from discord import app_commands, ui, ButtonStyle
from discord.ext import commands
import wavelink
import traceback
from typing import Optional


class MusicControlView(ui.View):
    def __init__(self, ctx: commands.Context, player: wavelink.Player):
        super().__init__()
        self.ctx = ctx
        self.player = player
        self.timeout = 180.0

    @ui.button(label="⏭️ Skip", style=ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: ui.Button):
        if not self.player.queue:
            await interaction.response.send_message("Không còn bài hát trong hàng đợi.", ephemeral=True)
            return

        await self.player.stop()
        next_track = await self.player.queue.get_wait()
        await self.player.play(next_track)

        embed = discord.Embed(
            title="⏭️ Bài hát tiếp theo",
            description=f"**{next_track.title}** đã được phát",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @ui.button(label="⏸️ Pause/Resume", style=ButtonStyle.secondary)
    async def pause_resume_button(self, interaction: discord.Interaction, button: ui.Button):
        if self.player.paused:
            await self.player.pause(False)
            await interaction.response.send_message("▶️ Tiếp tục phát nhạc", ephemeral=True)
        else:
            await self.player.pause(True)
            await interaction.response.send_message("⏸️ Tạm dừng phát nhạc", ephemeral=True)

    @ui.button(label="🔁 Lặp", style=ButtonStyle.green)
    async def loop_button(self, interaction: discord.Interaction, button: ui.Button):
        status = ''
        try:
            if self.player.queue.mode is not wavelink.QueueMode.loop:
                status = 'Bật'
                self.player.queue.mode = wavelink.QueueMode.loop
            else:
                status = 'Tắt'
                self.player.queue.mode = wavelink.QueueMode.normal
        except Exception as e:
            status = 'Lỗi'
            print(f"Lỗi khi thay đổi chế độ lặp: {e}")

        await interaction.response.send_message(f"🔁 Chế độ lặp: {status}", ephemeral=True)

    @ui.button(label="❌ Dừng", style=ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.player.disconnect()
        await interaction.response.send_message("🛑 Đã dừng phát nhạc", ephemeral=True)
        self.stop()

    @ui.button(label="🔊 Âm lượng", style=ButtonStyle.secondary)
    async def volume_button(self, interaction: discord.Interaction, button: ui.Button):
        view = VolumeControlView(self.player)

        embed = discord.Embed(
            title="🔊 Điều chỉnh âm lượng",
            description="Chọn mức âm lượng mong muốn",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class VolumeControlView(ui.View):
    def __init__(self, player: wavelink.Player):
        super().__init__()
        self.player = player
        self.timeout = 60.0

    @ui.button(label="🔉 Giảm", style=ButtonStyle.primary)
    async def volume_down(self, interaction: discord.Interaction, button: ui.Button):
        current_volume = self.player.volume
        new_volume = max(0, current_volume - 10)
        await self.player.set_volume(new_volume)

        await interaction.response.send_message(
            f"🔊 Âm lượng đã giảm xuống {new_volume}%",
            ephemeral=True
        )

    @ui.button(label="🔊 Tăng", style=ButtonStyle.primary)
    async def volume_up(self, interaction: discord.Interaction, button: ui.Button):
        current_volume = self.player.volume
        new_volume = min(100, current_volume + 10)
        await self.player.set_volume(new_volume)

        await interaction.response.send_message(
            f"🔊 Âm lượng đã tăng lên {new_volume}%",
            ephemeral=True
        )


def setup_music_commands(bot: commands.Bot):
    @bot.tree.command(name="play", description="Phát nhạc từ YouTube")
    @app_commands.describe(query="Tên bài hát hoặc link YouTube")
    async def play_music(interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            await interaction.response.send_message("Bạn phải ở trong voice channel!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel

        if not wavelink.Pool.get_node():
            await interaction.response.send_message("Không thể kết nối đến máy chủ âm nhạc!", ephemeral=True)
            return

        try:
            tracks = await wavelink.Playable.search(query, source=None)

            if not tracks:
                await interaction.response.send_message("Không tìm thấy bài hát!", ephemeral=True)
                return

            if len(tracks) > 1:
                view = TrackSelectionView(interaction.user, tracks)
                embed = discord.Embed(
                    title="🎵 Chọn bài hát",
                    description="Vui lòng chọn một bài hát từ danh sách:",
                    color=discord.Color.blue()
                )

                for i, track in enumerate(tracks[:5], 1):
                    embed.add_field(
                        name=f"{i}. {track.title}",
                        value=f"Nghệ sĩ: {track.author}",
                        inline=False
                    )

                await interaction.response.send_message(embed=embed, view=view)
                return

            track = tracks[0]

            try:
                player = await voice_channel.connect(cls=wavelink.Player)
            except discord.ClientException:
                player = wavelink.Pool.get_node().get_player(interaction.guild.id)

            await player.queue.put_wait(track)

            if not player.playing:
                await player.play(player.queue.get(), volume=30)

            view = MusicControlView(interaction, player)

            embed = discord.Embed(
                title="🎵 Đang phát nhạc",
                description=f"Đã thêm **{track.title}** vào danh sách phát",
                color=discord.Color.green()
            )
            embed.add_field(name="Nghệ sĩ", value=track.author, inline=True)
            embed.add_field(name="Thời lượng", value=f"{
                            track.length/1000:.2f} giây", inline=True)

            await interaction.response.send_message(embed=embed, view=view)

        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(f"Lỗi: {str(e)}", ephemeral=True)

    class TrackSelectionView(ui.View):
        def __init__(self, user: discord.User, tracks: list):
            super().__init__()
            self.user = user
            self.tracks = tracks
            self.timeout = 60.0

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user == self.user

        @ui.button(label="1️⃣", style=ButtonStyle.primary)
        async def select_first(self, interaction: discord.Interaction, button: ui.Button):
            await self.play_selected_track(interaction, 0)

        @ui.button(label="2️⃣", style=ButtonStyle.primary)
        async def select_second(self, interaction: discord.Interaction, button: ui.Button):
            await self.play_selected_track(interaction, 1)

        @ui.button(label="3️⃣", style=ButtonStyle.primary)
        async def select_third(self, interaction: discord.Interaction, button: ui.Button):
            await self.play_selected_track(interaction, 2)

        @ui.button(label="4️⃣", style=ButtonStyle.primary)
        async def select_fourth(self, interaction: discord.Interaction, button: ui.Button):
            await self.play_selected_track(interaction, 3)

        @ui.button(label="5️⃣", style=ButtonStyle.primary)
        async def select_fifth(self, interaction: discord.Interaction, button: ui.Button):
            await self.play_selected_track(interaction, 4)

        async def play_selected_track(self, interaction: discord.Interaction, index: int):
            try:
                voice_channel = interaction.user.voice.channel
                track = self.tracks[index]

                player = await voice_channel.connect(cls=wavelink.Player)

                await player.queue.put_wait(track)

                if not player.playing:
                    await player.play(player.queue.get(), volume=50)

                view = MusicControlView(interaction, player)

                embed = discord.Embed(
                    title="🎵 Đang phát nhạc",
                    description=f"Đã chọn và phát **{track.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Nghệ sĩ", value=track.author, inline=True)
                embed.add_field(name="Thời lượng", value=f"{
                                track.length/1000:.2f} giây", inline=True)

                await interaction.response.send_message(embed=embed, view=view)

                self.stop()

            except Exception as e:
                traceback.print_exc()
                await interaction.response.send_message(f"Lỗi: {str(e)}", ephemeral=True)

    @bot.tree.command(name="queue", description="Hiển thị danh sách phát")
    async def show_queue(interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild_id)

        if not player or not player.queue:
            await interaction.response.send_message("Không có bài hát trong hàng đợi.", ephemeral=True)
            return

        embed = discord.Embed(title="🎵 Danh sách phát",
                              color=discord.Color.blue())

        if player.current:
            embed.description = f"**Đang phát:** {player.current.title}"

        for i, track in enumerate(list(player.queue)[:10], 1):
            embed.add_field(
                name=f"{i}. {track.title}",
                value=f"Nghệ sĩ: {track.author}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="stop", description="Dừng phát nhạc")
    async def stop_music(interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild_id)

        if not player:
            await interaction.response.send_message("Bot không ở trong voice channel!", ephemeral=True)
            return

        await player.disconnect()
        await interaction.response.send_message("🛑 Đã dừng phát nhạc và rời khỏi voice channel", ephemeral=True)

    @bot.tree.command(name="volume", description="Điều chỉnh âm lượng phát nhạc")
    @app_commands.describe(
        volume="Mức âm lượng từ 0-100 (%)"
    )
    async def set_volume(
        interaction: discord.Interaction,
        volume: app_commands.Range[int, 0, 100]
    ):
        """Điều chỉnh âm lượng phát nhạc"""
        player = wavelink.Pool.get_node().get_player(interaction.guild_id)

        if not player:
            await interaction.response.send_message(
                "Bot không ở trong voice channel!",
                ephemeral=True
            )
            return

        try:
            await player.set_volume(volume)

            embed = discord.Embed(
                title="🔊 Điều chỉnh âm lượng",
                description=f"Đã đặt âm lượng thành {volume}%",
                color=discord.Color.green()
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"Lỗi khi điều chỉnh âm lượng: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="current-volume", description="Kiểm tra âm lượng hiện tại")
    async def get_current_volume(interaction: discord.Interaction):
        """Hiển thị âm lượng hiện tại"""
        player = wavelink.Pool.get_node().get_player(interaction.guild_id)

        if not player:
            await interaction.response.send_message(
                "Bot không ở trong voice channel!",
                ephemeral=True
            )
            return

        current_volume = player.volume

        embed = discord.Embed(
            title="🔊 Âm lượng hiện tại",
            description=f"Âm lượng đang được đặt ở mức {current_volume}%",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)
