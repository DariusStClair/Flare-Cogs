# -*- coding: utf-8 -*-
import asyncio
import typing
import urllib
from io import BytesIO

import aiohttp
import discord
import validators
from redbot.core import Config, commands
from redbot.core.utils.predicates import MessagePredicate

from .converters import ImageFinder


async def tokencheck(ctx):
    token = await ctx.bot.get_shared_api_tokens("imgen")
    return bool(token.get("authorization"))


class DankMemer(commands.Cog):
    """Dank Memer Commands."""

    __version__ = "0.0.13"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=95932766180343808, force_registration=True)
        self.config.register_global(url="https://imgen.flaree.xyz/api")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.headers = {}

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def initalize(self):
        self.api = await self.config.url()
        token = await self.bot.get_shared_api_tokens("imgen")
        self.headers = {"Authorization": token.get("authorization")}

    @commands.Cog.listener()
    async def on_red_api_tokens_update(self, service_name, api_tokens):
        if service_name == "imgen":
            self.headers = {"Authorization": api_tokens.get("authorization")}

    async def send_error(self, ctx, data):
        await ctx.send(f"Oops, an error occured. `{data['error']}`")

    async def get(self, ctx, url, json=False):
        async with ctx.typing():
            async with self.session.get(self.api + url, headers=self.headers) as resp:
                if resp.status == 200:
                    if json:
                        return await resp.json()
                    file = await resp.read()
                    file = BytesIO(file)
                    file.seek(0)
                    return file
                if resp.status == 404:
                    return {
                        "error": "Server not found, ensure the correct URL is setup and is reachable. "
                    }
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    return {"error": "Server may be down, please try again later."}

    async def send_img(self, ctx, image):
        if not ctx.channel.permissions_for(ctx.me).send_messages:
            return
        if not ctx.channel.permissions_for(ctx.me).attach_files:
            await ctx.send("I don't have permission to attach files.")
            return
        try:
            await ctx.send(file=image)
        except aiohttp.ClientOSError:
            await ctx.send("An error occured sending the picture.")

    def parse_text(self, text):
        return urllib.parse.quote(text)

    @commands.command()
    async def dankmemersetup(self, ctx):
        """Instructions on how to setup DankMemer."""
        msg = (
            "You must host your own instance of imgen or apply for a publically available instance.\n"
            f"You can then set the url endpoints using the `{ctx.clean_prefix}dmurl <url>` command. (Support will be limited if using your own instance.)\n\n"
            f"You can set the token using `{ctx.clean_prefix}set api imgen authorization <key>`"
        )
        await ctx.maybe_send_embed(msg)

    @commands.is_owner()
    @commands.command()
    async def dmurl(self, ctx, *, url: str):
        """Set the DankMemer API Url.

        Ensure the url ends in API without the backslash - Example: https://imgen.flaree.xyz/api
        Only use this if you have an instance already.
        """
        if not validators.url(url):
            return await ctx.send(f"{url} doesn't seem to be a valid URL. Please try again.")
        await ctx.send(
            "This has the ability to make every command fail if the URL is not reachable and/or not working. Only use this if you're experienced enough to understand. Type yes to continue, otherwise type no."
        )
        try:
            pred = MessagePredicate.yes_or_no(ctx, user=ctx.author)
            await ctx.bot.wait_for("message", check=pred, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Exiting operation.")
            return

        if pred.result:
            await self.config.url.set(url)
            await ctx.tick()
            await self.initalize()
        else:
            await ctx.send("Operation cancelled.")

    @commands.check(tokencheck)
    @commands.command()
    async def abandon(self, ctx, *, text: str):
        """Abandoning your son?"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/abandon?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "abandon.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command(aliases=["aborted"])
    async def abort(self, ctx, image: ImageFinder = None):
        """All the reasons why X was aborted."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/aborted?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "abort.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def affect(self, ctx, image: ImageFinder = None):
        """It won't affect my baby."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/affect?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "affect.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def airpods(self, ctx, image: ImageFinder = None):
        """Flex with airpods."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/airpods?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "airpods.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def america(self, ctx, image: ImageFinder = None):
        """Americafy a picture."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/america?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "america.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def armor(self, ctx, *, text: str):
        """Nothing gets through this armour."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/armor?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "armor.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def balloon(self, ctx, *, text: str):
        """Pop a balloon.

        Texts must be comma seperated.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/balloon?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "balloon.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def bed(self, ctx, user: discord.Member, user2: discord.Member = None):
        """There's a monster under my bed."""
        user2 = user2 or ctx.author
        user, user2 = user2, user
        data = await self.get(
            ctx,
            "/bed?avatar1={}{}".format(
                user.avatar_url_as(static_format="png"),
                f"&avatar2={user2.avatar_url_as(static_format='png')}"
                if user2 is not None
                else "",
            ),
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "bed.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def bongocat(self, ctx, image: ImageFinder = None):
        """Bongocat-ify your image."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/bongocat?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "bongocat.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def boo(self, ctx, *, text: str):
        """Scary.

        Texts must be comma seperated.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/boo?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "boo.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def brain(self, ctx, *, text: str):
        """Big brain meme.

        Texts must be 4 comma seperated items.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/brain?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "brain.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def brazzers(self, ctx, image: ImageFinder = None):
        """Brazzerfy your image."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/brazzers?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "brazzers.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def byemom(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """Bye mom.

        User is a discord user ID, name or mention.
        """
        user = user or ctx.author
        text = self.parse_text(text)

        data = await self.get(
            ctx,
            f"/byemom?avatar1={user.avatar_url_as(static_format='png')}&username1={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "byemom.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()  # TODO: Maybe remove?
    async def cancer(self, ctx, image: ImageFinder = None):
        """Squidward sign."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/cancer?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "cancer.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def changemymind(self, ctx, *, text: str):
        """Change my mind?"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/changemymind?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "changemymind.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def cheating(self, ctx, *, text: str):
        """Cheating?.

        Text must be comma seperated.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/cheating?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "cheating.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def crab(self, ctx, *, text: str):
        """Crab rave.

        Text must be comma seperated.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/crab?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "crabrave.mp4"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def paperplease(self, ctx, *, text: str):
        """Papers Please Citation.

        Text must be 3 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/citation?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "citation.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def communism(self, ctx, image: ImageFinder = None):
        """Communism-ify your picture."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/communism?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "communism.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def confusedcat(self, ctx, *, text: str):
        """Confused cat meme.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/confusedcat?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "confusedcat.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def corporate(self, ctx, image: ImageFinder = None):
        """Corporate meme."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/corporate?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "corporate.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def cry(self, ctx, *, text: str):
        """Drink my tears meme.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/cry?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "cry.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def dab(self, ctx, image: ImageFinder = None):
        """Hit a dab."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/dab?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "dab.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def dank(self, ctx, image: ImageFinder = None):
        """Dank, noscope 420."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/dank?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "dank.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def deepfried(self, ctx, image: ImageFinder = None):
        """Deepfry an image."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/deepfry?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "deepfry.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def delete(self, ctx, image: ImageFinder = None):
        """Delete Meme."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/delete?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "delete.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def disability(self, ctx, image: ImageFinder = None):
        """Disability Meme."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/disability?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "disability.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def doglemon(self, ctx, *, text: str):
        """Dog and Lemon Meme.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/doglemon?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "doglemon.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def door(self, ctx, image: ImageFinder = None):
        """Kick down the door meme."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/door?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "door.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def egg(self, ctx, image: ImageFinder = None):
        """Turn your picture into an egg."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/egg?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "egg.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def excuseme(self, ctx, *, text: str):
        """Excuse me, what the...

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/excuseme?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "excuseme.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def expanddong(self, ctx, *, text: str):
        """Expanding?

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/expanddong?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "expanddong.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def facts(self, ctx, *, text: str):
        """Facts book.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/facts?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "facts.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def failure(self, ctx, image: ImageFinder = None):
        """You're a failure meme."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/failure?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "failure.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def fakenews(self, ctx, image: ImageFinder = None):
        """Fake News."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/fakenews?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "fakenews.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def fedora(self, ctx, image: ImageFinder = None):
        """*Tips Fedora*."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/fedora?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "fedora.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def floor(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """The floor is ....

        User is a discord user ID, name or mention.
        """
        text = self.parse_text(text)
        user = user or ctx.author
        data = await self.get(
            ctx, f"/floor?avatar1={user.avatar_url_as(static_format='png')}&text={text}"
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "fedora.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def fuck(self, ctx, *, text: str):
        """Feck.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/fuck?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "fuck.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def garfield(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """I wonder who that's for - Garfield meme.

        User is a discord user ID, name or mention."""
        user = user or ctx.author
        text = self.parse_text(text)
        data = await self.get(
            ctx, f"/garfield?avatar1={user.avatar_url_as(static_format='png')}&text={text}"
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "garfield.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command(aliases=["rainbow", "lgbtq"])
    async def lgbt(self, ctx, image: ImageFinder = None):
        """Rainbow-fy your picture."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/gay?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "gay.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def goggles(self, ctx, image: ImageFinder = None):
        """Remember, safety goggles on."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/goggles?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "goggles.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def hitler(self, ctx, image: ImageFinder = None):
        """Worse than hitler?."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/hitler?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "hitler.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def humansgood(self, ctx, *, text: str):
        """Humans are wonderful things."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/humansgood?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "humansgood.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def inator(self, ctx, *, text: str):
        """Xinator."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/inator?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "inator.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command(aliases=["invertcolor", "invertcolors", "invercolours"])
    async def invertcolour(self, ctx, image: ImageFinder = None):
        """Invert the colour of an image."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/invert?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "invert.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def ipad(self, ctx, image: ImageFinder = None):
        """Put your picture on an ipad."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/ipad?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "ipad.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def jail(self, ctx, image: ImageFinder = None):
        """Send yourself to jail."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/jail?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "jail.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def justpretending(self, ctx, *, text: str):
        """Playing dead.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/justpretending?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "justpretending.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def kimborder(self, ctx, image: ImageFinder = None):
        """Place yourself under mighty kim."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/kimborder?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "kimborder.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def knowyourlocation(self, ctx, *, text: str):
        """Google wants to know your location.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/knowyourlocation?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "knowyourlocation.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()  # TODO: MP4s
    async def kowalski(self, ctx, *, text: str):
        """Kowlalski tapping.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/kowalski?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "kowalski.gif"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def laid(self, ctx, image: ImageFinder = None):
        """Do you get laid?"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/laid?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "laid.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()  # TODO: MP4s
    async def letmein(self, ctx, *, text: str):
        """LET ME IN."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/letmein?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "letmein.mp4"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def lick(self, ctx, *, text: str):
        """Lick lick.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/lick?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "lick.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def madethis(self, ctx, user: discord.Member, user2: discord.Member = None):
        """I made this!"""
        user2 = user2 or ctx.author
        user, user2 = user2, user
        data = await self.get(
            ctx,
            "/madethis?avatar1={}{}".format(
                user.avatar_url_as(static_format="png"),
                f"&avatar2={user2.avatar_url_as(static_format='png')}"
                if user2 is not None
                else "",
            ),
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "madethis.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()  # Support other urls soon
    async def magickify(self, ctx, image: ImageFinder = None):
        """Peform magik."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/magik?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "magik.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def master(self, ctx, *, text: str):
        """Yes master!

        Text must be 3 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/master?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "master.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def meme(
        self,
        ctx,
        image: typing.Optional[ImageFinder],
        top_text: str,
        bottom_text: str,
        color: typing.Optional[str],
        font: typing.Optional[str] = None,
    ):
        """Make your own meme.

        For text longer then one word for each variable, enclose them in "" This endpoint works a
        bit differently from the other endpoints. This endpoint takes in top_text and bottom_text
        parameters instead of text. It also supports color and font parameters. Fonts supported
        are: arial, arimobold, impact, robotomedium, robotoregular, sans, segoeuireg, tahoma and
        verdana. Colors can be defined with HEX codes or web colors, e.g. black, white, orange etc.
        Try your luck ;) The default is Impact in white.
        """
        top_text = urllib.parse.quote(top_text)
        bottom_text = urllib.parse.quote(bottom_text)
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        if font:
            fnt = f"&font={font}"
        else:
            fnt = ""
        if color:
            clr = f"&color={urllib.parse.quote(color)}"
        else:
            clr = ""
        data = await self.get(
            ctx, f"/meme?avatar1={image}&top_text={top_text}&bottom_text={bottom_text}{clr}{fnt}"
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "meme.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def note(self, ctx, *, text: str):
        """Pass a note back."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/note?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "note.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def nothing(self, ctx, *, text: str):
        """Woah!

        nothing.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/nothing?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "nothing.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def ohno(self, ctx, *, text: str):
        """Oh no, it's stupid!"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/ohno?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "ohno.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def piccolo(self, ctx, *, text: str):
        """Piccolo."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/piccolo?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "piccolo.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def plan(self, ctx, *, text: str):
        """Gru makes a plan.

        Text must be 3 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/plan?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "plan.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def presentation(self, ctx, *, text: str):
        """Lisa makes a presentation."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/presentation?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "presentation.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def quote(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """Quote a discord user."""
        user = user or ctx.author
        text = self.parse_text(text)
        data = await self.get(
            ctx,
            f"/quote?avatar1={user.avatar_url_as(static_format='png')}&username1={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "quote.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def radialblur(self, ctx, image: ImageFinder = None):
        """Radiarblur-ify your picture.."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/radialblur?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "radialblur.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command(aliases=["restinpeace"])
    async def tombstone(self, ctx, image: ImageFinder = None):
        """Give a lucky person a tombstone."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/rip?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "rip.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def roblox(self, ctx, image: ImageFinder = None):
        """Turn yourself into a roblox character."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/roblox?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "roblox.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def salty(self, ctx, image: ImageFinder = None):
        """Add some salt."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/salty?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "salty.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def satan(self, ctx, image: ImageFinder = None):
        """Place your picture over Satan."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/satan?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "satan.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def savehumanity(self, ctx, *, text: str):
        """The secret to saving humanity."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/savehumanity?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "savehumanity.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def screams(self, ctx, user: discord.Member, user2: discord.Member = None):
        """Why can't you just be normal?

        **Screams**
        """
        user2 = user2 or ctx.author
        user, user2 = user2, user
        data = await self.get(
            ctx,
            "/screams?avatar1={}{}".format(
                user.avatar_url_as(static_format="png"),
                f"&avatar2={user2.avatar_url_as(static_format='png')}"
                if user2 is not None
                else "",
            ),
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "screams.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def shit(self, ctx, *, text: str):
        """I stepped in crap."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/shit?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "shit.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def sickban(self, ctx, image: ImageFinder = None):
        """Ban this sick filth!"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/sickban?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "sickban.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def slap(self, ctx, user: discord.Member, user2: discord.Member = None):
        """*SLAPS*"""
        user2 = user2 or ctx.author
        user, user2 = user2, user
        data = await self.get(
            ctx,
            "/slap?avatar1={}{}".format(
                user.avatar_url_as(static_format="png"),
                f"&avatar2={user2.avatar_url_as(static_format='png')}"
                if user2 is not None
                else "",
            ),
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "slap.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def slapsroof(self, ctx, *, text: str):
        """This bad boy can fit so much in it."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/slapsroof?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "slapsroof.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def sneakyfox(self, ctx, *, text: str):
        """That sneaky fox.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/sneakyfox?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "sneakyfox.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def spank(self, ctx, user: discord.Member, user2: discord.Member = None):
        """*spanks*"""
        user2 = user2 or ctx.author
        user, user2 = user2, user
        data = await self.get(
            ctx,
            "/spank?avatar1={}{}".format(
                user.avatar_url_as(static_format="png"),
                f"&avatar2={user2.avatar_url_as(static_format='png')}"
                if user2 is not None
                else "",
            ),
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "spank.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def stroke(self, ctx, *, text: str):
        """How to recognize a stroke?"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/stroke?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "stroke.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def surprised(self, ctx, *, text: str):
        """Pikasuprised.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/surprised?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "surprised.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def sword(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """Swordknife.

        Text must be split on commas.
        """
        text = self.parse_text(text)
        user = user or ctx.author

        data = await self.get(
            ctx,
            f"/sword?avatar1={user.avatar_url_as(static_format='png')}&username1={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "sword.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def thesearch(self, ctx, *, text: str):
        """The search for intelligent life continues.."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/thesearch?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "thesearch.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def trash(self, ctx, image: ImageFinder = None):
        """Peter Parker trash."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/trash?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "trash.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def trigger(self, ctx, image: ImageFinder = None):
        """Triggerfied."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/trigger?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "trigger.gif"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def tweet(self, ctx, user: typing.Optional[discord.Member], *, text: str):
        """Create a fake tweet.

        user: discord User, takes their avatar, display name and name.
        text: String. Text to show on the generated image.
        """
        text = self.parse_text(text)
        user = user or ctx.author
        data = await self.get(
            ctx,
            f"/tweet?avatar1={user.avatar_url_as(static_format='png')}&username1={user.display_name}&username2={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "tweet.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def ugly(self, ctx, image: ImageFinder = None):
        """Make a user ugly."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/ugly?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "ugly.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def unpopular(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """Get rid of that pesky teacher."""
        user = user or ctx.author
        text = self.parse_text(text)
        data = await self.get(
            ctx,
            f"/unpopular?avatar1={user.avatar_url_as(static_format='png')}&username1={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "unpopular.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def violence(self, ctx, *, text: str):
        """Violence is never the answer."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/violence?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "violence.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def violentsparks(self, ctx, *, text: str):
        """Some violent sparks.

        Text must be 2 comma seperated values.
        """
        text = self.parse_text(text)
        data = await self.get(ctx, f"/violentsparks?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "violentsparks.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def vr(self, ctx, *, text: str):
        """Woah, VR is so realistic."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/vr?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "vr.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def walking(self, ctx, *, text: str):
        """Walking Meme."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/walking?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "walking.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def wanted(self, ctx, image: ImageFinder = None):
        """Heard you're a wanted fugitive?"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/wanted?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "wanted.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def warp(self, ctx, image: ImageFinder = None):
        """Warp?."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/warp?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "warp.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def whodidthis(self, ctx, image: ImageFinder = None):
        """Who did this?"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/whodidthis?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "whodidthis.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def whothisis(self, ctx, user: typing.Optional[discord.Member], username: str):
        """who this is."""
        user = user or ctx.author
        data = await self.get(
            ctx, f"/whothisis?avatar1={user.avatar_url_as(static_format='png')}&text={username}"
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "whothisis.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def yomomma(self, ctx):
        """Yo momma!."""
        data = await self.get(ctx, f"/yomomma", True)
        if data.get("error"):
            return await self.send_error(ctx, data)
        await ctx.send(data["text"])

    @commands.check(tokencheck)
    @commands.command()
    async def youtube(self, ctx, user: typing.Optional[discord.Member] = None, *, text: str):
        """Create a youtube comment."""
        user = user or ctx.author
        text = self.parse_text(text)
        data = await self.get(
            ctx,
            f"/youtube?avatar1={user.avatar_url_as(static_format='png')}&username1={user.name}&text={text}",
        )
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "youtube.png"
        await self.send_img(ctx, discord.File(data))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]
