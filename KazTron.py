#!/usr/bin/env python
# coding=utf8

import sys
import logging

import kaztron
from kaztron import runner
from kaztron.config import get_kaztron_config
from kaztron.logging import setup_logging, get_logging_info

# In the loving memory of my time as a moderator of r/worldbuilding network
# To the future dev, this whole thing is a mess that somehow works. Sorry for the inconvenience.
# (Assuming this is from Kazandaki -- Laogeodritt)


# load configuration
try:
    config = get_kaztron_config(kaztron.cfg_defaults)
except OSError as e:
    print(str(e), file=sys.stderr)
    sys.exit(runner.ErrorCodes.CFG_FILE)

# setup logging
setup_logging(logging.getLogger(), config, console=not config.get('core', 'daemon', False))
logger = logging.getLogger("kaztron.launcher")

if __name__ == '__main__':
    import asyncio
    import os
    import signal

    try:
        cmd = sys.argv[1].lower()
    except IndexError:
        cmd = None

    if cmd == 'start' and config.get('core', 'daemon', False):
        with runner.get_daemon_context(config):
            print("Starting KazTron (daemon mode)...")
            loop = asyncio.get_event_loop()
            runner.run_reboot_loop(loop)

    elif cmd == 'start':  # non-daemon
        print("Starting KazTron (non-daemon mode)...")
        loop = asyncio.get_event_loop()
        runner.run_reboot_loop(loop)

    elif cmd == 'debug':
        # override logging levels
        logging.getLogger().setLevel(logging.DEBUG)
        info = get_logging_info()
        info.console_handler.setLevel(logging.DEBUG)
        info.file_handler.setLevel(logging.DEBUG)
        print("Starting in debug mode...")

        # run in console (non-daemon)
        loop = asyncio.get_event_loop()
        runner.run_reboot_loop(loop)

    elif cmd == 'stop':
        if config.get('core', 'daemon', False):
            try:
                print("Reading pidfile...")
                from daemon import pidfile
                pidf = pidfile.TimeoutPIDLockFile(config.get('core', 'daemon_pidfile'))
                pid = pidf.read_pid()
                print("Stopping KazTron (PID={:d})...".format(pid))
                os.kill(pid, signal.SIGINT)
                print("Stopped.")
            except TypeError:
                logger.error("Cannot stop: daemon not running")
                sys.exit(runner.ErrorCodes.DAEMON_NOT_RUNNING)
        else:
            logger.error("Cannot stop: daemon mode disabled")
            sys.exit(runner.ErrorCodes.DAEMON_NOT_RUNNING)

    else:
        print("Usage: ./kaztron.py <start|stop|debug|help>\n")
