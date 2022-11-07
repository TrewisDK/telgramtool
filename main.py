from config import api_id, api_hash

import asyncio
from pyrogram import Client

api_id = api_id
api_hash = api_hash


async def parser(chat):
    async with Client("my_account", api_id, api_hash) as app:
        async for member in app.get_chat_members(chat):
            member_is = member.user.username
            print(member_is)
            try:
                with open(f"{chat}_members.txt", "a+") as f:
                    f.write("@" + member_is + "\n")
            except Exception as e:
                continue


async def sender(text):
    async with Client("my_account", api_id, api_hash) as app:
        with open("users_to_spam.txt", "r") as f:
            users = f.readlines()
            limit = 0
            for user in users:
                if limit >= 5:
                    break
                try:
                    await app.send_message(user, text)
                    limit += 1
                except Exception as e:
                    print(e)
                    continue


async def new_first_name(name):
    async with Client("my_account", api_id, api_hash) as app:
        await app.update_profile(first_name=name)


async def new_last_name(name):
    async with Client("my_account", api_id, api_hash) as app:
        await app.update_profile(last_name=name)


async def new_photo():
    async with Client("my_account", api_id, api_hash) as app:
        await app.set_profile_photo(photo="user_photo.jpg")


