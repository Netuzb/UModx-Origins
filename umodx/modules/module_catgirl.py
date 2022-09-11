__version__ = (1, 0, 0)
 
#            ▀█▀ █ █ █▀█ █▀▄▀█ ▄▀█ █▀
#             █  █▀█ █▄█ █ ▀ █ █▀█ ▄█  
#             https://t.me/netuzb
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @wilsonmods

import asyncio
import functools
import requests
from telethon.tl.types import Message
from .. import loader, utils

async def photo(nsfw: bool) -> str:
    tag = "not_found"
    while tag == "not_found":
        try:
            img = (
                await utils.run_sync(
                    requests.get, "https://nekos.moe/api/v1/random/image"
                )
            ).json()["images"][0]
        except KeyError:
            await asyncio.sleep(1)
            continue

        tag = (
            "not_found"
            if img["nsfw"] and not nsfw or not img["nsfw"] and nsfw
            else "found"
        )

    return f'https://nekos.moe/image/{img["id"]}.jpg'


@loader.tds
class AnimeCatgirlNekoMod(loader.Module):
    """Anime neko suratlari"""

    strings = {
            "name": "💌 Catgirl",
            "cat_wait": "💌 <b>Iltimos, kuting...</b>",
    }

    async def client_ready(self, client, db):
        self._client = client
    
    async def catcmd(self, message: Message):       
        """> Anime neko suratlar toʻplami"""
        await message.edit(self.strings("cat_wait"))
        await self.inline.gallery(
            caption=lambda: f"💌 <b>Catgirls {utils.ascii_face()}</b>",
            message=message,
            next_handler=functools.partial(
                photo,
                nsfw="nsfw" in utils.get_args_raw(message).lower(),
            ),
            preload=5,
        )
