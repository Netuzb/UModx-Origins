__version__ = (1, 0, 0)
 
#            ▀█▀ █ █ █▀█ █▀▄▀█ ▄▀█ █▀
#             █  █▀█ █▄█ █ ▀ █ █▀█ ▄█  
#             https://t.me/netuzb
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @wilsonmods

import io
import os

from asyncio import sleep
from requests import get
from .. import loader, utils
from telethon import events
from telethon import functions

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

x = "🔥"

@loader.tds
class DlMediaFileMod(loader.Module):
    """Fayllarni havola orqali yuklash moduli"""

    strings = {
        "name": "☕ Downloader",
        "no_link": (
            "<b>{} Hech qanday havola yo'q!</b>"
            ),
        "yuklanmoqda": (
            "<b>{} Yuklab olinmoqda...</b>\n"
            ),
        "yuborilmoqda": (
            "<b>{} Yuborilmoqda...</b>\n"
            ),
        "caption": (
            "💌 <b>Tayyor</b>"
            ),
        }

    async def dlfilecmd(self, message):
        """> Yuklash uchun havola kiriting"""
        await yuklash(self, message)    

async def yuklash(self, message):
    args = utils.get_args_raw(message)
    reply = await message.get_reply_message()
    if not args:
        if not reply:
            await message.edit(self.strings("no_link").format(x)),
            return
        message = reply
    else:
        message = message

    if not message.entities:
        await message.edit(self.strings("no_link").format(x)),
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
        await message.edit(self.strings("no_link").format(x)),
        return
    for url in urls:
        try:
            await message.edit(self.strings("yuklanmoqda").format(x)) + url
            fname = url.split("/")[-1]
            text = get(url, stream=big)
            if big:
                with open(fname, "wb") as f:
                    for chunk in text.iter_content(1024):
                        f.write(chunk)
                await message.edit(self.strings("yuborilmoqda").format(x)) + url
                await message.client.send_file(
                    message.to_id, open(fname, "rb"), reply_to=reply
                )
                os.remove(fname)
            else:
                file = io.BytesIO(text.content)
                file.name = fname
                file.seek(0)
                await message.edit(self.strings("yuborilmoqda").format(x)) + url
                await message.client.send_file(message.to_id, file, reply_to=reply)

        except Exception as e:
            await message.reply(
                "<b>Yuklab olishda xatolik yuz berdi!</b>\n"
                + url
                + "\n<code>"
                + str(e)
                + "</code>"
            )

    await message.delete()
