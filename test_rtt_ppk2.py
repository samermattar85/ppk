from pynrfjprog import API
# import time
# import binascii
# import signal
import struct
import keyboard
# import getopt
# import sys

import argparse
import os
import numpy as np

import collections



d = collections.deque()

import threading
import time

def parser(stop, freq_factor, csvfile):
    print('parser start')
    esc_flag = False
    payload = bytearray()

    samples = list()

    print('start parser with freq_factor {} and csvfile {}'.format(freq_factor,csvfile))

    with open(csvfile, 'w') as file:
        first_sample = True
        PAYLOAD_END = 3
        ESC_FLAG = 31
        while True:
            #check if d is empty
            if not d:
                if stop():
                    print('stopping parser')
                    break
                else:
                    # time.sleep(0.01)
                    continue

            byte = d.popleft()
            if esc_flag:
                payload.append(byte ^ 0x20)
                esc_flag = False
            else:
                if byte == PAYLOAD_END:
                    if len(payload) == 4:
                        # print('size 4!!!')
                        reading = struct.unpack('<f',payload)
                        payload = bytearray()
                        samples.append(reading)
                        if len(samples) >= freq_factor:
                            sample_mean = np.mean(samples)
                            samples = list()
                            if not first_sample:
                                # print('adding {} '.format(sample_mean))
                                file.write(',{}'.format(sample_mean))
                            else:
                                first_sample = False
                                file.write('{}'.format(sample_mean))
                    # elif len(payload) == 5:
                        # print('payload size is 5')
                    elif len(payload) > 5:
                        print('payload too long!!!')
                        payload = bytearray()
                elif byte == ESC_FLAG:
                    esc_flag = True
                else:
                    # print('add byte {}'.format(byte))
                    payload.append(byte)
        






def collector(api, stop):
    cmd = b'\x02\x06\x03'
    api.rtt_write(0, cmd, None)

    EXT = '\x03'
    ESC = '\x31'

    # timestamp = 0
    while True:
        read_data = api.rtt_read(0, 1000, None)

        if len(read_data) == 0:
            continue

        d.extend(read_data) 

        if stop():
            print('stopping collector')
            cmd = b'\x02\x07\x03'
            api.rtt_write(0, cmd, None)
            break

                  
def save_data(api, csvfile, freq_factor): 
    stop_collecting = False
    collector_th = threading.Thread(name=collector, target = collector, args =(api, lambda : stop_collecting,)) 
    collector_th.start() 

    stop_parsing = False
    parser_th = threading.Thread(name=parser, target = parser, args =(lambda : stop_parsing, freq_factor, csvfile,)) 
    parser_th.start() 

    while True:
        if keyboard.is_pressed('q'):
            break

    print('stopping all')
    stop_collecting = True
    stop_parsing = True
    collector_th.join()
    parser_th.join()
    print('finished collecting and parsing')

if __name__ == "__main__":    
    arg_parser = argparse.ArgumentParser(description='get and analyze specific 362 data')

    arg_parser.add_argument('--sampleFreqFactor', type=int, help='set sampling factor from 7692Hz. e.g. if set to 2 the sampling freq will be 3846Hz', default=1)
    arg_parser.add_argument('--outFile', help='set name of output file', default='out.csv')
    args = arg_parser.parse_args()
    snr = None
    # Detect the device family of your device. Initialize an API object with UNKNOWN family and read the device's family. This step is performed so this example can be run in all devices without customer input.
    print('# Opening API with device family UNKNOWN, reading the device family.')
    with API.API(API.DeviceFamily.UNKNOWN) as api:            # Using with construction so there is no need to open or close the API class.
        if snr is not None:
            api.connect_to_emu_with_snr(snr)
        else:
            api.connect_to_emu_without_snr()
        device_family = api.read_device_family()

    print('device family name is {}'.format(device_family))
    
    # Initialize an API object with the target family. This will load nrfjprog.dll with the proper target family.
    api = API.API(device_family)
    
    # Open the loaded DLL and connect to an emulator probe. If several are connected a pop up will appear.
    api.open()
    if snr is not None:
        api.connect_to_emu_with_snr(snr)
    else:
        api.connect_to_emu_without_snr()

    print('is JLink DLL open? {}'.format(api.is_open()))

    # time.sleep(5)

    # sn_val = api.read_u32(0x10001080)
    # print "sn reg val is ",hex(sn)

    # wr_data = b'\x12\x34\x56\xAB'
    # api.write(0x10001080, wr_data, True)

    # sn_val = api.read_u32(0x10001080)
    # print "sn reg val is ",hex(sn)

    api.rtt_start()
    # Wait for RTT to find control block etc.
    time.sleep(0.5)
    while not api.rtt_is_control_block_found():
        print('Looking for RTT control block...')
        api.rtt_stop()
        time.sleep(0.5)
        api.rtt_start()
        time.sleep(0.5)

    is_started = api.is_rtt_started()

    print('started state is {}'.format(is_started))

    save_data(api, 'out.csv', args.sampleFreqFactor)

    api.close()


