#!/usr/bin/python3
#-*- coding: utf-8 -*-

# Mercury_remote, allows you to remotely receive data from an electricity meter
# Copyright (C) 2018 Novokreshchenov Oleg xmanchan@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/
 
# Скрипт для удаленного снятия показаний со счетчика Меркурий 203.2Т

import argparse
import serial
import struct
import time

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument('serial', type=str,  nargs='?', default=0, help='Serial port. For exmple /dev/ttyUSB0')
parser.add_argument('dev_sn', type=str,  nargs='?', default=0, help='Device serial number')
args = parser.parse_args()

com = args.serial
sn = args.dev_sn

def crc16(data):
    crc = 0xFFFF 
    l = len(data)
    i = 0
    while i < l:
        j = 0
        crc = crc ^ data[i]
        while j < 8:
            if (crc & 0x1):
                mask = 0xA001
            else:
                mask = 0x00
            crc = ((crc >> 1) & 0x7FFF) ^ mask
            j += 1
        i += 1
    if crc < 0:
        crc -= 256
    result = data + chr(crc % 256).encode() + chr(crc // 256).encode('latin-1')
    return result

# Open serial port
ser = serial.Serial(com, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
print ('Connected:', ser.isOpen())

chunk = struct.pack('>L', int(sn))
# There are commands for get different data:
# \x2f - serial number
# \x21 - self time
# \x63 - get U,I,P
# \x27 - expended electricity distributed according to tariffs
# More information you can get there: http://www.incotexcom.ru/doc/M20x.rev2015.02.15.pdf
chunk += b'\x27'
chunk = crc16(chunk)

# Send data
ser.write(chunk)
time.sleep(1)
out = ser.read_all()
ser.close()

print ('Result string:', ':'.join('{:02x}'.format(c) for c in out))
print ('Check CRC:', out[-2:] == crc16(out[:-2])[-2:])
t1 = ''.join('{:02x}'.format(c) for c in out[5:9])
t2 = ''.join('{:02x}'.format(c) for c in out[9:13])
print ('T1 =', float(t1)*0.01, '(кВт*ч)', 'T2 =', float(t2)*0.01, '(кВт*ч)')


