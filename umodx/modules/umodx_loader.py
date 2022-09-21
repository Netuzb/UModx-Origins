"""Loads and registers modules"""

import asyncio
import contextlib
import copy
import functools
import importlib
import inspect
import logging
import os
import re
import ast
import sys
import time
import uuid
from collections import ChainMap
from importlib.machinery import ModuleSpec
from typing import Optional, Union
from urllib.parse import urlparse

import requests
import telethon
from telethon.tl.types import Message, Channel
from telethon.tl.functions.channels import JoinChannelRequest

from .. import loader, main, utils
from ..compat import geek
from ..inline.types import InlineCall
from ..types import CoreOverwriteError, CoreUnloadError

logger = logging.getLogger(__name__)


@loader.tds
class LoaderMod(loader.Module):
    """Loads modules"""

    strings = {
        "name": "Loader",
        "repo_config_doc": "URL to a module repo",
        "avail_header": (
            "<emoji document_id='6321352876505434037'>🎢</emoji><b> Modules"
            " from repo</b>"
        ),
        "select_preset": "<b>⚠️ Please select a preset</b>",
        "no_preset": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Preset not found</b>"
        ),
        "preset_loaded": (
            "<emoji document_id='6323332130579416910'>✅</emoji><b> Preset loaded</b>"
        ),
        "no_module": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Module not available"
            " in repo.</b>"
        ),
        "no_file": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> File not found</b>"
        ),
        "provide_module": "<b>⚠️ Provide a module to load</b>",
        "bad_unicode": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Invalid Unicode"
            " formatting in module</b>"
        ),
        "load_failed": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Loading failed. See"
            " logs for details</b>"
        ),
        "loaded": (
            "<emoji document_id='5188377234380954537'>🌘</emoji><b> Module"
            " </b><code>{}</code>{}<b> loaded {}</b>{}{}{}{}{}{}"
        ),
        "no_class": "<b>What class needs to be unloaded?</b>",
        "unloaded": (
            "<emoji document_id='5469654973308476699'>💣</emoji><b> Module {}"
            " unloaded.</b>"
        ),
        "not_unloaded": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Module not"
            " unloaded.</b>"
        ),
        "requirements_failed": (
            "<emoji document_id='5375201396859607943'>🚫</emoji><b> Requirements"
            " installation failed</b>"
        ),
        "requirements_failed_termux": (
            "<emoji document_id='5386399931378440814'>🕶</emoji> <b>Requirements"
            " installation failed</b>\n<b>The most common reason is that Termux doesn't"
            " support many libraries. Don't report it as bug, this can't be solved.</b>"
        ),
        "heroku_install_failed": (
            "♓️⚠️ <b>This module requires additional libraries to be installed, which"
            " can't be done on Heroku. Don't report it as bug, this can't be"
            " solved.</b>"
        ),
        "requirements_installing": (
            "<emoji document_id='5445284980978621387'>🚀</emoji><b> Installing"
            " requirements:\n\n{}</b>"
        ),
        "requirements_restart": (
            "<emoji document_id='5445284980978621387'>🚀</emoji><b> Requirements"
            " installed, but a restart is required for </b><code>{}</code><b> to"
            " apply</b>"
        ),
        "all_modules_deleted": (
            "<emoji document_id='6323332130579416910'>✅</emoji><b> All modules"
            " deleted</b>"
        ),
        "single_cmd": "\n📌 <b>{}{}</b> {}",
        "undoc_cmd": "🦥 No docs",
        "ihandler": "\n🍁 <b>{}</b> {}",
        "undoc_ihandler": "🦥 No docs",
        "inline_init_failed": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>This module requires"
            " umodx inline feature and initialization of InlineManager"
            " failed</b>\n<i>Please, remove one of your old bots from @BotFather and"
            " restart userbot to load this module</i>"
        ),
        "version_incompatible": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>This module requires"
            " umodx {}+\nPlease, update with </b><code>.update</code>"
        ),
        "ffmpeg_required": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>This module requires"
            " FFMPEG, which is not installed</b>"
        ),
        "developer": (
            "\n\n<emoji document_id='5431376038628171216'>👨‍💻</emoji> <b>Developer:"
            " </b>{}"
        ),
        "depends_from": (
            "\n\n<emoji document_id='5431736674147114227'>📦</emoji> <b>Dependencies:"
            " </b>\n{}"
        ),
        "by": "by",
        "module_fs": (
            "💿 <b>Would you like to save this module to filesystem, so it won't get"
            " unloaded after restart?</b>"
        ),
        "save": "💿 Saqlash",
        "no_save": "🚫 Kerakmas",
        "save_for_all": "💽 Har vaqt saqlash",
        "never_save": "🚫 Hechqachon saqlamaslik",
        "will_save_fs": (
            "💽 Now all modules, loaded with .loadmod will be saved to filesystem"
        ),
        "add_repo_config_doc": "Additional repos to load from",
        "share_link_doc": "Share module link in result message of .dlmod",
        "modlink": (
            "\n\n<emoji document_id='6037284117505116849'>🌐</emoji> <b>Manzil havolasi:"
            " </b><code>{}</code>"
        ),
        "blob_link": (
            "\n🚸 <b>Do not use `blob` links to download modules. Consider switching to"
            " `raw` instead</b>"
        ),
        "suggest_subscribe": (
            "\n\n<emoji document_id='5456129670321806826'>⭐️</emoji><b>This module is"
            " made by {}. Do you want to join this channel to support developer?</b>"
        ),
        "subscribe": "💬 Obuna boʻlish",
        "no_subscribe": "🚫 Shart emas",
        "subscribed": "💬 Obuna boʻldingiz",
        "not_subscribed": "🚫 I will no longer suggest subscribing to this channel",
        "confirm_clearmodules":  (
            "🚨 Siz haqiqatdan ham <b>barcha modullarni<b>"
            " oʻchirib yuborishni hoxlaysizmi?\n"
            " – <i>Keyinchalik ularni tiklab boʻlmaydi!</i>"
            ),
        "clearmodules": "🗑 Ha, oʻchirish",
        "cancel": "🚫 Bekor qilish",
        "overwrite_module": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>This module"
            " attempted to override the core one (</b><code>{}</code><b>)</b>\n\n<emoji"
            " document_id='5472146462362048818'>💡</emoji><i> Don't report it as bug."
            " It's a security measure to prevent replacing core modules with some"
            " junk</i>"
        ),
        "overwrite_command": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>This module"
            " attempted to override the core command"
            " (</b><code>{}{}</code><b>)</b>\n\n<emoji"
            " document_id='5472146462362048818'>💡</emoji><i> Don't report it as bug."
            " It's a security measure to prevent replacing core modules' commands with"
            " some junk</i>"
        ),
        "unload_core": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>You can't unload"
            " core module </b><code>{}</code><b></b>\n\n<emoji"
            " document_id='5472146462362048818'>💡</emoji><i> Don't report it as bug."
            " It's a security measure to prevent replacing core modules with some"
            " junk</i>"
        ),
        "cannot_unload_lib": (
            "<emoji document_id='5454225457916420314'>😖</emoji> <b>You can't unload"
            " library</b>"
        ),
        "wait_channel_approve": (
            "<emoji document_id='5469741319330996757'>💫</emoji> <b>Module"
            " </b><code>{}</code><b> requests permission to join channel <a"
            ' href="https://t.me/{}">{}</a>.\n\n<b><emoji'
            ' document_id="5467666648263564704">❓</emoji> Reason: {}</b>\n\n<i>Waiting'
            ' for <a href="https://t.me/{}">approval</a>...</i>'
        ),
    }

  
    _fully_loaded = False
    _links_cache = {}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "MODULES_REPO",
                "https://mods.hikariatama.ru",
                lambda: self.strings("repo_config_doc"),
                validator=loader.validators.Link(),
            ),
            loader.ConfigValue(
                "ADDITIONAL_REPOS",
                # Currenly the trusted developers are specified
                [
                    "https://github.com/thomasmod/hikkamods/raw/main",
                    "https://github.com/hikariatama/host/raw/master",
                    "https://github.com/MoriSummerz/ftg-mods/raw/main",
                    "https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master",
                ],
                lambda: self.strings("add_repo_config_doc"),
                validator=loader.validators.Series(validator=loader.validators.Link()),
            ),
            loader.ConfigValue(
                "share_link",
                doc=lambda: self.strings("share_link_doc"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        self.allmodules.add_aliases(self.lookup("settings").get("aliases", {}))

        main.umodx.ready.set()

        asyncio.ensure_future(self._update_modules())
        asyncio.ensure_future(self.get_repo_list("full"))
        self._react_queue = []

    @loader.loop(interval=120, autostart=True)
    async def _react_processor(self):
        if not self._react_queue:
            return

        developer_entity, modname = self._react_queue.pop(0)
        try:
            await (
                await self._client.get_messages(
                    developer_entity, limit=1, search=modname
                )
            )[0].react("❤️")
            self.set(
                "reacted",
                self.get("reacted", []) + [f"{developer_entity.id}/{modname}"],
            )
        except Exception:
            logger.debug(f"Unable to react to {developer_entity.id} about {modname}")

    @loader.loop(interval=3, wait_before=True, autostart=True)
    async def _config_autosaver(self):
        for mod in self.allmodules.modules:
            if (
                not hasattr(mod, "config")
                or not mod.config
                or not isinstance(mod.config, loader.ModuleConfig)
            ):
                continue

            for option, config in mod.config._config.items():
                if not hasattr(config, "_save_marker"):
                    continue

                delattr(mod.config._config[option], "_save_marker")
                self._db.setdefault(mod.__class__.__name__, {}).setdefault(
                    "__config__", {}
                )[option] = config.value

        for lib in self.allmodules.libraries:
            if (
                not hasattr(lib, "config")
                or not lib.config
                or not isinstance(lib.config, loader.ModuleConfig)
            ):
                continue

            for option, config in lib.config._config.items():
                if not hasattr(config, "_save_marker"):
                    continue

                delattr(lib.config._config[option], "_save_marker")
                self._db.setdefault(lib.__class__.__name__, {}).setdefault(
                    "__config__", {}
                )[option] = config.value

        self._db.save()

    def _update_modules_in_db(self):
        if self.allmodules.secure_boot:
            return

        self.set(
            "loaded_modules",
            {
                module.__class__.__name__: module.__origin__
                for module in self.allmodules.modules
                if module.__origin__.startswith("http")
            },
        )

    @loader.owner
    @loader.command(ru_doc="Загрузить модуль из официального репозитория")
    async def dlmod(self, message: Message):
        """Install a module from the official module repo"""
        if args := utils.get_args(message):
            args = args[0]

            await self.download_and_install(args, message)
            if self._fully_loaded:
                self._update_modules_in_db()
        else:
            await self.inline.list(
                message,
                [
                    self.strings("avail_header")
                    + f"\n☁️ {repo.strip('/')}\n\n"
                    + "\n".join(
                        [
                            " | ".join(chunk)
                            for chunk in utils.chunks(
                                [
                                    f"<code>{i}</code>"
                                    for i in sorted(
                                        [
                                            utils.escape_html(
                                                i.split("/")[-1].split(".")[0]
                                            )
                                            for i in mods.values()
                                        ]
                                    )
                                ],
                                5,
                            )
                        ]
                    )
                    for repo, mods in (await self.get_repo_list("full")).items()
                ],
            )

    @loader.owner
    @loader.command(ru_doc="Установить пресет модулей")
    async def dlpreset(self, message: Message):
        """Set modules preset"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("select_preset"))
            return

        await self.get_repo_list(args[0])
        self.set("chosen_preset", args[0])

        await utils.answer(message, self.strings("preset_loaded"))
        await self.allmodules.commands["restart"](
            await message.reply(f"{self.get_prefix()}restart --force")
        )

    async def _get_modules_to_load(self):
        preset = self.get("chosen_preset")

        if preset != "disable":
            possible_mods = (
                await self.get_repo_list(preset, only_primary=True)
            ).values()
            todo = dict(ChainMap(*possible_mods))
        else:
            todo = {}

        todo.update(**self.get("loaded_modules", {}))
        logger.debug(f"Loading modules: {todo}")
        return todo

    async def _get_repo(self, repo: str, preset: str) -> str:
        repo = repo.strip("/")
        preset_id = f"{repo}/{preset}"

        if self._links_cache.get(preset_id, {}).get("exp", 0) >= time.time():
            return self._links_cache[preset_id]["data"]

        res = await utils.run_sync(
            requests.get,
            f"{repo}/{preset}.txt",
        )

        if not str(res.status_code).startswith("2"):
            logger.debug(f"Can't load {repo=}, {preset=}, {res.status_code=}")
            return []

        self._links_cache[preset_id] = {
            "exp": time.time() + 5 * 60,
            "data": [link for link in res.text.strip().splitlines() if link],
        }

        return self._links_cache[preset_id]["data"]

    async def get_repo_list(
        self,
        preset: Optional[str] = None,
        only_primary: Optional[bool] = False,
    ) -> dict:
        if preset is None or preset == "none":
            preset = "minimal"

        return {
            repo: {
                f"Mod/{repo_id}/{i}": f'{repo.strip("/")}/{link}.py'
                for i, link in enumerate(set(await self._get_repo(repo, preset)))
            }
            for repo_id, repo in enumerate(
                [self.config["MODULES_REPO"]]
                + ([] if only_primary else self.config["ADDITIONAL_REPOS"])
            )
            if repo.startswith("http")
        }

    async def get_links_list(self):
        def converter(repo_dict: dict) -> list:
            return list(dict(ChainMap(*list(repo_dict.values()))).values())

        links = await self.get_repo_list("full")
        # Make `MODULES_REPO` primary one
        main_repo = list(links[self.config["MODULES_REPO"]].values())
        del links[self.config["MODULES_REPO"]]
        return main_repo + converter(links)

    async def _find_link(self, module_name: str) -> Union[str, bool]:
        links = await self.get_links_list()
        return next(
            (
                link
                for link in links
                if link.lower().endswith(f"/{module_name.lower()}.py")
            ),
            False,
        )

    async def download_and_install(
        self,
        module_name: str,
        message: Optional[Message] = None,
    ):
        try:
            blob_link = False
            module_name = module_name.strip()
            if urlparse(module_name).netloc:
                url = module_name
                if re.match(
                    r"^(https:\/\/github\.com\/.*?\/.*?\/blob\/.*\.py)|"
                    r"(https:\/\/gitlab\.com\/.*?\/.*?\/-\/blob\/.*\.py)$",
                    url,
                ):
                    url = url.replace("/blob/", "/raw/")
                    blob_link = True
            else:
                url = await self._find_link(module_name)

                if not url:
                    if message is not None:
                        await utils.answer(message, self.strings("no_module"))

                    return False

            r = await utils.run_sync(requests.get, url)

            if r.status_code == 404:
                if message is not None:
                    await utils.answer(message, self.strings("no_module"))

                return False

            r.raise_for_status()

            return await self.load_module(
                r.content.decode("utf-8"),
                message,
                module_name,
                url,
                blob_link=blob_link,
            )
        except Exception:
            logger.exception(f"Failed to load {module_name}")

    async def _inline__load(
        self,
        call: InlineCall,
        doc: str,
        path_: Optional[str],
        mode: str,
    ):
        save = False
        if mode == "all_yes":
            self._db.set(main.__name__, "permanent_modules_fs", True)
            self._db.set(main.__name__, "disable_modules_fs", False)
            await call.answer(self.strings("will_save_fs"))
            save = True
        elif mode == "all_no":
            self._db.set(main.__name__, "disable_modules_fs", True)
            self._db.set(main.__name__, "permanent_modules_fs", False)
        elif mode == "once":
            save = True

        await self.load_module(doc, call, origin=path_ or "<string>", save_fs=save)

    @loader.owner
    @loader.command(ru_doc="Загрузить модуль из файла")
    async def loadmod(self, message: Message):
        """Loads the module file"""
        msg = message if message.file else (await message.get_reply_message())

        if msg is None or msg.media is None:
            if args := utils.get_args(message):
                try:
                    path_ = args[0]
                    with open(path_, "rb") as f:
                        doc = f.read()
                except FileNotFoundError:
                    await utils.answer(message, self.strings("no_file"))
                    return
            else:
                await utils.answer(message, self.strings("provide_module"))
                return
        else:
            path_ = None
            doc = await msg.download_media(bytes)

        logger.debug("Loading external module...")

        try:
            doc = doc.decode("utf-8")
        except UnicodeDecodeError:
            await utils.answer(message, self.strings("bad_unicode"))
            return

        if (
            not self._db.get(
                main.__name__,
                "disable_modules_fs",
                False,
            )
            and not self._db.get(main.__name__, "permanent_modules_fs", False)
            and "DYNO" not in os.environ
        ):
            if message.file:
                await message.edit("")
                message = await message.respond("🌘")

            if await self.inline.form(
                self.strings("module_fs"),
                message=message,
                reply_markup=[
                    [
                        {
                            "text": self.strings("save"),
                            "callback": self._inline__load,
                            "args": (doc, path_, "once"),
                        },
                        {
                            "text": self.strings("no_save"),
                            "callback": self._inline__load,
                            "args": (doc, path_, "no"),
                        },
                    ],
                    [
                        {
                            "text": self.strings("save_for_all"),
                            "callback": self._inline__load,
                            "args": (doc, path_, "all_yes"),
                        }
                    ],
                    [
                        {
                            "text": self.strings("never_save"),
                            "callback": self._inline__load,
                            "args": (doc, path_, "all_no"),
                        }
                    ],
                ],
            ):
                return

        if path_ is not None:
            await self.load_module(
                doc,
                message,
                origin=path_,
                save_fs=self._db.get(main.__name__, "permanent_modules_fs", False)
                and not self._db.get(main.__name__, "disable_modules_fs", False),
            )
        else:
            await self.load_module(
                doc,
                message,
                save_fs=self._db.get(main.__name__, "permanent_modules_fs", False)
                and not self._db.get(main.__name__, "disable_modules_fs", False),
            )

    async def _send_stats(self, url: str, retry: bool = False):
        """Send anonymous stats to umodx"""
        try:
            if not self.get("token"):
                self.set(
                    "token",
                    (
                        await (await self._client.get_messages("@umodx_ub", ids=[10]))[
                            0
                        ].click(0)
                    ).message,
                )

            res = await utils.run_sync(
                requests.post,
                "https://heta.hikariatama.ru/stats",
                data={"url": url},
                headers={"X-umodx-Token": self.get("token")},
            )

            if res.status_code == 403:
                if retry:
                    return

                self.set("token", None)
                return await self._send_stats(url, retry=True)
        except Exception:
            logger.debug("Failed to send stats", exc_info=True)

    async def load_module(
        self,
        doc: str,
        message: Message,
        name: Optional[Union[str, None]] = None,
        origin: Optional[str] = "<string>",
        did_requirements: Optional[bool] = False,
        save_fs: Optional[bool] = False,
        blob_link: Optional[bool] = False,
    ):
        if any(
            line.replace(" ", "") == "#scope:ffmpeg" for line in doc.splitlines()
        ) and os.system("ffmpeg -version 1>/dev/null 2>/dev/null"):
            if isinstance(message, Message):
                await utils.answer(message, self.strings("ffmpeg_required"))
            return

        if (
            any(line.replace(" ", "") == "#scope:inline" for line in doc.splitlines())
            and not self.inline.init_complete
        ):
            if isinstance(message, Message):
                await utils.answer(message, self.strings("inline_init_failed"))
            return

        if re.search(r"# ?scope: ?umodx_min", doc):
            ver = re.search(r"# ?scope: ?umodx_min ((\d+\.){2}\d+)", doc).group(1)
            ver_ = tuple(map(int, ver.split(".")))
            if main.__version__ < ver_:
                if isinstance(message, Message):
                    if getattr(message, "file", None):
                        m = utils.get_chat_id(message)
                        await message.edit("")
                    else:
                        m = message

                    await self.inline.form(
                        self.strings("version_incompatible").format(ver),
                        m,
                        reply_markup=[
                            {
                                "text": self.lookup("updater").strings("btn_update"),
                                "callback": self.lookup("updater").inline_update,
                            },
                            {
                                "text": self.lookup("updater").strings("cancel"),
                                "action": "close",
                            },
                        ],
                    )
                return

        developer = re.search(r"# ?meta developer: ?(.+)", doc)
        developer = developer.group(1) if developer else False

        blob_link = self.strings("blob_link") if blob_link else ""

        if utils.check_url(name):
            url = copy.deepcopy(name)
        elif utils.check_url(origin):
            url = copy.deepcopy(origin)
        else:
            url = None

        if name is None:
            try:
                node = ast.parse(doc)
                uid = next(n.name for n in node.body if isinstance(n, ast.ClassDef))
            except Exception:
                logger.debug(
                    "Can't parse classname from code, using legacy uid instead",
                    exc_info=True,
                )
                uid = "__extmod_" + str(uuid.uuid4())
        else:
            if name.startswith(self.config["MODULES_REPO"]):
                name = name.split("/")[-1].split(".py")[0]

            uid = name.replace("%", "%%").replace(".", "%d")

        module_name = f"umodx.modules.{uid}"

        doc = geek.compat(doc)

        async def core_overwrite(e: CoreOverwriteError):
            nonlocal message

            with contextlib.suppress(Exception):
                self.allmodules.modules.remove(instance)

            if not message:
                return

            await utils.answer(
                message,
                self.strings(f"overwrite_{e.type}").format(
                    *(e.target,)
                    if e.type == "module"
                    else (self.get_prefix(), e.target)
                ),
            )

        try:
            try:
                spec = ModuleSpec(
                    module_name,
                    loader.StringLoader(
                        doc, f"<string {uid}>" if origin == "<string>" else origin
                    ),
                    origin=f"<string {uid}>" if origin == "<string>" else origin,
                )
                instance = await self.allmodules.register_module(
                    spec,
                    module_name,
                    origin,
                    save_fs=save_fs,
                )
            except ImportError as e:
                logger.info(
                    "Module loading failed, attemping dependency installation"
                    f" ({e.name})"
                )
                # Let's try to reinstall dependencies
                try:
                    requirements = list(
                        filter(
                            lambda x: not x.startswith(("-", "_", ".")),
                            map(
                                str.strip,
                                loader.VALID_PIP_PACKAGES.search(doc)[1].split(),
                            ),
                        )
                    )
                except TypeError:
                    logger.warning(
                        "No valid pip packages specified in code, attemping"
                        " installation from error"
                    )
                    requirements = [e.name]

                logger.debug(f"Installing requirements: {requirements}")

                if not requirements:
                    raise Exception("Nothing to install") from e

                if did_requirements:
                    if message is not None:
                        if "DYNO" in os.environ:
                            await utils.answer(
                                message,
                                self.strings("heroku_install_failed"),
                            )
                        else:
                            await utils.answer(
                                message,
                                self.strings("requirements_restart").format(e.name),
                            )

                    return

                if message is not None:
                    await utils.answer(
                        message,
                        self.strings("requirements_installing").format(
                            "\n".join(f"▫️ {req}" for req in requirements)
                        ),
                    )

                pip = await asyncio.create_subprocess_exec(
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "-q",
                    "--disable-pip-version-check",
                    "--no-warn-script-location",
                    *["--user"] if loader.USER_INSTALL else [],
                    *requirements,
                )

                rc = await pip.wait()

                if rc != 0:
                    if message is not None:
                        if "com.termux" in os.environ.get("PREFIX", ""):
                            await utils.answer(
                                message,
                                self.strings("requirements_failed_termux"),
                            )
                        else:
                            await utils.answer(
                                message,
                                self.strings("requirements_failed"),
                            )

                    return

                importlib.invalidate_caches()

                kwargs = utils.get_kwargs()
                kwargs["did_requirements"] = True

                return await self.load_module(**kwargs)  # Try again
            except loader.LoadError as e:
                with contextlib.suppress(Exception):
                    await self.allmodules.unload_module(instance.__class__.__name__)

                with contextlib.suppress(Exception):
                    self.allmodules.modules.remove(instance)

                if message:
                    await utils.answer(
                        message,
                        "<emoji document_id='5454225457916420314'>😖</emoji>"
                        f" <b>{utils.escape_html(str(e))}</b>",
                    )
                return
            except CoreOverwriteError as e:
                await core_overwrite(e)
                return
        except BaseException as e:
            logger.exception(f"Loading external module failed due to {e}")

            if message is not None:
                await utils.answer(message, self.strings("load_failed"))

            return

        instance.inline = self.inline

        if hasattr(instance, "__version__") and isinstance(instance.__version__, tuple):
            version = (
                "<b><i>"
                f" (v{'.'.join(list(map(str, list(instance.__version__))))})</i></b>"
            )
        else:
            version = ""

        try:
            try:
                self.allmodules.send_config_one(instance)

                async def inner_proxy():
                    nonlocal instance, message
                    while True:
                        if hasattr(instance, "umodx_wait_channel_approve"):
                            if message:
                                (
                                    module,
                                    channel,
                                    reason,
                                ) = instance.umodx_wait_channel_approve
                                message = await utils.answer(
                                    message,
                                    self.strings("wait_channel_approve").format(
                                        module,
                                        channel.username,
                                        utils.escape_html(channel.title),
                                        utils.escape_html(reason),
                                        self.inline.bot_username,
                                    ),
                                )
                                return

                        await asyncio.sleep(0.1)

                task = asyncio.ensure_future(inner_proxy())
                await self.allmodules.send_ready_one(
                    instance,
                    no_self_unload=True,
                    from_dlmod=bool(message),
                )
                task.cancel()
            except loader.LoadError as e:
                with contextlib.suppress(Exception):
                    await self.allmodules.unload_module(instance.__class__.__name__)

                with contextlib.suppress(Exception):
                    self.allmodules.modules.remove(instance)

                if message:
                    await utils.answer(
                        message,
                        "<emoji document_id='5454225457916420314'>😖</emoji>"
                        f" <b>{utils.escape_html(str(e))}</b>",
                    )
                return
            except loader.SelfUnload as e:
                logging.debug(f"Unloading {instance}, because it raised `SelfUnload`")
                with contextlib.suppress(Exception):
                    await self.allmodules.unload_module(instance.__class__.__name__)

                with contextlib.suppress(Exception):
                    self.allmodules.modules.remove(instance)

                if message:
                    await utils.answer(
                        message,
                        "<emoji document_id='5454225457916420314'>😖</emoji>"
                        f" <b>{utils.escape_html(str(e))}</b>",
                    )
                return
            except loader.SelfSuspend as e:
                logging.debug(f"Suspending {instance}, because it raised `SelfSuspend`")
                if message:
                    await utils.answer(
                        message,
                        "🥶 <b>Module suspended itself\nReason:"
                        f" {utils.escape_html(str(e))}</b>",
                    )
                return
            except CoreOverwriteError as e:
                await core_overwrite(e)
                return
        except Exception as e:
            logger.exception(f"Module threw because {e}")

            if message is not None:
                await utils.answer(message, self.strings("load_failed"))

            return

        with contextlib.suppress(Exception):
            if (
                not any(
                    line.replace(" ", "") == "#scope:no_stats"
                    for line in doc.splitlines()
                )
                and self._db.get(main.__name__, "stats", True)
                and url is not None
                and utils.check_url(url)
            ):
                await self._send_stats(url)

        for alias, cmd in self.lookup("settings").get("aliases", {}).items():
            if cmd in instance.commands:
                self.allmodules.add_alias(alias, cmd)

        try:
            modname = instance.strings("name")
        except KeyError:
            modname = getattr(instance, "name", "ERROR")

        try:
            if developer in self._client._umodx_cache and getattr(
                await self._client.get_entity(developer), "left", True
            ):
                developer_entity = await self._client.force_get_entity(developer)
            else:
                developer_entity = await self._client.get_entity(developer)
        except Exception:
            developer_entity = None

        if not isinstance(developer_entity, Channel):
            developer_entity = None

        if (
            developer_entity is not None
            and f"{developer_entity.id}/{modname}" not in self.get("reacted", [])
        ):
            self._react_queue += [(developer_entity, modname)]

        if message is None:
            return

        modhelp = ""

        if instance.__doc__:
            modhelp += f"<i>\nℹ️ {utils.escape_html(inspect.getdoc(instance))}</i>\n"

        subscribe = ""
        subscribe_markup = None

        depends_from = []
        for key in dir(instance):
            value = getattr(instance, key)
            if isinstance(value, loader.Library):
                depends_from.append(
                    f"▫️ <code>{value.__class__.__name__}</code><b>"
                    f" {self.strings('by')} </b><code>{value.developer if isinstance(getattr(value, 'developer', None), str) else 'Unknown'}</code>"
                )

        depends_from = (
            self.strings("depends_from").format("\n".join(depends_from))
            if depends_from
            else ""
        )

        def loaded_msg(use_subscribe: bool = True):
            nonlocal modname, version, modhelp, developer, origin, subscribe, blob_link, depends_from
            return self.strings("loaded").format(
                modname.strip(),
                version,
                utils.ascii_face(),
                modhelp,
                developer if not subscribe or not use_subscribe else "",
                depends_from,
                self.strings("modlink").format(origin)
                if origin != "<string>" and self.config["share_link"]
                else "",
                blob_link,
                subscribe if use_subscribe else "",
            )

        if developer:
            if developer.startswith("@") and developer not in self.get(
                "do_not_subscribe", []
            ):
                if (
                    developer_entity
                    and getattr(developer_entity, "left", True)
                    and self._db.get(main.__name__, "suggest_subscribe", True)
                ):
                    subscribe = self.strings("suggest_subscribe").format(
                        f"@{utils.escape_html(developer_entity.username)}"
                    )
                    subscribe_markup = [
                        {
                            "text": self.strings("subscribe"),
                            "callback": self._inline__subscribe,
                            "args": (
                                developer_entity.id,
                                functools.partial(loaded_msg, use_subscribe=False),
                                True,
                            ),
                        },
                        {
                            "text": self.strings("no_subscribe"),
                            "callback": self._inline__subscribe,
                            "args": (
                                developer,
                                functools.partial(loaded_msg, use_subscribe=False),
                                False,
                            ),
                        },
                    ]

            developer = self.strings("developer").format(
                utils.escape_html(developer)
                if isinstance(developer_entity, Channel)
                else f"<code>{utils.escape_html(developer)}</code>"
            )
        else:
            developer = ""

        if any(
            line.replace(" ", "") == "#scope:disable_onload_docs"
            for line in doc.splitlines()
        ):
            await utils.answer(message, loaded_msg(), reply_markup=subscribe_markup)
            return

        for _name, fun in sorted(
            instance.commands.items(),
            key=lambda x: x[0],
        ):
            modhelp += self.strings("single_cmd").format(
                self.get_prefix(),
                _name,
                (
                    utils.escape_html(inspect.getdoc(fun))
                    if fun.__doc__
                    else self.strings("undoc_cmd")
                ),
            )

        if self.inline.init_complete:
            if hasattr(instance, "inline_handlers"):
                for _name, fun in sorted(
                    instance.inline_handlers.items(),
                    key=lambda x: x[0],
                ):
                    modhelp += self.strings("ihandler").format(
                        f"@{self.inline.bot_username} {_name}",
                        (
                            utils.escape_html(inspect.getdoc(fun))
                            if fun.__doc__
                            else self.strings("undoc_ihandler")
                        ),
                    )

        try:
            await utils.answer(message, loaded_msg(), reply_markup=subscribe_markup)
        except telethon.errors.rpcerrorlist.MediaCaptionTooLongError:
            await message.reply(loaded_msg(False))

    async def _inline__subscribe(
        self,
        call: InlineCall,
        entity: int,
        msg: callable,
        subscribe: bool,
    ):
        if not subscribe:
            self.set("do_not_subscribe", self.get("do_not_subscribe", []) + [entity])
            await utils.answer(call, msg())
            await call.answer(self.strings("not_subscribed"))
            return

        await self._client(JoinChannelRequest(entity))
        await utils.answer(call, msg())
        await call.answer(self.strings("subscribed"))

    @loader.owner
    @loader.command(ru_doc="Выгрузить модуль")
    async def unloadmod(self, message: Message):
        """Unload module by class name"""
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, self.strings("no_class"))
            return

        instance = self.lookup(args)

        if issubclass(instance.__class__, loader.Library):
            await utils.answer(message, self.strings("cannot_unload_lib"))
            return

        try:
            worked = await self.allmodules.unload_module(args)
        except CoreUnloadError as e:
            await utils.answer(message, self.strings("unload_core").format(e.module))
            return

        if not self.allmodules.secure_boot:
            self.set(
                "loaded_modules",
                {
                    mod: link
                    for mod, link in self.get("loaded_modules", {}).items()
                    if mod not in worked
                },
            )

        msg = (
            self.strings("unloaded").format(
                ", ".join(
                    [(mod[:-3] if mod.endswith("Mod") else mod) for mod in worked]
                )
            )
            if worked
            else self.strings("not_unloaded")
        )

        await utils.answer(message, msg)

    @loader.owner
    @loader.command(ru_doc="Удалить все модули")
    async def clearmodules(self, message: Message):
        """Delete all installed modules"""
        await self.inline.form(
            self.strings("confirm_clearmodules"),
            message,
            reply_markup=[
                {
                    "text": self.strings("clearmodules"),
                    "callback": self._inline__clearmodules,
                },
                {
                    "text": self.strings("cancel"),
                    "action": "close",
                },
            ],
        )

    async def _inline__clearmodules(self, call: InlineCall):
        self.set("loaded_modules", {})

        if "DYNO" not in os.environ:
            for file in os.scandir(loader.LOADED_MODULES_DIR):
                os.remove(file)

        self.set("chosen_preset", "none")

        await utils.answer(call, self.strings("all_modules_deleted"))
        await self.lookup("Updater").restart_common(call)

    async def _update_modules(self):
        todo = await self._get_modules_to_load()

        # ⚠️⚠️  WARNING!  ⚠️⚠️
        # If you are a module developer, and you'll try to bypass this protection to
        # force user join your channel, you will be added to SCAM modules
        # list and you will be banned from umodx federation.
        # Let USER decide, which channel he will follow. Do not be so petty
        # I hope, you understood me.
        # Thank you

        if any(
            arg in todo.values()
            for arg in {
                "https://mods.hikariatama.ru/forbid_joins.py",
                "https://heta.hikariatama.ru/hikariatama/ftg/forbid_joins.py",
                "https://github.com/hikariatama/ftg/raw/master/forbid_joins.py",
                "https://raw.githubusercontent.com/hikariatama/ftg/master/forbid_joins.py",
            }
        ):
            from ..forbid_joins import install_join_forbidder

            install_join_forbidder(self._client)

        secure_boot = False

        if self._db.get(loader.__name__, "secure_boot", False):
            self._db.set(loader.__name__, "secure_boot", False)
            secure_boot = True
        else:
            for mod in todo.values():
                await self.download_and_install(mod)

            self._update_modules_in_db()

            aliases = {
                alias: cmd
                for alias, cmd in self.lookup("settings").get("aliases", {}).items()
                if self.allmodules.add_alias(alias, cmd)
            }

            self.lookup("settings").set("aliases", aliases)

        self._fully_loaded = True

        with contextlib.suppress(AttributeError):
            await self.lookup("Updater").full_restart_complete(secure_boot)
