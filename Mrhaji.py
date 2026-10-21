# ba_meta require api 9
# ba_meta export babase.Plugin

"""Mrhaji GiftBot for BombSquad.

This version is safe for in-game execution and does not delete the mods folder.
It waits for a chat message containing "x", then watches for the next
"✅I have N coins!" message and sends a gift to the configured target.
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
        print(f"[GRT] send error: {exc}")


def parse_coins(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"(?:✅|\u2705)?\s*I have\s+([\d,]+)\s+coins!", text, re.IGNORECASE)
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
        print(f"[GRT] sound error ({name}): {exc}")


def send_gift(coins):
    try:
        safe_chat_send(f"gift {GIFT_TARGET} {coins}")
        play_sound("dingSmallHigh")
        babase.apptimer(1.0, lambda: safe_chat_send("1"))
        babase.apptimer(1.05, lambda: play_sound("dingSmall"))
    except Exception as exc:
        print(f"[GRT] gift error: {exc}")


def handle_message(msg):
    global is_active

    try:
        if not isinstance(msg, str):
            return

        content = msg
        if ": " in msg:
            content = msg.split(": ", 1)[-1].strip()
        if not content:
            return

        content_lower = content.lower()

        if "x" in content_lower and not is_active:
            is_active = True
            safe_chat_send("c!")
            play_sound("dingSmall")

        if is_active:
            coins = parse_coins(content)
            if coins is not None:
                is_active = False
                send_gift(coins)

    except Exception as exc:
        print(f"[GRT] handle error: {exc}")


class GiftBot(Plugin):
    def __init__(self):
        self.last_hash = ""
        self.running = True
        print("[GRT] Mrhaji GiftBot loaded (BombSquad API 9).")
        babase.apptimer(1.0, self.ear)

    def ear(self):
        if not self.running:
            return

        try:
            messages = GCM()
            if not messages:
                return

            last_msg = messages[-1]
            current_hash = f"{len(last_msg)}_{last_msg}"
            if current_hash == self.last_hash:
                return
            self.last_hash = current_hash
            handle_message(last_msg)

        except Exception as exc:
            print(f"[GRT] ear error: {exc}")
        finally:
            if self.running:
                babase.apptimer(0.25, self.ear)

    def on_app_shutdown(self):
        self.running = False
