# ba_meta require api 9
# ba_meta export babase.Plugin

"""Mrhaji GiftBot adapted for BombSquad 1.7.62 (API 9).

Safety: this plugin never deletes files or folders. Chat/gift commands are
retained from the original script; test in a private party first.
"""

import re

import babase
import bauiv1 as bui
import bascenev1 as bs
from babase import Plugin
from bascenev1 import get_chat_messages as GCM

GIFT_TARGET = "Badr"
is_active = False


def safe_chat_send(msg):
    try:
        bs.chatmessage(msg)
    except Exception as exc:
        print("[GRT] send error: {}".format(exc))


def parse_coins(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"âœ…I have\s+([\d,]+)\s+coins!", text)
    if match:
        try:
            return int(match.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


def play_sound(name):
    try:
        bui.getsound(name).play()
    except Exception as exc:
        print("[GRT] sound error ({}): {}".format(name, exc))


def send_gift(coins):
    try:
        safe_chat_send("gift {} {}".format(GIFT_TARGET, coins))
        play_sound("dingSmallHigh")
        babase.apptimer(1.0, lambda: safe_chat_send("1"))
        babase.apptimer(1.05, lambda: play_sound("dingSmall"))
    except Exception as exc:
        print("[GRT] gift error: {}".format(exc))


def handle_message(msg):
    global is_active
    try:
        if not isinstance(msg, str):
            return
        content = msg.split(": ", 1)[-1].strip()
        if not content:
            return

        if "x" in content.lower() and not is_active:
            is_active = True
            safe_chat_send("c!")
            play_sound("dingSmall")

        if is_active:
            coins = parse_coins(content)
            if coins is not None:
                is_active = False
                send_gift(coins)
    except Exception as exc:
        print("[GRT] handle error: {}".format(exc))


class GiftBot(Plugin):
    def __init__(self):
        self.last_hash = ""
        self.running = True
        babase.apptimer(1.0, self.ear)
        print("[GRT] Mrhaji GiftBot loaded (BombSquad API 9).")

    def ear(self):
        if not self.running:
            return
        try:
            messages = GCM()
            if messages:
                last_msg = messages[-1]
                current_hash = "{}_{}".format(len(last_msg), last_msg)
                if current_hash != self.last_hash:
                    self.last_hash = current_hash
                    handle_message(last_msg)
        except Exception as exc:
            print("[GRT] ear error: {}".format(exc))
        finally:
            if self.running:
                babase.apptimer(0.25, self.ear)

    def on_app_shutdown(self):
        self.running = False
