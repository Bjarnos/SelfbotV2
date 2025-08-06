import selfbotv2 as selfbot
import dotenv, time, os

dotenv.load_dotenv("sensitive.env")
bot = selfbot.create_session('Bjarnos', os.getenv("PASSWORD"))

@bot.event
async def on_ready():
    group = bot.get_group("Cats")
    if group:
        print(group.send_message("test2"))

bot.run()