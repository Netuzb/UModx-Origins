import asyncio
import logging
from ..inline.types import InlineCall, BotInlineMessage
from .. import loader, utils


PRESETS = {
    "wilsonmods": [
        "https://github.com/thomasmod/hikkamods/raw/main/cdeanon.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/atelegraph.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/cmovies.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/cchid.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/crename.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/ctiktok.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/cuploader.py",
        "https://raw.githubusercontent.com/thomasmod/hikkamods/main/kursinfo.py",        
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/mydiary.py",
    ],
    "amoremods": [
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/abstract.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/amoreinfo.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/autoprofile.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/animevoices.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/bull.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/createlinks.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/funquotes.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/hacker.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/imgbb.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/instsave.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/meowvoices.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/mydiary.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/searchpic.py",
        "https://raw.githubusercontent.com/AmoreForever/amoremods/master/telegraphup.py",
    ],
    "fun": [
        "https://mods.hikariatama.ru/aniquotes.py",
        "https://mods.hikariatama.ru/artai.py",
        "https://mods.hikariatama.ru/inline_ghoul.py",
        "https://mods.hikariatama.ru/lovemagic.py",
        "https://mods.hikariatama.ru/mindgame.py",
        "https://mods.hikariatama.ru/moonlove.py",
        "https://mods.hikariatama.ru/neko.py",
        "https://mods.hikariatama.ru/purr.py",
        "https://mods.hikariatama.ru/rpmod.py",
        "https://mods.hikariatama.ru/scrolller.py",
        "https://mods.hikariatama.ru/tictactoe.py",
        "https://mods.hikariatama.ru/trashguy.py",
        "https://mods.hikariatama.ru/truth_or_dare.py",
        "https://mods.hikariatama.ru/sticks.py",
        "https://mods.hikariatama.ru/premium_sticks.py",
        "https://heta.hikariatama.ru/MoriSummerz/ftg-mods/magictext.py",
        "https://heta.hikariatama.ru/HitaloSama/FTG-modules-repo/quotes.py",
        "https://heta.hikariatama.ru/HitaloSama/FTG-modules-repo/spam.py",
        "https://heta.hikariatama.ru/SkillsAngels/Modules/IrisLab.py",
        "https://heta.hikariatama.ru/Fl1yd/FTG-Modules/arts.py",
        "https://heta.hikariatama.ru/SkillsAngels/Modules/Complements.py",
        "https://heta.hikariatama.ru/Den4ikSuperOstryyPer4ik/Astro-modules/Compliments.py",
        "https://heta.hikariatama.ru/vsecoder/hikka_modules/mazemod.py",
    ],
    "chat": [
        "https://mods.hikariatama.ru/activists.py",
        "https://mods.hikariatama.ru/banstickers.py",
        "https://mods.hikariatama.ru/hikarichat.py",
        "https://mods.hikariatama.ru/inactive.py",
        "https://mods.hikariatama.ru/keyword.py",
        "https://mods.hikariatama.ru/tagall.py",
        "https://mods.hikariatama.ru/voicechat.py",
        "https://mods.hikariatama.ru/vtt.py",
        "https://heta.hikariatama.ru/SekaiYoneya/Friendly-telegram/BanMedia.py",
        "https://heta.hikariatama.ru/iamnalinor/FTG-modules/swmute.py",
        "https://heta.hikariatama.ru/GeekTG/FTG-Modules/filter.py",
    ],
    "service": [
        "https://mods.hikariatama.ru/account_switcher.py",
        "https://mods.hikariatama.ru/surl.py",
        "https://mods.hikariatama.ru/httpsc.py",
        "https://mods.hikariatama.ru/img2pdf.py",
        "https://mods.hikariatama.ru/latex.py",
        "https://mods.hikariatama.ru/pollplot.py",
        "https://mods.hikariatama.ru/sticks.py",
        "https://mods.hikariatama.ru/temp_chat.py",
        "https://mods.hikariatama.ru/vtt.py",
        "https://heta.hikariatama.ru/vsecoder/hikka_modules/accounttime.py",
        "https://heta.hikariatama.ru/vsecoder/hikka_modules/searx.py",
        "https://heta.hikariatama.ru/iamnalinor/FTG-modules/swmute.py",
    ],
    "downloaders": [
        "https://mods.hikariatama.ru/musicdl.py",
        "https://mods.hikariatama.ru/uploader.py",
        "https://mods.hikariatama.ru/porn.py",
        "https://mods.hikariatama.ru/web2file.py",
        "https://heta.hikariatama.ru/AmoreForever/amoremods/instsave.py",
        "https://heta.hikariatama.ru/CakesTwix/Hikka-Modules/tikcock.py",
        "https://heta.hikariatama.ru/CakesTwix/Hikka-Modules/InlineYouTube.py",
        "https://heta.hikariatama.ru/CakesTwix/Hikka-Modules/InlineSpotifyDownloader.py",
        "https://heta.hikariatama.ru/GeekTG/FTG-Modules/downloader.py",
        "https://heta.hikariatama.ru/Den4ikSuperOstryyPer4ik/Astro-modules/dl_yt_previews.py",
    ],
}

@loader.tds
class ThomPresets(loader.Module):
    """Modullar jamlangan bepul doʻkon"""

    strings = {
        "name": "ThomPresets",
        "_wilsonmods_title": "🔥 Thomas modullar",
        "_wilsonmods_desc": "«UModx» yaratuvchisining rasmiy modullari quyida joylashgan",
        "_amoremods_title": "☕ AmoreForever modullar",
        "_amoremods_desc": "Fazliddin‘ boshchiligida tuzilgan rasmiy modullari",
        "_fun_title": "🪩 Ko‘ngilochar modullar",
        "_fun_desc": "Fun modules — animations, spam, entertainment, etc.",
        "_chat_title": "👥 Guruh ma‘muriyati yordamchilari",
        "_chat_desc": (
            "The collection of tools which will help to moderate your group chat —"
            " filters, notes, voice recognition, etc."
        ),
        "_service_title": "⚙️ Foydali modullar",
        "_service_desc": (
            "Really useful modules — account management, link shortener, search engine,"
            " etc."
        ),
        "_downloaders_title": "📥 Yuklab oluvchilar",
        "_downloaders_desc": (
            "The collection of tools which will help you download/upload files from/to"
            " different sources — YouTube, TikTok, Instagram, Spotify, VK Music, etc."
        ),
        "welcome": "🌟 Salom! Bu <b>«UModx»</b> modullar doʻkoni",
        "preset": (
            "<b>{}:</b>\n🚨 <b>Info:</b> <i>{}</i>\n\n🗃️ <b>Ushbu katalogdagi modullar:</b>\n\n{}"
        ),    
        "installing": (
            "<emoji document_id='5451732530048802485'>⏳</emoji> <b>Hozirgi vaqtda"
            " </b><code>{}</code> modullari o'rnatilmoqda <b>...</b>"
        ),
        "installing_module": (
            "<emoji document_id='5451732530048802485'>⏳</emoji> <b>Hozirgi vaqtda..."
            " </b><code>{}</code><b> ({}/{} modul oʻrnatildi)...</b>\n\n<emoji"
            " document_id='5235816140302721259'>👑</emoji> <i>"
            " {}...</i>"
        ),
        "installed": (
            "<emoji document_id='5235816140302721259'>👑</emoji> <b>Barcha"
            " </b><code>{}</code><b> modullari oʻrnatildi!</b>"
        ),
        "back": "↩️ Orqaga",
        "install": "💾️ O'rnatish",
        "already_installed": "✅ [Oʻrnatildi]",
    }

    async def client_ready(self):
        self._markup = utils.chunks(
            [
                {
                    "text": self.strings(f"_{preset}_title"),
                    "callback": self._preset,
                    "args": (preset,),
                }
                for preset in PRESETS
            ],
            1,
        )

        if self.get("sent"):
            return

        self.set("sent", True)

        await self._menu()

    async def _menu(self):
        await self.inline.bot.send_message(
            self._client.tg_id,
            self.strings("welcome"),
            reply_markup=self.inline.generate_markup(self._markup),
        )

    async def _back(self, call: InlineCall):
        await call.edit(self.strings("welcome"), reply_markup=self._markup)

    async def _install(self, call: InlineCall, preset: str):
        await call.delete()
        m = await self._client.send_message(
            self.inline.bot_id, self.strings("installing").format(preset)
        )
        for i, module in enumerate(PRESETS[preset]):
            await m.edit(
                self.strings("installing_module").format(
                    preset, i, len(PRESETS[preset]), module
                )
            )
            await self.lookup("loader").download_and_install(module, None)
            await asyncio.sleep(1)

        if self.lookup("loader")._fully_loaded:
            self.lookup("loader")._update_modules_in_db()

        await m.edit(self.strings("installed").format(preset))
        await self._menu()

    def _is_installed(self, link: str) -> bool:
        return any(
            link.strip().lower() == installed.strip().lower()
            for installed in self.lookup("loader").get("loaded_modules", {}).values()
        )

    async def _preset(self, call: InlineCall, preset: str):
        await call.edit(
            self.strings("preset").format(
                self.strings(f"_{preset}_title"),
                self.strings(f"_{preset}_desc"),
                "\n".join(
                    map(
                        lambda x: x[0],
                        sorted(
                            [
                                (
                                    f"{self.strings('already_installed') if self._is_installed(link) else '▫️'} <b>{link.rsplit('/', maxsplit=1)[1].split('.')[0]}</b>",
                                    int(self._is_installed(link)),
                                )
                                for link in PRESETS[preset]
                            ],
                            key=lambda x: x[1],
                            reverse=True,
                        ),
                    )
                ),
            ),
            reply_markup=[
                {"text": self.strings("back"), "callback": self._back},
                {
                    "text": self.strings("install"),
                    "callback": self._install,
                    "args": (preset,),
                },
            ],
        )

    async def aiogram_watcher(self, message: BotInlineMessage):
        if message.text != "/modullar" or message.from_user.id != self._client.tg_id:
            return

        await self._menu()
