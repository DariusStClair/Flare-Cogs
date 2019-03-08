from redbot.core import commands, Config, checks
import discord


class Modmail(commands.Cog):
    """Forward messages to a set channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1398467138476)
        default_global = {"modmail": {}, "toggle": {"status": True}, "type": {"command": False}}
        self.config.register_global(**default_global)

    async def channelsend(self, embed2):
        async with self.config.toggle() as toggle:
            if not toggle['status']:
                return
        async with self.config.modmail() as modmail:
            for stats in modmail:
                channel = self.bot.get_channel(modmail[stats])
                await channel.send(embed=embed2)

    async def on_message(self, message):
        if message.guild is not None:
            return
        if message.author == self.bot.user:
            return
        async with self.config.type() as type:
            if type['command']:
                return
        if message.attachments or not any(
                message.content.startswith(prefix) for prefix in await self.bot.get_prefix(message)):
            embeds = []
            attachments_urls = []
            embeds.append(discord.Embed(description=message.content))
            embeds[0].set_author(name=f"{message.author} | {message.author.id}", icon_url=message.author.avatar_url)
            for attachment in message.attachments:
                if any(attachment.filename.endswith(imageext) for imageext in ["jpg", "png", "gif"]):
                    if embeds[0].image:
                        embed = discord.Embed()
                        embed.set_image(url=attachment.url)
                        embeds.append(embed)
                    else:
                        embeds[0].set_image(url=attachment.url)
                else:
                    attachments_urls.append(f"[{attachment.filename}]({attachment.url})")
            if attachments_urls:
                embeds[0].add_field(name="Attachments", value="\n".join(attachments_urls))
            embeds[-1].timestamp = message.created_at
            for embed in embeds:
                await self.channelsend(embed)

    @checks.is_owner()
    @commands.group(autohelp=True)
    async def modmailset(self, ctx):
        """Modmail Commands"""
        pass

    @commands.command()
    async def modmail(self, ctx, *, content: str = None):
        """Manually send modmail."""
        async with self.config.type() as type:
            if not type['command']:
                await ctx.send("Modmail is currently set to be recieved via DMs, this can be changed via [p]modmailset")
                return
        if ctx.message.attachments or content:
            embeds = []
            attachments_urls = []
            embeds.append(discord.Embed(description=content))
            embeds[0].set_author(name=f"{ctx.author} | {ctx.author.id}", icon_url=ctx.author.avatar_url)
            for attachment in ctx.message.attachments:
                if any(attachment.filename.endswith(imageext) for imageext in ["jpg", "png", "gif"]):
                    if embeds[0].image:
                        embed = discord.Embed()
                        embed.set_image(url=attachment.url)
                        embeds.append(embed)
                    else:
                        embeds[0].set_image(url=attachment.url)
                else:
                    attachments_urls.append(f"[{attachment.filename}]({attachment.url})")
            if attachments_urls:
                embeds[0].add_field(name="Attachments", value="\n".join(attachments_urls))
            embeds[-1].timestamp = ctx.message.created_at
            for embed in embeds:
                await self.channelsend(embed)

    @modmailset.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel that the bot will post to - Mention the channel."""
        async with self.config.modmail() as modmail:
            key = str(ctx.message.guild.id)
            modmail[key] = channel.id
        await ctx.send("Channel added successfully.")

    @modmailset.command()
    async def list(self, ctx):
        """List all current modmail channels."""
        async with self.config.modmail() as modmail:
            if not modmail:
                await ctx.send("No channels are currently set.")
            for stats in modmail:
                await ctx.send(modmail[stats])

    @modmailset.command()
    async def toggle(self, ctx, mode: bool):
        """Toggle modmail."""
        async with self.config.toggle() as toggle:
            if mode:
                toggle['status'] = True
                await ctx.send("ModMail is now enabled.")
            else:
                toggle['status'] = False
                await ctx.send("ModMail is now disabled.")

    @modmailset.command()
    async def command(self, ctx, mode: bool):
        """Toggle modmail between command or forwarding.
           True """
        async with self.config.type() as type:
            if mode:
                type['command'] = True
                await ctx.send("ModMail will now only be triggerd via [p]modmail.")
            else:
                type['command'] = False
                await ctx.send("ModMail will no longer forward every message sent via DM.")
