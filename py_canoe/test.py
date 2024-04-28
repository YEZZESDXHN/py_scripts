import sys

import can
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from can.interfaces.vector import VectorBus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp
import datetime


app_name = 'xl_tool_py'

channel_lists = VectorBus._detect_available_configs()



configs = can.detect_available_configs(interfaces=['vector'])
cfg = configs[0]
VectorBus.set_application_config(app_name=app_name, app_channel=0, **cfg)

class VectorCanParamsd(dict):
    bitrate: int
    data_bitrate: int
    sjw_abr: int
    tseg1_abr: int
    tseg2_abr: int
    sam_abr: int
    sjw_dbr: int
    tseg1_dbr: int
    tseg2_dbr: int
    output_mode: can.interfaces.vector.xldefine.XL_OutputMode


channel_can_Params = VectorCanParamsd(
    bitrate=500000,
    data_bitrate=2000000,
    sjw_abr=2,
    tseg1_abr=63,
    tseg2_abr=16,
    sam_abr=1,
    sjw_dbr=2,
    tseg1_dbr=15,
    tseg2_dbr=4,
    output_mode=can.interfaces.vector.xldefine.XL_OutputMode.XL_OUTPUT_MODE_NORMAL,
)
msg = can.Message(
    is_extended_id=False,
    is_remote_frame=False,
    data=[0, 1, 2, 3, 4, 5, 6, 7],
    dlc=8,
    channel=0,
    arbitration_id=0x100,
    is_rx=False,
    is_fd=True,
    timestamp=datetime.datetime.timestamp(datetime.datetime.now()),
)



channel_1 = VectorBus(channel=0, app_name=app_name, fd=True, **channel_can_Params)
# channel_1=VectorBus(channel=0, app_name=app_name, fd=True)


# Refer to isotp documentation for full details about parameters
isotp_params = {
 'blocking_send': True,
 'stmin': 32,                            # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
 'blocksize': 8,                         # Request the sender to send 8 consecutives frames before sending a new flow control message
 'wftmax': 0,                            # Number of wait frame allowed before triggering an error
 'tx_data_length': 8,                    # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
 # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
 'tx_data_min_length': None,
 'tx_padding': 0,                        # Will pad all transmitted CAN messages with byte 0x00.
 'rx_flowcontrol_timeout': 5000,         # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
 'rx_consecutive_frame_timeout': 1000,   # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
 'override_receiver_stmin': 0,      # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
 'max_frame_size': 4095,                 # Limit the size of receive frame.
 'can_fd': True,                        # Does not set the can_fd flag on the output CAN messages
 'bitrate_switch': False,                # Does not set the bitrate_switch flag on the output CAN messages
 'rate_limit_enable': False,             # Disable the rate limiter
 'rate_limit_max_bitrate': 1000000,      # Ignored when rate_limit_enable=False. Sets the max bitrate when rate_limit_enable=True
 'rate_limit_window_size': 0.2,          # Ignored when rate_limit_enable=False. Sets the averaging window size for bitrate calculation when rate_limit_enable=True
 'listen_mode': False,                   # Does not use the listen_mode which prevent transmission.
}

uds_config = udsoncan.configs.default_client_config.copy()
canlister=can.Printer()
notifier = can.Notifier(channel_1, [])                                       # Add a debug listener that print all messages
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x123, rxid=0x456) # Network layer addressing scheme
# tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA05F1, rxid=0x18DAF105,functional_id=0x18DB33F1)
#stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)              # isotp v1.x has no notifier support
stack = isotp.NotifierBasedCanStack(bus=channel_1, notifier=notifier, address=tp_addr, params=isotp_params)  # Network/Transport layer (IsoTP protocol). Register a new listenenr


# uds_config['data_identifiers'] = {
#    'default' : '>H',                      # Default codec is a struct.pack/unpack string. 16bits little endian
#    # 0x1234 : MyCustomCodecThatShiftBy4,    # Uses own custom defined codec. Giving the class is ok
#    # 0x1235 : MyCustomCodecThatShiftBy4(),  # Same as 0x1234, giving an instance is good also
#    0xF194 : udsoncan.AsciiCodec(10)       # Codec that read ASCII string. We must tell the length of the string
#    }
#
conn = PythonIsoTpConnection(stack)                                                 # interface between Application and Transport layer
# with Client(conn, config=uds_config) as client:                                     # Application layer (UDS protocol)
#    # client.ecu_reset(1)
#    # data=client.ecu_reset(1)
#    # print(list(data.original_payload))
#    # response = client.read_data_by_identifier([0xF190])
#    # print(list(response.service_data.values[61840]))  # This is a dict of DID:Value
#
#    # Or, if a single DID is expected, a shortcut to read the value of the first DID
#    vin = client.read_data_by_identifier_first(0xF194)
#    print(list(vin))  # 'ABCDE0123456789' (15 chars)


conn.open()
conn.send(b'\x22\xf1\x94') # Sends ECU Reset, with subfunction = 1
payload = conn.wait_frame(timeout=2)
# if payload == b'\x51\x01':
if payload :
   print(f'Success!,data{list(payload)}')
else:
   print('Reset failed')


# try:
#     stack.start()
#     stack.send(bytes([0x10,0x01]))    # Blocking send, raise on error
#     print("Payload transmission successfully completed.")     # Success is guaranteed because send() can raise
#
#     rxdata_array=stack.recv(True)
#     rxdata_list = list(rxdata_array)
#     print(rxdata_list)
#
# except isotp.BlockingSendFailure:   # Happens for any kind of failure, including timeouts
#     print("Send failed")
# finally:
#     stack.stop()
#     channel_1.shutdown()