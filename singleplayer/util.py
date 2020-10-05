"""Utilities"""
import logging
import time


def log(sender, msg):
    output = f"[{sender.upper()}] {msg}"
    print(f"<{time.strftime('%H:%M:%S', time.localtime())}> {output}")
    logging.info(output)
