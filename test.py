# This is an example script to show how your selfbot can look
import selfbotv2 as selfbot
import dotenv, time, os

dotenv.load_dotenv("sensitive.env")
bot = selfbot.create_session('Bjarnos', os.getenv("PASSWORD"))

@bot.event
async def on_ready():
    print((await bot.user()).username)

bot.run()