import discord
from discord.ext import commands

class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = None
        self.current_player = None
        self.next_player = None
        self.game_message = None
        self.players = {}  # Store player's ID

    def print_board(self):
        header = ' '.join(['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣'])  # Column numbers
        board_str = header + '\n' + '\n'.join([' '.join(row) for row in self.board])
        return board_str

    def check_winner(self, player):
    # Horizontal check
        for row in self.board:
            for col in range(4):
                if row[col] == row[col+1] == row[col+2] == row[col+3] == player:
                    return True

        # Vertical check
        for col in range(7):
            for row in range(3):
                if self.board[row][col] == self.board[row+1][col] == self.board[row+2][col] == self.board[row+3][col] == player:
                    return True

        # Diagonal check
        for col in range(4):
            for row in range(3):
                if self.board[row][col] == self.board[row+1][col+1] == self.board[row+2][col+2] == self.board[row+3][col+3] == player:
                    return True
                if self.board[row+3][col] == self.board[row+2][col+1] == self.board[row+1][col+2] == self.board[row][col+3] == player:
                    return True
        return False

    @commands.command()
    async def c4(self, ctx, opponent: commands.MemberConverter):
        self.board = [['⚪']*7 for _ in range(6)]
        self.players['🔴'] = ctx.author.id  # Challenger is red
        self.players['🔵'] = opponent.id  # Challenged is blue
        self.current_player = '🔴'  # Red starts
        self.game_message = await ctx.send(self.print_board())
        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']:
            await self.game_message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user or reaction.message.id != self.game_message.id:
            return

        if user.id != self.players[self.current_player]:
            return
        
        column = int(reaction.emoji[0]) - 1  # Convert emoji to column index
        await self.game_message.remove_reaction(reaction.emoji, user)  # Remove the user's reaction

        # Place the piece in the selected column
        for row in reversed(self.board):
            if row[column] == '⚪':
                row[column] = self.current_player
                break

        # Check for win condition here
        if self.check_winner(self.current_player):
            await self.game_message.edit(content=f"{self.print_board()}\n{self.current_player} wins!")
            return  # End the game
        
        # Switch players
        self.current_player = '🔵' if self.current_player == '🔴' else '🔴'

        # Update the game message
        await self.game_message.edit(content=self.print_board())

async def setup(bot):
    await bot.add_cog(Connect4(bot))