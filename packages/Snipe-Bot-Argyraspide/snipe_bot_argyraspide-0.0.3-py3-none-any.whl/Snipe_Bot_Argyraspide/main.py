from twitchAPI.chat import Chat,EventData,ChatMessage,ChatSub,ChatCommand
from twitchAPI.type import AuthScope,ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

import time as tm

import asyncio

from config import CLIENT_ID,CLIENT_SECRET,cooldown

#CLIENT_ID: str = "azzbmgahm4n02w8z6ohmcnnaeug0af"
#CLIENT_SECRET: str = "ck5fk7njrfz58u0orzrqs30dqkkbcx"
#BOT_ID : str = "21734222"
#OWNER_ID : str = "405417781"

# Initialisation du controle anti-spam
last_call=float("inf")

USER_SCOPE = [AuthScope.CHAT_READ,AuthScope.CHAT_EDIT,AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL='snipebot__'

async def on_message(msg: ChatMessage):
    print(f'{msg.user.display_name} - {msg.text}')


async def anti_spamm(last_call):
    print(last_call)
    print(tm.time())
    if abs(last_call - tm.time()) >= 20 :
        return True
    else :
        return False



async def snipe_command(cmd: ChatCommand,):
    global last_call
    if await anti_spamm(last_call) :
        last_call=tm.time()
        for i in range(5,0,-1):
            await cmd.send("---- "+ str(i) + " ----")
            tm.sleep(1)
        await cmd.send("---- GO ! ----")

async def on_ready(ready_event: EventData):

    await ready_event.chat.join_room(TARGET_CHANNEL)

    print("Bot Ready")

async def run_bot():

    bot= await Twitch(CLIENT_ID,CLIENT_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token,USER_SCOPE,refresh_token)

    chat = await Chat(bot)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.register_command('snipe',snipe_command)


    chat.start()

    try:
        input('Press ENTER to stop \\n')
    finally :
        chat.stop()
        await bot.close()

asyncio.run(run_bot())