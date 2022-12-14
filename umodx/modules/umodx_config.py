import ast
import functools
import logging
from math import ceil
from typing import Optional, Union, Any

from telethon.tl.types import Message

from .. import loader, utils, translations
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

# Everywhere in this module, we use the following naming convention:
# `obj_type` of non-core module = False
# `obj_type` of core module = True
# `obj_type` of library = "library"


@loader.tds
class umodxConfigMod(loader.Module):
    """Interactive configurator for umodx Userbot"""

    strings = {
        "name": "Configs",
        "choose_core": "đ <b>Choose a category</b>",
        "configure": "đ <b>Choose a module to configure</b>",
        "configure_lib": "đĒ´ <b>Choose a library to configure</b>",
        "configuring_mod": (
            "đ <b>Choose config option for mod</b> <code>{}</code>\n\n<b>Current"
            " options:</b>\n\n{}"
        ),
        "configuring_lib": (
            "đĒ´ <b>Choose config option for library</b> <code>{}</code>\n\n<b>Current"
            " options:</b>\n\n{}"
        ),
        "configuring_option": (
            "đ <b>Configuring option </b><code>{}</code><b> of mod"
            " </b><code>{}</code>\n<i>âšī¸ {}</i>\n\n<b>Default: {}</b>\n\n<b>Current:"
            " {}</b>\n\n{}"
        ),
        "configuring_option_lib": (
            "đĒ´ <b>Configuring option </b><code>{}</code><b> of library"
            " </b><code>{}</code>\n<i>âšī¸ {}</i>\n\n<b>Default: {}</b>\n\n<b>Current:"
            " {}</b>\n\n{}"
        ),
        "option_saved": (
            "đ <b>Option </b><code>{}</code><b> of module </b><code>{}</code><b>"
            " saved!</b>\n<b>Current: {}</b>"
        ),
        "option_saved_lib": (
            "đĒ´ <b>Option </b><code>{}</code><b> of library </b><code>{}</code><b>"
            " saved!</b>\n<b>Current: {}</b>"
        ),
        "option_reset": (
            "âģī¸ <b>Option </b><code>{}</code><b> of module </b><code>{}</code><b> has"
            " been reset to default</b>\n<b>Current: {}</b>"
        ),
        "option_reset_lib": (
            "âģī¸ <b>Option </b><code>{}</code><b> of library </b><code>{}</code><b> has"
            " been reset to default</b>\n<b>Current: {}</b>"
        ),
        "args": "đĢ <b>You specified incorrect args</b>",
        "no_mod": "đĢ <b>Module doesn't exist</b>",
        "no_option": "đĢ <b>Configuration option doesn't exist</b>",
        "validation_error": "đĢ <b>You entered incorrect config value. \nError: {}</b>",
        "try_again": "đ Try again",
        "typehint": "đĩī¸ <b>Must be a{eng_art} {}</b>",
        "set": "set",
        "set_default_btn": "âģī¸ Reset default",
        "enter_value_btn": "âī¸ Enter value",
        "enter_value_desc": "âī¸ Enter new configuration value for this option",
        "add_item_desc": "âī¸ Enter item to add",
        "remove_item_desc": "âī¸ Enter item to remove",
        "back_btn": "đ Back",
        "close_btn": "đģ Close",
        "add_item_btn": "â Add item",
        "remove_item_btn": "â Remove item",
        "show_hidden": "đ¸ Show value",
        "hide_value": "đ Hide value",
        "builtin": "đ° Built-in",
        "external": "đ¸ External",
        "libraries": "đĒ´ Libraries",
    }

    strings_ru = {
        "choose_core": "đ <b>ĐŅĐąĐĩŅĐ¸ ĐēĐ°ŅĐĩĐŗĐžŅĐ¸Ņ</b>",
        "configure": "đ <b>ĐŅĐąĐĩŅĐ¸ ĐŧĐžĐ´ŅĐģŅ Đ´ĐģŅ ĐŊĐ°ŅŅŅĐžĐšĐēĐ¸</b>",
        "configure_lib": "đĒ´ <b>ĐŅĐąĐĩŅĐ¸ ĐąĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēŅ Đ´ĐģŅ ĐŊĐ°ŅŅŅĐžĐšĐēĐ¸</b>",
        "configuring_mod": (
            "đ <b>ĐŅĐąĐĩŅĐ¸ ĐŋĐ°ŅĐ°ĐŧĐĩŅŅ Đ´ĐģŅ ĐŧĐžĐ´ŅĐģŅ</b> <code>{}</code>\n\n<b>ĐĸĐĩĐēŅŅĐ¸Đĩ"
            " ĐŊĐ°ŅŅŅĐžĐšĐēĐ¸:</b>\n\n{}"
        ),
        "configuring_lib": (
            "đĒ´ <b>ĐŅĐąĐĩŅĐ¸ ĐŋĐ°ŅĐ°ĐŧĐĩŅŅ Đ´ĐģŅ ĐąĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēĐ¸</b> <code>{}</code>\n\n<b>ĐĸĐĩĐēŅŅĐ¸Đĩ"
            " ĐŊĐ°ŅŅŅĐžĐšĐēĐ¸:</b>\n\n{}"
        ),
        "configuring_option": (
            "đ <b>ĐŖĐŋŅĐ°Đ˛ĐģĐĩĐŊĐ¸Đĩ ĐŋĐ°ŅĐ°ĐŧĐĩŅŅĐžĐŧ </b><code>{}</code><b> ĐŧĐžĐ´ŅĐģŅ"
            " </b><code>{}</code>\n<i>âšī¸ {}</i>\n\n<b>ĐĄŅĐ°ĐŊĐ´Đ°ŅŅĐŊĐžĐĩ:"
            " {}</b>\n\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>\n\n{}"
        ),
        "configuring_option_lib": (
            "đĒ´ <b>ĐŖĐŋŅĐ°Đ˛ĐģĐĩĐŊĐ¸Đĩ ĐŋĐ°ŅĐ°ĐŧĐĩŅŅĐžĐŧ </b><code>{}</code><b> ĐąĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēĐ¸"
            " </b><code>{}</code>\n<i>âšī¸ {}</i>\n\n<b>ĐĄŅĐ°ĐŊĐ´Đ°ŅŅĐŊĐžĐĩ:"
            " {}</b>\n\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>\n\n{}"
        ),
        "option_saved": (
            "đ <b>ĐĐ°ŅĐ°ĐŧĐĩŅŅ </b><code>{}</code><b> ĐŧĐžĐ´ŅĐģŅ </b><code>{}</code><b>"
            " ŅĐžŅŅĐ°ĐŊĐĩĐŊ!</b>\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>"
        ),
        "option_saved_lib": (
            "đĒ´ <b>ĐĐ°ŅĐ°ĐŧĐĩŅŅ </b><code>{}</code><b> ĐąĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēĐ¸ </b><code>{}</code><b>"
            " ŅĐžŅŅĐ°ĐŊĐĩĐŊ!</b>\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>"
        ),
        "option_reset": (
            "âģī¸ <b>ĐĐ°ŅĐ°ĐŧĐĩŅŅ </b><code>{}</code><b> ĐŧĐžĐ´ŅĐģŅ </b><code>{}</code><b>"
            " ŅĐąŅĐžŅĐĩĐŊ Đ´Đž ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Ņ ĐŋĐž ŅĐŧĐžĐģŅĐ°ĐŊĐ¸Ņ</b>\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>"
        ),
        "option_reset_lib": (
            "âģī¸ <b>ĐĐ°ŅĐ°ĐŧĐĩŅŅ </b><code>{}</code><b> ĐąĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēĐ¸ </b><code>{}</code><b>"
            " ŅĐąŅĐžŅĐĩĐŊ Đ´Đž ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Ņ ĐŋĐž ŅĐŧĐžĐģŅĐ°ĐŊĐ¸Ņ</b>\n<b>ĐĸĐĩĐēŅŅĐĩĐĩ: {}</b>"
        ),
        "_cls_doc": "ĐĐŊŅĐĩŅĐ°ĐēŅĐ¸Đ˛ĐŊŅĐš ĐēĐžĐŊŅĐ¸ĐŗŅŅĐ°ŅĐžŅ umodx",
        "args": "đĢ <b>ĐĸŅ ŅĐēĐ°ĐˇĐ°Đģ ĐŊĐĩĐ˛ĐĩŅĐŊŅĐĩ Đ°ŅĐŗŅĐŧĐĩĐŊŅŅ</b>",
        "no_mod": "đĢ <b>ĐĐžĐ´ŅĐģŅ ĐŊĐĩ ŅŅŅĐĩŅŅĐ˛ŅĐĩŅ</b>",
        "no_option": "đĢ <b>ĐŖ ĐŧĐžĐ´ŅĐģŅ ĐŊĐĩŅ ŅĐ°ĐēĐžĐŗĐž ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Ņ ĐēĐžĐŊŅĐ¸ĐŗĐ°</b>",
        "validation_error": (
            "đĢ <b>ĐĐ˛ĐĩĐ´ĐĩĐŊĐž ĐŊĐĩĐēĐžŅŅĐĩĐēŅĐŊĐžĐĩ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ ĐēĐžĐŊŅĐ¸ĐŗĐ°. \nĐŅĐ¸ĐąĐēĐ°: {}</b>"
        ),
        "try_again": "đ ĐĐžĐŋŅĐžĐąĐžĐ˛Đ°ŅŅ ĐĩŅĐĩ ŅĐ°Đˇ",
        "typehint": "đĩī¸ <b>ĐĐžĐģĐļĐŊĐž ĐąŅŅŅ {}</b>",
        "set": "ĐŋĐžŅŅĐ°Đ˛Đ¸ŅŅ",
        "set_default_btn": "âģī¸ ĐĐŊĐ°ŅĐĩĐŊĐ¸Đĩ ĐŋĐž ŅĐŧĐžĐģŅĐ°ĐŊĐ¸Ņ",
        "enter_value_btn": "âī¸ ĐĐ˛ĐĩŅŅĐ¸ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ",
        "enter_value_desc": "âī¸ ĐĐ˛ĐĩĐ´Đ¸ ĐŊĐžĐ˛ĐžĐĩ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ ŅŅĐžĐŗĐž ĐŋĐ°ŅĐ°ĐŧĐĩŅŅĐ°",
        "add_item_desc": "âī¸ ĐĐ˛ĐĩĐ´Đ¸ ŅĐģĐĩĐŧĐĩĐŊŅ, ĐēĐžŅĐžŅŅĐš ĐŊŅĐļĐŊĐž Đ´ĐžĐąĐ°Đ˛Đ¸ŅŅ",
        "remove_item_desc": "âī¸ ĐĐ˛ĐĩĐ´Đ¸ ŅĐģĐĩĐŧĐĩĐŊŅ, ĐēĐžŅĐžŅŅĐš ĐŊŅĐļĐŊĐž ŅĐ´Đ°ĐģĐ¸ŅŅ",
        "back_btn": "đ ĐĐ°ĐˇĐ°Đ´",
        "close_btn": "đģ ĐĐ°ĐēŅŅŅŅ",
        "add_item_btn": "â ĐĐžĐąĐ°Đ˛Đ¸ŅŅ ŅĐģĐĩĐŧĐĩĐŊŅ",
        "remove_item_btn": "â ĐŖĐ´Đ°ĐģĐ¸ŅŅ ŅĐģĐĩĐŧĐĩĐŊŅ",
        "show_hidden": "đ¸ ĐĐžĐēĐ°ĐˇĐ°ŅŅ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ",
        "hide_value": "đ ĐĄĐēŅŅŅŅ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ",
        "builtin": "đ° ĐŅŅŅĐžĐĩĐŊĐŊŅĐĩ",
        "external": "đ¸ ĐĐŊĐĩŅĐŊĐ¸Đĩ",
        "libraries": "đĒ´ ĐĐ¸ĐąĐģĐ¸ĐžŅĐĩĐēĐ¸",
    }

    _row_size = 3
    _num_rows = 5

    @staticmethod
    def prep_value(value: Any) -> Any:
        if isinstance(value, str):
            return f"</b><code>{utils.escape_html(value.strip())}</code><b>"

        if isinstance(value, list) and value:
            return (
                "</b><code>[</code>\n    "
                + "\n    ".join(
                    [f"<code>{utils.escape_html(str(item))}</code>" for item in value]
                )
                + "\n<code>]</code><b>"
            )

        return f"</b><code>{utils.escape_html(value)}</code><b>"

    def hide_value(self, value: Any) -> str:
        if isinstance(value, list) and value:
            return self.prep_value(["*" * len(str(i)) for i in value])

        return self.prep_value("*" * len(str(value)))

    async def inline__set_config(
        self,
        call: InlineCall,
        query: str,
        mod: str,
        option: str,
        inline_message_id: str,
        obj_type: Union[bool, str] = False,
    ):
        try:
            self.lookup(mod).config[option] = query
        except loader.validators.ValidationError as e:
            await call.edit(
                self.strings("validation_error").format(e.args[0]),
                reply_markup={
                    "text": self.strings("try_again"),
                    "callback": self.inline__configure_option,
                    "args": (mod, option),
                    "kwargs": {"obj_type": obj_type},
                },
            )
            return

        await call.edit(
            self.strings(
                "option_saved" if isinstance(obj_type, bool) else "option_saved_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(self.lookup(mod).config[option])
                if not self.lookup(mod).config._config[option].validator
                or self.lookup(mod).config._config[option].validator.internal_id
                != "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
            inline_message_id=inline_message_id,
        )

    async def inline__reset_default(
        self,
        call: InlineCall,
        mod: str,
        option: str,
        obj_type: Union[bool, str] = False,
    ):
        mod_instance = self.lookup(mod)
        mod_instance.config[option] = mod_instance.config.getdef(option)

        await call.edit(
            self.strings(
                "option_reset" if isinstance(obj_type, bool) else "option_reset_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(self.lookup(mod).config[option])
                if not self.lookup(mod).config._config[option].validator
                or self.lookup(mod).config._config[option].validator.internal_id
                != "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
        )

    async def inline__set_bool(
        self,
        call: InlineCall,
        mod: str,
        option: str,
        value: bool,
        obj_type: Union[bool, str] = False,
    ):
        try:
            self.lookup(mod).config[option] = value
        except loader.validators.ValidationError as e:
            await call.edit(
                self.strings("validation_error").format(e.args[0]),
                reply_markup={
                    "text": self.strings("try_again"),
                    "callback": self.inline__configure_option,
                    "args": (mod, option),
                    "kwargs": {"obj_type": obj_type},
                },
            )
            return

        validator = self.lookup(mod).config._config[option].validator
        doc = utils.escape_html(
            next(
                (
                    validator.doc[lang]
                    for lang in self._db.get(translations.__name__, "lang", "en").split(
                        " "
                    )
                    if lang in validator.doc
                ),
                validator.doc["en"],
            )
        )

        await call.edit(
            self.strings(
                "configuring_option"
                if isinstance(obj_type, bool)
                else "configuring_option_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                utils.escape_html(self.lookup(mod).config.getdoc(option)),
                self.prep_value(self.lookup(mod).config.getdef(option)),
                self.prep_value(self.lookup(mod).config[option])
                if not validator or validator.internal_id != "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
                self.strings("typehint").format(
                    doc,
                    eng_art="n" if doc.lower().startswith(tuple("euioay")) else "",
                )
                if doc
                else "",
            ),
            reply_markup=self._generate_bool_markup(mod, option, obj_type),
        )

        await call.answer("â")

    def _generate_bool_markup(
        self,
        mod: str,
        option: str,
        obj_type: Union[bool, str] = False,
    ) -> list:
        return [
            [
                *(
                    [
                        {
                            "text": f"â {self.strings('set')} `False`",
                            "callback": self.inline__set_bool,
                            "args": (mod, option, False),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                    if self.lookup(mod).config[option]
                    else [
                        {
                            "text": f"â {self.strings('set')} `True`",
                            "callback": self.inline__set_bool,
                            "args": (mod, option, True),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                )
            ],
            [
                *(
                    [
                        {
                            "text": self.strings("set_default_btn"),
                            "callback": self.inline__reset_default,
                            "args": (mod, option),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                    if self.lookup(mod).config[option]
                    != self.lookup(mod).config.getdef(option)
                    else []
                )
            ],
            [
                {
                    "text": self.strings("back_btn"),
                    "callback": self.inline__configure,
                    "args": (mod,),
                    "kwargs": {"obj_type": obj_type},
                },
                {"text": self.strings("close_btn"), "action": "close"},
            ],
        ]

    async def inline__add_item(
        self,
        call: InlineCall,
        query: str,
        mod: str,
        option: str,
        inline_message_id: str,
        obj_type: Union[bool, str] = False,
    ):
        try:
            try:
                query = ast.literal_eval(query)
            except Exception:
                pass

            if isinstance(query, (set, tuple)):
                query = list(query)

            if not isinstance(query, list):
                query = [query]

            self.lookup(mod).config[option] = self.lookup(mod).config[option] + query
        except loader.validators.ValidationError as e:
            await call.edit(
                self.strings("validation_error").format(e.args[0]),
                reply_markup={
                    "text": self.strings("try_again"),
                    "callback": self.inline__configure_option,
                    "args": (mod, option),
                    "kwargs": {"obj_type": obj_type},
                },
            )
            return

        await call.edit(
            self.strings(
                "option_saved" if isinstance(obj_type, bool) else "option_saved_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(self.lookup(mod).config[option])
                if not self.lookup(mod).config._config[option].validator
                or self.lookup(mod).config._config[option].validator.internal_id
                != "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
            inline_message_id=inline_message_id,
        )

    async def inline__remove_item(
        self,
        call: InlineCall,
        query: str,
        mod: str,
        option: str,
        inline_message_id: str,
        obj_type: Union[bool, str] = False,
    ):
        try:
            try:
                query = ast.literal_eval(query)
            except Exception:
                pass

            if isinstance(query, (set, tuple)):
                query = list(query)

            if not isinstance(query, list):
                query = [query]

            query = list(map(str, query))

            old_config_len = len(self.lookup(mod).config[option])

            self.lookup(mod).config[option] = [
                i for i in self.lookup(mod).config[option] if str(i) not in query
            ]

            if old_config_len == len(self.lookup(mod).config[option]):
                raise loader.validators.ValidationError(
                    f"Nothing from passed value ({self.prep_value(query)}) is not in"
                    " target list"
                )
        except loader.validators.ValidationError as e:
            await call.edit(
                self.strings("validation_error").format(e.args[0]),
                reply_markup={
                    "text": self.strings("try_again"),
                    "callback": self.inline__configure_option,
                    "args": (mod, option),
                    "kwargs": {"obj_type": obj_type},
                },
            )
            return

        await call.edit(
            self.strings(
                "option_saved" if isinstance(obj_type, bool) else "option_saved_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(self.lookup(mod).config[option])
                if not self.lookup(mod).config._config[option].validator
                or self.lookup(mod).config._config[option].validator.internal_id
                != "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
            inline_message_id=inline_message_id,
        )

    def _generate_series_markup(
        self,
        call: InlineCall,
        mod: str,
        option: str,
        obj_type: Union[bool, str] = False,
    ) -> list:
        return [
            [
                {
                    "text": self.strings("enter_value_btn"),
                    "input": self.strings("enter_value_desc"),
                    "handler": self.inline__set_config,
                    "args": (mod, option, call.inline_message_id),
                    "kwargs": {"obj_type": obj_type},
                }
            ],
            [
                *(
                    [
                        {
                            "text": self.strings("remove_item_btn"),
                            "input": self.strings("remove_item_desc"),
                            "handler": self.inline__remove_item,
                            "args": (mod, option, call.inline_message_id),
                            "kwargs": {"obj_type": obj_type},
                        },
                        {
                            "text": self.strings("add_item_btn"),
                            "input": self.strings("add_item_desc"),
                            "handler": self.inline__add_item,
                            "args": (mod, option, call.inline_message_id),
                            "kwargs": {"obj_type": obj_type},
                        },
                    ]
                    if self.lookup(mod).config[option]
                    else []
                ),
            ],
            [
                *(
                    [
                        {
                            "text": self.strings("set_default_btn"),
                            "callback": self.inline__reset_default,
                            "args": (mod, option),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                    if self.lookup(mod).config[option]
                    != self.lookup(mod).config.getdef(option)
                    else []
                )
            ],
            [
                {
                    "text": self.strings("back_btn"),
                    "callback": self.inline__configure,
                    "args": (mod,),
                    "kwargs": {"obj_type": obj_type},
                },
                {"text": self.strings("close_btn"), "action": "close"},
            ],
        ]

    async def _choice_set_value(
        self,
        call: InlineCall,
        mod: str,
        option: str,
        value: bool,
        obj_type: Union[bool, str] = False,
    ):
        try:
            self.lookup(mod).config[option] = value
        except loader.validators.ValidationError as e:
            await call.edit(
                self.strings("validation_error").format(e.args[0]),
                reply_markup={
                    "text": self.strings("try_again"),
                    "callback": self.inline__configure_option,
                    "args": (mod, option),
                    "kwargs": {"obj_type": obj_type},
                },
            )
            return

        validator = self.lookup(mod).config._config[option].validator
        doc = utils.escape_html(
            next(
                (
                    validator.doc[lang]
                    for lang in self._db.get(translations.__name__, "lang", "en").split(
                        " "
                    )
                    if lang in validator.doc
                ),
                validator.doc["en"],
            )
        )

        await call.edit(
            self.strings(
                "option_saved" if isinstance(obj_type, bool) else "option_saved_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(self.lookup(mod).config[option])
                if not validator.internal_id == "Hidden"
                else self.hide_value(self.lookup(mod).config[option]),
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
        )

        await call.answer("â")

    def _generate_choice_markup(
        self,
        call: InlineCall,
        mod: str,
        option: str,
        obj_type: Union[bool, str] = False,
    ) -> list:
        possible_values = list(
            self.lookup(mod)
            .config._config[option]
            .validator.validate.keywords["possible_values"]
        )
        return [
            [
                {
                    "text": self.strings("enter_value_btn"),
                    "input": self.strings("enter_value_desc"),
                    "handler": self.inline__set_config,
                    "args": (mod, option, call.inline_message_id),
                    "kwargs": {"obj_type": obj_type},
                }
            ],
            *utils.chunks(
                [
                    {
                        "text": (
                            f"{'âī¸' if self.lookup(mod).config[option] == value else 'đ'} "
                            f"{value if len(str(value)) < 20 else str(value)[:20]}"
                        ),
                        "callback": self._choice_set_value,
                        "args": (mod, option, value, obj_type),
                    }
                    for value in possible_values
                ],
                2,
            )[:6],
            [
                *(
                    [
                        {
                            "text": self.strings("set_default_btn"),
                            "callback": self.inline__reset_default,
                            "args": (mod, option),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                    if self.lookup(mod).config[option]
                    != self.lookup(mod).config.getdef(option)
                    else []
                )
            ],
            [
                {
                    "text": self.strings("back_btn"),
                    "callback": self.inline__configure,
                    "args": (mod,),
                    "kwargs": {"obj_type": obj_type},
                },
                {"text": self.strings("close_btn"), "action": "close"},
            ],
        ]

    async def inline__configure_option(
        self,
        call: InlineCall,
        mod: str,
        config_opt: str,
        force_hidden: Optional[bool] = False,
        obj_type: Union[bool, str] = False,
    ):
        module = self.lookup(mod)
        args = [
            utils.escape_html(config_opt),
            utils.escape_html(mod),
            utils.escape_html(module.config.getdoc(config_opt)),
            self.prep_value(module.config.getdef(config_opt)),
            self.prep_value(module.config[config_opt])
            if not module.config._config[config_opt].validator
            or module.config._config[config_opt].validator.internal_id != "Hidden"
            or force_hidden
            else self.hide_value(module.config[config_opt]),
        ]

        if (
            module.config._config[config_opt].validator
            and module.config._config[config_opt].validator.internal_id == "Hidden"
        ):
            additonal_button_row = (
                [
                    [
                        {
                            "text": self.strings("hide_value"),
                            "callback": self.inline__configure_option,
                            "args": (mod, config_opt, False),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                ]
                if force_hidden
                else [
                    [
                        {
                            "text": self.strings("show_hidden"),
                            "callback": self.inline__configure_option,
                            "args": (mod, config_opt, True),
                            "kwargs": {"obj_type": obj_type},
                        }
                    ]
                ]
            )
        else:
            additonal_button_row = []

        try:
            validator = module.config._config[config_opt].validator
            doc = utils.escape_html(
                next(
                    (
                        validator.doc[lang]
                        for lang in self._db.get(
                            translations.__name__, "lang", "en"
                        ).split(" ")
                        if lang in validator.doc
                    ),
                    validator.doc["en"],
                )
            )
        except Exception:
            doc = None
            validator = None
            args += [""]
        else:
            args += [
                self.strings("typehint").format(
                    doc,
                    eng_art="n" if doc.lower().startswith(tuple("euioay")) else "",
                )
            ]
            if validator.internal_id == "Boolean":
                await call.edit(
                    self.strings(
                        "configuring_option"
                        if isinstance(obj_type, bool)
                        else "configuring_option_lib"
                    ).format(*args),
                    reply_markup=additonal_button_row
                    + self._generate_bool_markup(mod, config_opt, obj_type),
                )
                return

            if validator.internal_id == "Series":
                await call.edit(
                    self.strings(
                        "configuring_option"
                        if isinstance(obj_type, bool)
                        else "configuring_option_lib"
                    ).format(*args),
                    reply_markup=additonal_button_row
                    + self._generate_series_markup(call, mod, config_opt, obj_type),
                )
                return

            if validator.internal_id == "Choice":
                await call.edit(
                    self.strings(
                        "configuring_option"
                        if isinstance(obj_type, bool)
                        else "configuring_option_lib"
                    ).format(*args),
                    reply_markup=additonal_button_row
                    + self._generate_choice_markup(call, mod, config_opt, obj_type),
                )
                return

        await call.edit(
            self.strings(
                "configuring_option"
                if isinstance(obj_type, bool)
                else "configuring_option_lib"
            ).format(*args),
            reply_markup=additonal_button_row
            + [
                [
                    {
                        "text": self.strings("enter_value_btn"),
                        "input": self.strings("enter_value_desc"),
                        "handler": self.inline__set_config,
                        "args": (mod, config_opt, call.inline_message_id),
                        "kwargs": {"obj_type": obj_type},
                    }
                ],
                [
                    {
                        "text": self.strings("set_default_btn"),
                        "callback": self.inline__reset_default,
                        "args": (mod, config_opt),
                        "kwargs": {"obj_type": obj_type},
                    }
                ],
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__configure,
                        "args": (mod,),
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ],
            ],
        )

    async def inline__configure(
        self,
        call: InlineCall,
        mod: str,
        obj_type: Union[bool, str] = False,
    ):
        btns = [
            {
                "text": param,
                "callback": self.inline__configure_option,
                "args": (mod, param),
                "kwargs": {"obj_type": obj_type},
            }
            for param in self.lookup(mod).config
        ]

        await call.edit(
            self.strings(
                "configuring_mod" if isinstance(obj_type, bool) else "configuring_lib"
            ).format(
                utils.escape_html(mod),
                "\n".join(
                    [
                        f"âĢī¸ <code>{utils.escape_html(key)}</code>:"
                        f" <b>{self.prep_value(value) if not self.lookup(mod).config._config[key].validator or self.lookup(mod).config._config[key].validator.internal_id != 'Hidden' else self.hide_value(value)}</b>"
                        for key, value in self.lookup(mod).config.items()
                    ]
                ),
            ),
            reply_markup=list(utils.chunks(btns, 2))
            + [
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.inline__global_config,
                        "kwargs": {"obj_type": obj_type},
                    },
                    {"text": self.strings("close_btn"), "action": "close"},
                ]
            ],
        )

    async def inline__choose_category(self, call: Union[Message, InlineCall]):
        await utils.answer(
            call,
            self.strings("choose_core"),
            reply_markup=[
                [
                    {
                        "text": self.strings("builtin"),
                        "callback": self.inline__global_config,
                        "kwargs": {"obj_type": True},
                    },
                    {
                        "text": self.strings("external"),
                        "callback": self.inline__global_config,
                    },
                ],
                *(
                    [
                        [
                            {
                                "text": self.strings("libraries"),
                                "callback": self.inline__global_config,
                                "kwargs": {"obj_type": "library"},
                            }
                        ]
                    ]
                    if self.allmodules.libraries
                    and any(hasattr(lib, "config") for lib in self.allmodules.libraries)
                    else []
                ),
                [{"text": self.strings("close_btn"), "action": "close"}],
            ],
        )

    async def inline__global_config(
        self,
        call: InlineCall,
        page: int = 0,
        obj_type: Union[bool, str] = False,
    ):
        if isinstance(obj_type, bool):
            to_config = [
                mod.strings("name")
                for mod in self.allmodules.modules
                if hasattr(mod, "config")
                and callable(mod.strings)
                and (getattr(mod, "__origin__", None) == "<core>" or not obj_type)
                and (getattr(mod, "__origin__", None) != "<core>" or obj_type)
            ]
        else:
            to_config = [
                lib.name for lib in self.allmodules.libraries if hasattr(lib, "config")
            ]

        to_config.sort()

        kb = []
        for mod_row in utils.chunks(
            to_config[
                page
                * self._num_rows
                * self._row_size : (page + 1)
                * self._num_rows
                * self._row_size
            ],
            3,
        ):
            row = [
                {
                    "text": btn,
                    "callback": self.inline__configure,
                    "args": (btn,),
                    "kwargs": {"obj_type": obj_type},
                }
                for btn in mod_row
            ]
            kb += [row]

        if len(to_config) > self._num_rows * self._row_size:
            kb += self.inline.build_pagination(
                callback=functools.partial(
                    self.inline__global_config, obj_type=obj_type
                ),
                total_pages=ceil(len(to_config) / (self._num_rows * self._row_size)),
                current_page=page + 1,
            )

        kb += [
            [
                {
                    "text": self.strings("back_btn"),
                    "callback": self.inline__choose_category,
                },
                {"text": self.strings("close_btn"), "action": "close"},
            ]
        ]

        await call.edit(
            self.strings(
                "configure" if isinstance(obj_type, bool) else "configure_lib"
            ),
            reply_markup=kb,
        )

    @loader.command(ru_doc="ĐĐ°ŅŅŅĐžĐ¸ŅŅ ĐŧĐžĐ´ŅĐģĐ¸")
    async def configcmd(self, message: Message):
        """Configure modules"""
        args = utils.get_args_raw(message)
        if self.lookup(args) and hasattr(self.lookup(args), "config"):
            form = await self.inline.form("đ <b>Loading configuration</b>", message)
            mod = self.lookup(args)
            if isinstance(mod, loader.Library):
                type_ = "library"
            else:
                type_ = getattr(mod, "__origin__", None) == "<core>"

            await self.inline__configure(form, args, obj_type=type_)
            return

        await self.inline__choose_category(message)

    @loader.command(
        ru_doc=(
            "<ĐŧĐžĐ´ŅĐģŅ> <ĐŊĐ°ŅŅŅĐžĐšĐēĐ°> <ĐˇĐŊĐ°ŅĐĩĐŊĐ¸ĐĩĐŽ - ŅŅŅĐ°ĐŊĐžĐ˛Đ¸ŅŅ ĐˇĐŊĐ°ŅĐĩĐŊĐ¸Đĩ ĐēĐžĐŊŅĐ¸ĐŗĐ° Đ´ĐģŅ ĐŧĐžĐ´ŅĐģŅ"
        )
    )
    async def fconfig(self, message: Message):
        """<module_name> <property_name> <config_value> - set the config value for the module"""
        args = utils.get_args_raw(message).split(maxsplit=2)

        if len(args) < 3:
            await utils.answer(message, self.strings("args"))
            return

        mod, option, value = args

        instance = self.lookup(mod)
        if not instance:
            await utils.answer(message, self.strings("no_mod"))
            return

        if option not in instance.config:
            await utils.answer(message, self.strings("no_option"))
            return

        instance.config[option] = value
        await utils.answer(
            message,
            self.strings(
                "option_saved"
                if isinstance(instance, loader.Module)
                else "option_saved_lib"
            ).format(
                utils.escape_html(option),
                utils.escape_html(mod),
                self.prep_value(instance.config[option])
                if not instance.config._config[option].validator
                or instance.config._config[option].validator.internal_id != "Hidden"
                else self.hide_value(instance.config[option]),
            ),
        )
