import os
import sys
import time

from asciinema.term import raw, read_non_blocking


def compress_time(stdout, max_wait):
    if max_wait:
        return ([min(delay, max_wait), text] for delay, text in stdout)
    else:
        return stdout


def adjust_speed(stdout, speed):
    return ([delay / speed, text] for delay, text in stdout)


class Player:

    def play(self, asciicast, max_wait=None, speed=1.0):
        if os.isatty(sys.stdin.fileno()):
            with raw(sys.stdin.fileno()):
                self._play(asciicast, max_wait, speed, True)
        else:
            self._play(asciicast, max_wait, speed, False)

    def _play(self, asciicast, max_wait, speed, raw):
        step = False
        max_wait = max_wait or asciicast.max_wait

        stdout = asciicast.stdout()
        stdout = compress_time(stdout, max_wait)
        stdout = adjust_speed(stdout, speed)

        for delay, text in stdout:
            time.sleep(delay)
            sys.stdout.write(text)
            sys.stdout.flush()

            if raw:
                data = read_non_blocking(sys.stdin.fileno())
                if 0x03 in data:  # ctrl-c
                    break
                if 0x20 in data or step:  # space
                    step, exit = self._pause_loop()
                    if exit:
                        break
                if 0x2b in data:  # plus sign
                    speed = 2 * speed
                if 0x2d in data:  # minus sign
                    speed = speed / 2

    def _pause_loop(self):
        while True:
            time.sleep(0.001)
            paused_data = read_non_blocking(sys.stdin.fileno())
            if 0x2e in paused_data:  # period; step one terminal change
                return True, False
            if 0x20 in paused_data:
                return False, False
            if 0x03 in paused_data:  # ctrl-c
                return False, True
