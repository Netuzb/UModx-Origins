import io
import os
from asyncio import sleep

from requests import get
from telethon import events
from telethon import functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

from .. import loader, utils

x = "🔥"

@loader.tds
class DownloaderMod(loader.Module):
    """Downloader module"""

    strings = {"name": "🚨 Downloader"}

    async def dlfilecmd(self, message):
        """File downloader (small files)"""
        await downloading(message)

    async def dlbigfilecmd(self, message):
        """File downloader (big files)"""
        await downloading(message, True)


async def downloading(message, big=False):
    args = utils.get_args_raw(message)
    reply = await message.get_reply_message()
    if not args:
        if not reply:
            await message.edit(f"<b>{x} Hech qanday havola yo'q!</b>")
            return
        message = reply
    else:
        message = message

    if not message.entities:
        await message.edit(f"<b>{x} Hech qanday havola yo'q!</b>")
        return

    urls = []
    for ent in message.entities:
        if type(ent) in [MessageEntityUrl, MessageEntityTextUrl]:
            if type(ent) == MessageEntityUrl:
                offset = ent.offset
                length = ent.length
                url = message.raw_text[offset : offset + length]
            else:
                url = ent.url
            if not url.startswith("http"):
                url = f"<code>http://{url}</code>"
            urls.append(url)

    if not urls:
        await message.edit(f"<b>{x} Hech qanday havola yo'q!</b>")
        return
    for url in urls:
        try:
            await message.edit(f"<b>{x} Yuklab olinmoqda...</b>\n" + url)
            fname = url.split("/")[-1]
            text = get(url, stream=big)
            if big:
                with open(fname, "wb") as f:
                    for chunk in text.iter_content(1024):
                        f.write(chunk)
                await message.edit(f"<b>{x} Yuborilmoqda...</b>\n" + url)
                await message.client.send_file(
                    message.to_id, open(fname, "rb"), reply_to=reply
                )
                os.remove(fname)
            else:
                file = io.BytesIO(text.content)
                file.name = fname
                file.seek(0)
                await message.edit(f"<b>{x} Yuborilmoqda...</b>\n" + url)
                await message.client.send_file(message.to_id, file, reply_to=reply, caption="💌 <b>Tayyor</b>")

        except Exception as e:
            await message.reply(
                "<b>Yuklab olishda xatolik yuz berdi!</b>\n"
                + url
                + "\n<code>"
                + str(e)
                + "</code>"
            )

    await message.delete()
