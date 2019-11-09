from pynrfjprog import API
import time
import binascii
import signal
import struct
import keyboard

if __name__ == "__main__":
        snr = None
        # Detect the device family of your device. Initialize an API object with UNKNOWN family and read the device's family. This step is performed so this example can be run in all devices without customer input.
        print('# Opening API with device family UNKNOWN, reading the device family.')
        with API.API(API.DeviceFamily.UNKNOWN) as api:            # Using with construction so there is no need to open or close the API class.
            if snr is not None:
                api.connect_to_emu_with_snr(snr)
            else:
                api.connect_to_emu_without_snr()
            device_family = api.read_device_family()

        print "device family name is ",device_family
        
        # Initialize an API object with the target family. This will load nrfjprog.dll with the proper target family.
        api = API.API(device_family)
        
        # Open the loaded DLL and connect to an emulator probe. If several are connected a pop up will appear.
        api.open()
        if snr is not None:
            api.connect_to_emu_with_snr(snr)
        else:
            api.connect_to_emu_without_snr()

        print "is JLink DLL open? ",api.is_open()

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
            print "Looking for RTT control block..."
            api.rtt_stop()
            time.sleep(0.5)
            api.rtt_start()
            time.sleep(0.5)

        is_started = api.is_rtt_started()

        print "started state is ",is_started

        time.sleep(2)
        metadata = api.rtt_read(0, 1000, None)
        print metadata

        raw_file = open('/home/samer/out.bin', 'wb')

        cmd = b'\x02\x06\x03'
        api.rtt_write(0,cmd)

        EXT = '\x03'
        ESC = '\x31'

        # timestamp = 0
        while True:
            read_data = api.rtt_read(0, 1000, None)
            
            if len(read_data) == 0:
                continue

            raw_file.write(read_data)

            if keyboard.is_pressed('q'):
                print "stopping"
                cmd = b'\x02\x07\x03'
                api.rtt_write(0,cmd)
                break

        raw_file.close()

        
        # data_file = open('/home/samer/stable_ppk_out.csv', 'w')
        # raw_file = open('/home/samer/out.bin', 'rb')

        

        # data_payload = bytearray()
        # total_bytes_read = 0
        # index = 0
        # read_data = raw_file.read()
        # split_read_data = read_data.split(EXT)
        # for data_payload in split_read_data:
        #     if len(data_payload) == 4:
        #         [float_val] = struct.unpack('f', data_payload)
        #         data_file.write(str(float_val)+",")
        #         timestamp = timestamp + AVERAGE_TIME_US
        #     elif len(data_payload) == 5:
        #         continue# timestamp = convertSysTick2MicroSeconds(dataPayload.slice(0, 4))
        #     else:
        #         print("RX EXT and payload size is ", len(data_payload))


        # data_file.close()
        # raw_file.close()
    # except:
    #     raise
        # csvfilename = '/home/daniel/PycharmProjects/plot_ppk_csv/ppk_out_comm_info.csv'
