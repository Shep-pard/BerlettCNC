#!/usr/bin/python3
import serial
import hal
import sys
import time

PORT = "/dev/ttyACM0"
ser = serial.Serial(PORT, 115200, timeout=.5)

# Now we create the HAL component and its pins
# HAL_IN arduino can read the from linuxCNC
# HAL_OUT arduino can write to linuxCNC

c = hal.component("STM_IO")

for port in range(48):
    c.newpin("IN.%02d" % port, hal.HAL_BIT, hal.HAL_OUT)
    c.newpin("OUT.%02d" % port, hal.HAL_BIT, hal.HAL_IN)


time.sleep(1)
c.ready()

key = ''
try:
    while 1:

        ser.flushInput()
        a = bytearray()
        a.append(0x01)
        a = ser.write(a)
        del a
        inData = 0
        sendData = 0
        time.sleep(0.05)

        # Check to see if we have a message waiting from the Arduino
        while ser.inWaiting():
            # This should be set to the length of whatever fixed-length message
            # you're sending from the arduino. It does not have to be the same length
            # as the outbound messages.
            key = ser.read(7)
            #for i in range(7):
            #    print(key[i])
            # The Arduino generates two different key events
            # One when the key is pressed down (+S) and another when it is released (-S)
            # In this case we are going to ignore the release

        if len(key) == 7:
            for i in range(6):
                inData = inData | ((key[6-i]) << (8*i))
        # print len(key)

        for ports in range(48):
            if c['IN.%02d' % ports] != (inData >> ports) & 0x01:
                print("PORT" + str(ports) + "Changed")
            c['IN.%02d' % ports] = (inData >> ports) & 0x01

            sendData = sendData | (c['OUT.%02d' % ports] << (ports))

        # sendString = ''
        # for i in range(6):
            # sendString += ( (sendData >> (8*i)) & 0xFF )
        a = bytearray()
        a.append(0x02)
        for i in range(6):
            a.append(((sendData >> (47 - (8*i))) & 0xFF))
        print(a)
        a = ser.write(a)
        del a

        time.sleep(.03)

except KeyboardInterrupt:
    ser.write(str.encode("-P;"))
    ser.close()
    raise SystemExit
