import selfbotv2 as selfbot
import dotenv, time, os

dotenv.load_dotenv("sensitive.env")
bot = selfbot.create_session('Bjarnos', os.environ.get("PASSWORD"))

@bot.event
async def on_ready():
    groups = bot.get_groups()
    user = selfbot.get_profile("JonaZwetsloot")
    for title, item in groups.items():
        if item.is_admin(user):
            print(item.title)

bot.run()