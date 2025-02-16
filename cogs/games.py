import nextcord
from nextcord.ext import commands
import random

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#
#ROCK PAPER SCISSORS GAME
#
    @commands.command(name="rps", help="Play Rock, Paper, Scissors. Choose one: rock, paper, or scissors.")
    async def rps(self, ctx, player_choice: str):
        # Define the choices
        choices = ["rock", "paper", "scissors"]
        
        # Ensure the player's choice is valid
        player_choice = player_choice.lower()
        if player_choice not in choices:
            await ctx.send("Invalid choice! Please choose 'rock', 'paper', or 'scissors'.")
            return
        
        # Bot makes a random choice
        bot_choice = random.choice(choices)
        
        # Determine the winner
        if player_choice == bot_choice:
            result = "It's a tie!"
        elif (player_choice == "rock" and bot_choice == "scissors") or \
             (player_choice == "paper" and bot_choice == "rock") or \
             (player_choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
        else:
            result = "You lose!"
        
        # Send the result to the channel
        await ctx.send(f"You chose {player_choice}. I chose {bot_choice}. {result}")

            #
            # MAGIC 8 BALL GAME
            #
    @commands.command(name="8ball", help="Ask the magic 8 ball a question.")
    async def eightball(self, ctx, *, question: str):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
            
        # Bot makes a random choice
        response = random.choice(responses)
            
        # Send the response to the channel
        await ctx.send(f"**Question:** {question}\n**Answer:** {response}")

def setup(bot):
    bot.add_cog(GameCommands(bot))