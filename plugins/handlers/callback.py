# SCP-079-CAPTCHA - Provide challenges for new joined members
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-CAPTCHA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from json import loads

from pyrogram import Client, CallbackQuery

from .. import glovar
from ..functions.captcha import answer_question
from ..functions.etc import lang, thread
from ..functions.filters import captcha_group
from ..functions.telegram import answer_callback

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query(~captcha_group)
def check_wait(client: Client, callback_query: CallbackQuery) -> bool:
    # Answer the check query
    glovar.locks["message"].acquire()
    try:
        # Basic data
        gid = callback_query.message.chat.id
        uid = callback_query.from_user.id
        callback_data = loads(callback_query.data)
        action = callback_data["a"]
        action_type = callback_data["t"]

        # Answer
        if action == "hint":
            if action_type == "check":
                if glovar.user_ids.get(uid) and glovar.user_ids[uid]["wait"].get(gid, 0):
                    thread(answer_callback, (client, callback_query.id, lang("yes"), True))
                else:
                    thread(answer_callback, (client, callback_query.id, lang("no"), True))

        return True
    except Exception as e:
        logger.warning(f"Check wait error: {e}", exc_info=True)
    finally:
        glovar.locks["message"].release()

    return False


@Client.on_callback_query(captcha_group)
def verify_answer(client: Client, callback_query: CallbackQuery) -> bool:
    # Answer the answer query
    glovar.locks["message"].acquire()
    try:
        # Basic data
        uid = callback_query.from_user.id
        callback_data = loads(callback_query.data)
        action = callback_data["a"]
        action_type = callback_data["t"]
        data = callback_data["d"]

        # Check permission
        if data and uid != data:
            return True

        # Answer
        if action == "answer":
            if glovar.user_ids.get(uid) and glovar.user_ids[uid]["answer"]:
                text = action_type
                answer_question(client, uid, text)

        thread(answer_callback, (client, callback_query.id, ""))

        return True
    except Exception as e:
        logger.warning(f"Verify answer error: {e}", exc_info=True)
    finally:
        glovar.locks["message"].release()

    return False