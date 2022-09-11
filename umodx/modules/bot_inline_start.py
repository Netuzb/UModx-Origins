import logging
import re
import string

from umodx.inline.types import BotInlineMessage
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class BotInlineStartMod(loader.Module):
    """Bot start markazi"""

    strings = {
        "name": "NewBot",
        "this_is_umodx": (
            "☕ <b>Salom!</b> — Bu <b>«UModx»</b> yuzerboti. Oʻrnatish uchun quyidagi manzillarga oʻting.\n\n"
            '🔥 <a href="https://t.me/umodules_modullar">«UMod» Modullar Guruhi</a>\n'
            '🚨 <a href="https://t.me/umodxbot">«UMod» Qo‘llab-Quvvatlash markazi</a>'
        ),
    }

    async def watcher(self, message: Message):
        if (
            getattr(message, "out", False)
            and getattr(message, "via_bot_id", False)
            and message.via_bot_id == self.inline.bot_id
            and "This message will be deleted automatically"
            in getattr(message, "raw_text", "")
        ):
            await message.delete()
            return

        if (
            not getattr(message, "out", False)
            or not getattr(message, "via_bot_id", False)
            or message.via_bot_id != self.inline.bot_id
            or "Loading umodx gallery..." not in getattr(message, "raw_text", "")
        ):
            return

        id_ = re.search(r"#id: ([a-zA-Z0-9]+)", message.raw_text)[1]

        await message.delete()

        m = await message.respond("🌘 <b>Opening gallery... wait</b>")

        await self.inline.gallery(
            message=m,
            next_handler=self.inline._custom_map[id_]["handler"],
            caption=self.inline._custom_map[id_].get("caption", ""),
            force_me=self.inline._custom_map[id_].get("force_me", False),
            disable_security=self.inline._custom_map[id_].get(
                "disable_security", False
            ),
        )

    async def _check_bot(self, username: str) -> bool:
        async with self._client.conversation("@BotFather", exclusive=False) as conv:
            try:
                m = await conv.send_message("/token")
            except YouBlockedUserError:
                await self._client(UnblockRequest(id="@BotFather"))
                m = await conv.send_message("/token")

            r = await conv.get_response()

            await m.delete()
            await r.delete()

            if not hasattr(r, "reply_markup") or not hasattr(r.reply_markup, "rows"):
                return False

            for row in r.reply_markup.rows:
                for button in row.buttons:
                    if username != button.text.strip("@"):
                        continue

                    m = await conv.send_message("/cancel")
                    r = await conv.get_response()

                    await m.delete()
                    await r.delete()

                    return True

    async def aiogram_watcher(self, message: Message):
        if message.text != "/start":
            return
        await message.answer_photo(
            "https://te.legra.ph/file/eca95f4035898ee660212.jpg",
            caption=self.strings("this_is_umodx"),
        )
