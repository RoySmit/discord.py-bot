from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
								  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or

from ..db import db

PREFIX = "."
OWNER_IDS = [287969892689379331]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot,message):
	return when_mentioned_or(PREFIX)(bot, message)


class ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.cogs_ready = ready()

		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)
		super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS)

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f" {cog} cog loaded")

		print("setup complete")

	def run(self, version):
		self.VERSION = version

		print("running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:

				await self.invoke(ctx)

			else:
				await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

	async def rules_reminder(self):
		await self.stdout.send("Remember to add to rules!")

	async def on_connect(self):
		print(" bot connected")

	async def on_disconnect(self):
		print(" bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")

		await self.stdout.send("An error has occured")
		raise

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more required arguments are missing.")

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown, please wait {exc.retry_after:,.2f} seconds.")

		# elif isinstance(exc.original, HTTPException):
		# 	await ctx.send("Unable to send message.")

		elif isinstance(exc.original, Forbidden):
			await ctx.send("I do not have permission to do that.")

		else:
			raise exc.original


	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(721160314787201116)
			self.stdout = self.get_channel(721160314787201119)
			self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
			self.scheduler.start()

			embed = Embed(title="Now online", description="Shiina is now online.", 
						  colour=0xCCCC00, timestamp=datetime.utcnow())
			fields = [("Shiina", "Version 1.0", True),
					  ("Online since", "june 15th 2020", True)]
			fields = [("Owner", f"{self.guild.get_member(287969892689379331).mention}", True),
					  ("Highest role", f"{self.guild.get_member(287969892689379331).top_role.mention}", True)]
			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_author(name="Empire", icon_url=self.guild.icon_url)
			embed.set_footer(text="Created by Cretorial")
			embed.set_thumbnail(url="https://i.pinimg.com/originals/8a/18/ef/8a18efc7afe0c21b7002a610054b1d90.png")
			await self.stdout.send(embed=embed)

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			self.ready = True
			print(" bot ready")

		else:
			print("bot reconnected")


	async def on_message(self, message):
		if not message.author.bot:
			await self.process_commands(message)


bot = Bot()