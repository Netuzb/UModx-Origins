__version__ = (1, 0, 4)

#            ▀█▀ █ █ █▀█  █▀▄▀█ ▄▀█ █▀
#             █  █▀█ █▄█ █ ▀ █ █▀█ ▄█  
#             https://t.me/netuzb
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import datetime
import io
import json
import logging
import time
from telethon.tl.types import Message
from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

# Emoji places 
emoji_white_cube = "◽ "
emoji_main = "😎 "
emoji_corona = "👑 "
emoji_star = "🌟 "
emoji_warn = "🚨 "
emoji_fire = "🔥 "

# UModx start information 
umodx = f"""{emoji_star}<b>«<u>UModx</u>»</b> - zamonaviy qatlamga xush kelibsiz!
{emoji_white_cube}<b>«Maʼlumot oʻrnida»</b> - <u>UModx</u> yangilanishlari sizga bildirishnoma orqali yetib keladi

{emoji_warn} <b>Maʼlumot uchun buyruqlar:</b>
{emoji_white_cube}.um - <b>versiya haqida maʼlumot</b>
{emoji_white_cube}.help - <b>barcha mavjud modullar</b>

{emoji_warn} <b>Inline bot uchun buyruqlar:</b>
{emoji_white_cube}/start - <b>yuzerbot haqida maʼlumot</b>
{emoji_white_cube}/modullar - <b>modullar doʻkoni</b>"""

@loader.tds
class StartHelloMod(loader.Module):
    """Kutib olish markazi"""

    strings = {
        "name": "StartMarkaz",
        "umodx_yopish": emoji_warn + "Postni berkitish",
        "umodx_fed": emoji_corona + "UMod feder.",
        "umodx_fed_url": "https://t.me/umodules",
        "umodx_thomas": emoji_fire + "UMod guruh.",
        "umodx_thomas_url": "https://t.me/wilsonmods",
        "umodx_asosiy_info": umodx + "\n\n<b>Powered by:</b> <a href='https://t.me/netuzb'>Thomas Wilson</a>",        
        "umodx_katta_rahmat": emoji_main + "UMODX tanlagningizga pushaymon boʻlmaysiz!",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        if not self.get("umodx_asosiy_info"):
            await self.inline.bot.send_photo(
                self._tg_id,
                photo="https://te.legra.ph/file/eca95f4035898ee660212.jpg",
                caption=self.strings("umodx_asosiy_info"),
                reply_markup=self.inline.generate_markup(
                    utils.chunks(
                        [{
                            "text": f"{self.strings('umodx_fed')}", 
                            "url": f"{self.strings('umodx_fed_url')}"
                        },{
                            "text": f"{self.strings('umodx_thomas')}", 
                            "url": f"{self.strings('umodx_thomas_url')}"
                        }], 3,
                        )                    
                ),
            )        

        self.handler.start()    

    @loader.loop(interval=1)
    async def handler(self):
        try:
            if not self.get("umodx_asosiy_info"):
                await asyncio.sleep(3)
                return

            if not self.get("umodx_null"):
                self.set("umodx_null", round(time.time()))
                await asyncio.sleep(self.get("umodx_asosiy_info"))
                return

            if self.get("umodx_asosiy_info") == "disabled":
                raise loader.StopLoop

            await asyncio.sleep(
                self.get("umodx_null") + self.get("umodx_asosiy_info") - time.time()
            )

            backup = io.BytesIO(json.dumps(self._db).encode("utf-8"))
            backup.name = "umodx.null"

            await self._client.send_file(
                self._backup_channel,
                backup,
            )
            self.set("umodx_null", round(time.time()))
        except loader.StopLoop:
            raise
        except Exception:
            logger.exception("umodx_null")
            await asyncio.sleep(60)
