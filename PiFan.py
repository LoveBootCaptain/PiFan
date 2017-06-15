#!/usr/bin/python3
# -*- coding: utf-8 -*-

# PiFan is a python program to control a fan with a transistor.
# It uses on/ff as well as a kind of voltage regulation by turning the transitor om/of
# very very fast to "modulate" the output voltage.

# please adafruit make an AC motor driver with voltage regulation for venting the pi's from internal 5V !!!

# MIT License
#
# Copyright (c) 2016 LoveBootCaptain (https://github.com/LoveBootCaptain)
# Author: Stephan Ansorge aka LoveBootCaptain
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import atexit
import logging.handlers
import time

import RPi.GPIO as GPIO

# setup logging

temp_fan_logger = logging.getLogger('Temp and Fan Logger')
temp_fan_logger.setLevel(logging.INFO)

handler = logging.handlers.SysLogHandler(address='/dev/log')

temp_fan_logger.addHandler(handler)


# generic log function with print
def log_message(message):
    temp_fan_logger.info(message)
    print(message)


# setup GPIO
fan_pin = 21
frequency = 15

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_pin, GPIO.OUT)


def set_pin(mode):
    GPIO.output(fan_pin, mode)
    return


# create exit handler
def exit_handler():

    set_pin(False)
    GPIO.cleanup()
    log_message('Exit PiFan')


# read the cpu temp and return it
def read_cpu_temp():

    with open('/sys/class/thermal/thermal_zone0/temp') as temp:

        current_temp = float(temp.read()) / 1000
        log_message('CPU Temp: {} °C'.format(current_temp))

        return current_temp


# set the fan speed depending on temp
def set_fan_speed(temp):

    current_temp = temp

    if current_temp > 50:

        set_pin(True)

        log_message('CPU Fan: 100%')

        time.sleep(frequency)

        return

    else:

        log_message('CPU Fan: 50%')

        for j in range(frequency):

            for i in range(20):  # loop should run 1sec

                set_pin(True)
                time.sleep(0.025)

                set_pin(False)
                time.sleep(0.025)

        return


if __name__ == '__main__':

    # register exit handler
    atexit.register(exit_handler)

    try:
        # start the fan on program start
        log_message('Starting PiFan at 100% for 1sec')

        set_pin(True)
        time.sleep(1)

        log_message('Running Fan regulation now')

        while True:
            # run the loop
            set_fan_speed(read_cpu_temp())

    except KeyboardInterrupt:

        exit_handler()
