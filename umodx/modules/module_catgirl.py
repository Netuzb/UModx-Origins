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
            await asyncio.sleep(0.1)
            continue

        tag = (
            "not_found"
            if img["nsfw"] and not nsfw or not img["nsfw"] and nsfw
            else "found"
        )

    return f'https://nekos.moe/image/{img["id"]}.jpg'


@loader.tds
class CatgirlMod(loader.Module):
    """Anime neko suratlari"""

    strings = {"name": "💌 Catgirl"}

    async def client_ready(self, client, db):
        self._client = client
    
    @loader.command
    async def catgirl(self, message):       
        """> Anime neko suratlar toʻplami"""
        await self.inline.gallery(
            caption=lambda: f"💌 <b>Catgirls</b> <b>{utils.ascii_face()}</b>",
            message=message,
            next_handler=functools.partial(
                photo,
                nsfw="nsfw" in utils.get_args_raw(message).lower(),
            ),
            preload=5,
        )
