import discord
from discord import app_commands
from discord.ext import commands
import config
import discord.utils
import urllib.parse


def setup_global_commands(bot: commands.Bot):
    @bot.tree.command(name="clear", description="Xoá tin nhắn trong kênh")
    @app_commands.describe(amount="Số lượng tin nhắn cần xoá (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_messages(interaction: discord.Interaction, amount: int):
        try:
            if amount < 1 or amount > 100:
                await interaction.response.send_message("Số lượng tin nhắn cần xoá phải từ 1 đến 100!", ephemeral=True)
                return

            # Trì hoãn phản hồi vì xoá tin nhắn có thể mất thời gian
            await interaction.response.defer(ephemeral=True)

            # Xoá tin nhắn
            deleted = await interaction.channel.purge(limit=amount)

            # Gửi thông báo
            await interaction.followup.send(
                f"✅ Đã xoá {len(deleted)} tin nhắn.",
                ephemeral=True
            )

        except discord.Forbidden:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Bot không có quyền xoá tin nhắn trong kênh này!",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Bot không có quyền xoá tin nhắn trong kênh này!",
                    ephemeral=True
                )
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Đã xảy ra lỗi: {str(e)}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Đã xảy ra lỗi: {str(e)}",
                    ephemeral=True
                )

    @bot.tree.command(name="userinfo", description="Xem thông tin của người dùng")
    @app_commands.describe(member="Người dùng cần xem thông tin")
    async def user_info(interaction: discord.Interaction, member: discord.Member = None):
        try:
            # Nếu không chỉ định member thì lấy thông tin người gọi lệnh
            target = member or interaction.user

            # Tạo embed hiển thị thông tin
            embed = discord.Embed(
                title=f"👤 Thông tin người dùng",
                description=f"Thông tin chi tiết về {target.mention}",
                color=discord.Color.blue()
            )

            # Thêm avatar và thông tin người dùng
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.set_author(name=str(target),
                             icon_url=target.display_avatar.url)

            # Thông tin cơ bản
            embed.add_field(
                name="📝 Thông tin chung",
                value=f"**Tên hiển thị:** {target.display_name}\n"
                f"**ID:** {target.id}\n"
                f"**Bot:** {'🤖 Có' if target.bot else '👤 Không'}",
                inline=False
            )

            # Thông tin về thời gian
            created_time = int(target.created_at.timestamp())
            joined_time = int(target.joined_at.timestamp())
            embed.add_field(
                name="⏰ Thời gian",
                value=f"**Tham gia Discord:** <t:{
                    created_time}:D> (<t:{created_time}:R>)\n"
                f"**Tham gia Server:** <t:{
                    joined_time}:D> (<t:{joined_time}:R>)",
                inline=False
            )

            # Thông tin về role
            roles = [role.mention for role in reversed(target.roles[1:])]
            embed.add_field(
                name=f"🎭 Roles [{len(roles)}]",
                value=" ".join(roles) if roles else "Không có role",
                inline=False
            )

            # Thêm footer
            embed.set_footer(
                text=f"Yêu cầu bởi {interaction.user}",
                icon_url=interaction.user.display_avatar.url
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Đã xảy ra lỗi: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name='pay', description='Tạo mã QR thanh toán')
    @app_commands.describe(
        bank='Chọn ngân hàng',
        account_number='Số tài khoản',
        amount='Số tiền cần chuyển',
        content='Nội dung chuyển khoản'
    )
    @app_commands.choices(bank=[
        app_commands.Choice(name='VietinBank', value='ICB'),
        app_commands.Choice(name='Vietcombank', value='VCB'),
        app_commands.Choice(name='BIDV', value='BIDV'),
        app_commands.Choice(name='ACB', value='ACB'),
    ])
    async def pay(
        interaction: discord.Interaction,
        bank: app_commands.Choice[str],
        account_number: str,
        amount: int,
        content: str
    ):
        try:
            # Mã hóa nội dung và tạo URL QR code
            encoded_content = urllib.parse.quote(content)
            qr_url = f"https://img.vietqr.io/image/{bank.value}-{
                account_number}-compact2.jpg?amount={amount}&addInfo={encoded_content}"

            # Tạo embed hiển thị QR
            embed = discord.Embed(
                title="🏦 Mã QR Thanh Toán",
                description=f"**Số tiền:** {
                    amount:,} VNĐ\n**Nội dung:** {content}",
                color=discord.Color.green()
            )

            # Thêm thông tin tài khoản
            embed.add_field(
                name="📝 Thông tin tài khoản",
                value=f"**Ngân hàng:** {
                    bank.name}\n**Số tài khoản:** {account_number}",
                inline=False
            )

            # Thêm hình QR
            embed.set_image(url=qr_url)

            # Thêm footer
            embed.set_footer(
                text=f"Yêu cầu bởi {interaction.user}",
                icon_url=interaction.user.display_avatar.url
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Đã xảy ra lỗi: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="avatar", description="Xem avatar của người dùng")
    @app_commands.describe(member="Người dùng cần xem avatar")
    async def avatar(interaction: discord.Interaction, member: discord.Member = None):
        try:
            # Nếu không chỉ định member thì lấy avatar người gọi lệnh
            target = member or interaction.user

            # Tạo embed hiển thị avatar
            embed = discord.Embed(
                title=f"🖼️ Avatar của {target.display_name}",
                description="Nhấp vào các link bên dưới để tải avatar với định dạng tương ứng",
                color=target.color
            )

            # Thêm thông tin người dùng
            embed.set_author(
                name=str(target),
                icon_url=target.display_avatar.url
            )

            # Thêm avatar vào embed với kích thước lớn nhất
            embed.set_image(url=target.display_avatar.url)

            # Thêm các link avatar với các định dạng khác nhau
            formats = []
            if target.display_avatar.is_animated():
                formats.append(
                    f"[`GIF`]({target.display_avatar.replace(format='gif', size=4096).url})")
            formats.extend([
                f"[`PNG`]({target.display_avatar.replace(
                    format='png', size=4096).url})",
                f"[`JPG`]({target.display_avatar.replace(
                    format='jpg', size=4096).url})",
                f"[`WEBP`]({target.display_avatar.replace(
                    format='webp', size=4096).url})"
            ])

            embed.add_field(
                name="📥 Tải xuống",
                value=" • ".join(formats),
                inline=False
            )

            # Thêm footer
            embed.set_footer(
                text=f"ID: {target.id}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )

            # Thêm timestamp
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Đã xảy ra lỗi: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="chat", description="Chat với AI sử dụng Gemini")
    @app_commands.describe(prompt="Nội dung bạn muốn hỏi AI")
    async def chat(interaction: discord.Interaction, prompt: str):
        try:
            # Gửi thông báo đang xử lý
            await interaction.response.defer()

            # Tạo embed cho câu trả lời
            embed = discord.Embed(
                title="💬 Gemini AI",
                description="*Đang xử lý câu trả lời...*",
                color=discord.Color.blue()
            )

            # Gọi API Gemini và lấy phản hồi
            try:
                import google.generativeai as genai

                # Cấu hình API key
                genai.configure(api_key=config.GEMINI_API_KEY)

                # Khởi tạo model
                model = genai.GenerativeModel('gemini-1.5-flash')

                # Lấy phản hồi từ AI
                response = model.generate_content(prompt)

                # Cập nhật embed với câu trả lời
                embed.description = response.text
                embed.add_field(name="Câu hỏi", value=prompt, inline=False)

                await interaction.followup.send(embed=embed)

            except Exception as e:
                embed.description = f"❌ Lỗi khi gọi API Gemini: {str(e)}"
                embed.color = discord.Color.red()
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Đã xảy ra lỗi: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="server", description="Xem thông tin về server và cấu hình máy")
    async def server_info(interaction: discord.Interaction):
        try:
            # Lấy thông tin server
            guild = interaction.guild

            # Tạo embed
            embed = discord.Embed(
                title=f"📊 Thông tin Server: {guild.name}",
                color=discord.Color.blue()
            )

            # Thông tin cơ bản
            embed.add_field(
                name="🆔 Server ID",
                value=guild.id,
                inline=True
            )
            embed.add_field(
                name="👑 Chủ server",
                value=guild.owner.mention,
                inline=True
            )
            embed.add_field(
                name="📅 Ngày tạo",
                value=guild.created_at.strftime("%d/%m/%Y"),
                inline=True
            )

            # Thông tin thành viên
            embed.add_field(
                name="👥 Tổng thành viên",
                value=guild.member_count,
                inline=True
            )
            embed.add_field(
                name="🤖 Số lượng bot",
                value=len([m for m in guild.members if m.bot]),
                inline=True
            )
            embed.add_field(
                name="📝 Số lượng kênh",
                value=len(guild.channels),
                inline=True
            )

            # Thông tin boost
            embed.add_field(
                name="🚀 Boost Level",
                value=f"Level {guild.premium_tier}",
                inline=True
            )
            embed.add_field(
                name="💎 Số lượng boost",
                value=guild.premium_subscription_count,
                inline=True
            )

            # Server icon
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Đã xảy ra lỗi: {str(e)}",
                ephemeral=True
            )
