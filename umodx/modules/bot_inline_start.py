import logging
import re
import string

from umodx.inline.types import BotInlineMessage
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class BotInlineStartMod(loader.Module):
    """Bot start markazi"""

    strings = {
        "name": "BotInlineStart",       
        "this_is_umodx": (
            "☕ <b>Salom!</b> — Bu <b>«UModx»</b> yuzerboti. Oʻrnatish uchun quyidagi manzillarga oʻting.\n\n"
            '🔥 <a href="https://t.me/umodules_modullar">«UMod» Modullar Guruhi</a>\n'
            '🚨 <a href="https://t.me/umodxbot">«UMod» Qo‘llab-Quvvatlash markazi</a>'
        ),
    }

    async def aiogram_watcher(self, message: BotInlineMessage):
        if message.text != "/start":
            return
        await message.reply(self.strings("this_is_umodx"))
