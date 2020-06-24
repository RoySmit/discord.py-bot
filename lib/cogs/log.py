from datetime import datetime

from discord import Forbidden
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command


class Log(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(722764410791133234)
			self.bot.cogs_ready.ready_up("log")

	@Cog.listener()
	async def on_user_update(self, before, after):
		if before.name != after.name:
			embed = Embed(title="Username change",
						  colour=0xCCCC00,
						  timestamp=datetime.utcnow())

			fields = [("Before", before.name, False),
					  ("After", after.name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_thumbnail(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

		if before.discriminator != after.discriminator:
			embed = Embed(title="Discriminator change",
						  colour=0xCCCC00,
						  timestamp=datetime.utcnow())

			fields = [("Before", before.discriminator, False),
					  ("After", after.discriminator, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_thumbnail(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

		if before.avatar_url != after.avatar_url:
			embed = Embed(title="Avatar update. image below is their new avatar!",
						  colour=0xCCCC00,
						  timestamp=datetime.utcnow())

			embed.set_thumbnail(url=before.avatar_url)
			embed.set_image(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_member_update(self, before, after):
		if before.display_name !=  after.display_name:
			embed = Embed(title="Nickname change",
						  colour=0xCCCC00,
						  timestamp=datetime.utcnow())

			fields = [("Before", before.display_name, False),
					  ("After", after.display_name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_thumbnail(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

		elif before.roles != after.roles:
			embed = Embed(title="Role updates",
	        			  colour=0xCCCC00,
	        			  timestamp=datetime.utcnow())

			if len(after.roles) > len(before.roles):
				embed.add_field(name="Role add", value=set(before.roles).symmetric_difference(after.roles).pop().mention, inline=False)
				embed.set_thumbnail(url=after.avatar_url)

			else:
				embed.add_field(name="Role deleted", value=set(before.roles).symmetric_difference(after.roles).pop().mention, inline=False)
				embed.set_thumbnail(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.author.bot:
			if before.content != after.content:
				embed = Embed(title="Message edit",
							  description=f"Edit by {after.author.display_name}.",
						  	  colour=0xCCCC00,
						  	  timestamp=datetime.utcnow())

			fields = [("Before", before.content, False),
					  ("After", after.content, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_thumbnail(url=after.author.avatar_url)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_delete(self, message):
		if not message.author.bot:
			embed = Embed(title="Message deletion",
						  description=f"Action by {message.author.display_name}.",
						  colour=message.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Content", message.content, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.set_thumbnail(url=message.author.avatar_url)

			if message.content == "": return
			
			await self.log_channel.send(embed=embed)

		



def setup(bot):
	bot.add_cog(Log(bot))