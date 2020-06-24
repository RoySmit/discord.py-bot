from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"], brief="Make me say a variaty of the word hello.")
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey','Heya'))} {ctx.author.mention}!")

	@command(name="dice", aliases=["roll"], brief="Roll dices.")
	@cooldown(1, 1, BucketType.user)
	async def roll_dice(self, ctx, die_string: str):
		dice, value = ( int(term) for term in die_string.split("d"))

		if dice <= 25:
			rolls = [randint(1, value) for i in range(dice)]

			await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

		else:
			await ctx.send("The numbers of dice is too high.")

	@command(name="slap", brief="Slap someone.")
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
		await ctx.send(f"{ctx.author.display_name} slaps {member.mention} {reason}")

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("You can't hit a member that doesn't exist baka!")

	@command(name="echo", aliases=["say"], brief="Make me say something.")
	@cooldown(5, 60, BucketType.user)
	async def echo_message(self, ctx, *,message):
		await ctx.message.delete()
		await ctx.send(message)

	@command(name="fact", brief="Gives you some interesting facts about a cat, dog, panda, fox, bird or koala.")
	@cooldown(5, 60, BucketType.user)
	async def animal_fact(self, ctx, animal: str):
		if (animal:= animal.lower()) in("dog", "cat", "panda", "fox", "bird", "koala"):
			fact_url = f"https://some-random-api.ml/facts/{animal}"
			image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

			async with request("GET", image_url, headers={}) as response:
				if response.status == 200:
					data = await response.json()
					image_link = data["link"]

				else:
					image_link = None

			async with request("GET", fact_url, headers={}) as response:
				if response.status == 200:
					data = await response.json()

					embed = Embed(title=f"{animal.title()} fact",
								  description=data["fact"],
								  colour=ctx.author.colour)
					if image_link is not None:
						embed.set_image(url=image_link)
					await ctx.send(embed=embed)

				else:
					await ctx.send(f"API returned a {response.status} status.")

		else:
			await ctx.send("No facts are available for that animal.")
			
	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")


def setup(bot):
	bot.add_cog(Fun(bot))