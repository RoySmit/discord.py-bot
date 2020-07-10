from datetime import datetime, timedelta

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")


class Reactions(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.polls = []

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.colours = {
				"💚": self.bot.guild.get_role(724775029690204192), #Buttercup
				"💙": self.bot.guild.get_role(724775287136452609), #Bubbles
				"❤️": self.bot.guild.get_role(724775466149347410), #Blossom
			}
			self.reaction_message = await self.bot.get_channel(722562680858345472).fetch_message(728352040300052530)
			self.startboard_channel = self.bot.get_channel(728764063735087189)
			self.bot.cogs_ready.ready_up("reactions")

	@command (name="poll", aliases=["Poll", "createpoll", "Createpoll"])
	@has_permissions (manage_guild= True)
	async def create_poll(self, ctx, hours: int, question: str, *options):
		if len(options) > 10:
			ctx.send("You can only create a poll consisting of 10 options")

		else:
			embed = Embed(title="Poll",
						  description=question,
						  colour=ctx.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
					  ("Instructions", "React to cast a vote", False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			message = await ctx.send(embed=embed)

			for emoji in numbers[:len(options)]:
				await message.add_reaction(emoji)

			self.polls.append((message.channel.id, message.id))

			self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=hours*3600),
									   args=[message.channel.id, message.id])

	async def complete_poll(self, channel_id, message_id):
		message = await self.bot.get_channel(channel_id).fetch_message(message_id)

		most_voted = max(message.reactions, key=lambda r: r.count)

		await message.channel.send(f"The results are in. option {most_voted.emoji} was most voted for and won with {most_voted.count-1:,} votes")
		self.polls.remove((message.channel.id, message.id))

	@Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.message_id == self.reaction_message.id:
			current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
			await payload.member.remove_roles(*current_colours, reason="Self role")
			await payload.member.add_roles(self.colours[payload.emoji.name], reason="Self role")
			await self.reaction_message.remove_reaction(payload.emoji, payload.member)

		elif payload.message_id in (poll[1] for poll in self.polls):
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

			for reaction in message.reactions:
				if (not payload.member.bot
					and payload.member in await reaction.users().flatten()
					and reaction.emoji != payload.emoji.name):
					await message.remove_reaction(reaction.emoji, payload.member)


		elif payload.emoji.name == "⭐":
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

			if not message.author.bot and payload.member.id != message.author.id:
				msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?",
									  	  message.id) or (None, 0)

				embed = Embed(title="Starred message",
							  colour=message.author.colour,
							  timestamp=datetime.utcnow())

				fields = [("Author", message.author.mention, True),
						  ("Content", message.content or "See attachment", True),
						  ("\u200b", "\u200b", True),
						  ("Stars", stars+1, True)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)
					embed.set_footer(text=f"Starred by {payload.member.display_name}", icon_url=payload.member.avatar_url)

				if len(message.attachments):
					embed.set_image(url=message.attachments[0].url)

				if not stars:
					star_message = await self.startboard_channel.send(embed=embed)
					db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)",
							   message.id, star_message.id)

				else:
					star_message = await self.startboard_channel.fetch_message(msg_id)
					await star_message.edit(embed=embed)
					db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)

			else:
				await message.remove_reaction(payload.emoji, payload.member)

		else:
			for message in self.polls:
				if payload.message_id == message.id:
					for reaction in message.reactions:
						if member in reaction.users and reaction.emoji != payload.emoji:
							await message.remove_reaction(reaction.emoji, member)
					break

def setup(bot):
	bot.add_cog(Reactions(bot))
