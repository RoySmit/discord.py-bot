from typing import Optional

from datetime import datetime
from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="kick")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "Misbehavior"):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			for target in targets:
				if (ctx.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
					await target.kick(reason=reason)

					embed = Embed(title="Member Kicked",
								  colour=0xDD2222,
								  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", target.display_name, False),
							 ("Actioned by", ctx.author.display_name, False),
							 ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

				else:
					await ctx.send(f"{target.display_name} could not be kicked.")

			await ctx.send("Kick command executed")

	@kick_members.error
	async def kick_members_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("I'm sorry. I don't have the required permissions to execute this command.")

	@command(name="ban")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "Misbehavior"):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			for target in targets:
				if (ctx.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
					await target.ban(reason=reason)

					embed = Embed(title="Member Banned",
								  colour=0xDD2222,
								  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", target.display_name, False),
							 ("Actioned by", ctx.author.display_name, False),
							 ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)
				else:
					await ctx.send(f"{target.display_name} could not be banned.")

			await ctx.send("Ban command executed")

	@ban_members.error
	async def ban_members_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("I'm sorry. I don't have the required permissions to execute this command.")

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(722764410791133234)
			self.bot.cogs_ready.ready_up("mod")


def setup(bot):
	bot.add_cog(Mod(bot))