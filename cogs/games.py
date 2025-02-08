import discord
from discord import app_commands
from discord.ext import commands
import random

class Games(app_commands.Group):
    def __init__(self):
        super().__init__(name="game", description="Play different games")

    @app_commands.command(name="guess", description="Play the guessing game")
    async def guess(self, interaction: discord.Interaction):
        number = random.randint(1, 10)
        await interaction.response.send_message("Guess a number between 1 and 10! Type your guess in the chat.")

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.content.isdigit()

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=15)
            guess = int(msg.content)

            if guess == number:
                await interaction.followup.send(f"🎉 Correct! The number was {number}.")
            else:
                await interaction.followup.send(f"❌ Wrong! The correct number was {number}. Try again!")
        except:
            await interaction.followup.send("⏳ Time's up! You didn't guess in time.")

    @app_commands.command(name="rps", description="Play rock-paper-scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice.lower() not in choices:
            await interaction.response.send_message("Invalid choice! Choose rock, paper, or scissors.")
            return

        result = "You win!" if (
                (choice == "rock" and bot_choice == "scissors") or
                (choice == "paper" and bot_choice == "rock") or
                (choice == "scissors" and bot_choice == "paper")
        ) else "You lose!" if choice != bot_choice else "It's a tie!"

        await interaction.response.send_message(f"You chose {choice}, I chose {bot_choice}. {result}")

    @app_commands.command(name="coinflip", description="Flip a coin!")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"The coin landed on {result}!")

    @app_commands.command(name="dice", description="Roll a dice!")
    async def dice(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        await interaction.response.send_message(f"You rolled a {result}!")

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.add_command(Games())  # Register the game group

async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))
