import sys
import time

import can
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget
from can.interfaces.vector import VectorBus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp
import datetime
from py_can_tool import Ui_Form

# app_name = 'xl_tool_py'
#
# channel_lists = VectorBus._detect_available_configs()
#
#
#
# configs = can.detect_available_configs(interfaces=['vector'])
# cfg = configs[0]
# VectorBus.set_application_config(app_name=app_name, app_channel=0, **cfg)
#
# class VectorCanParamsd(dict):
#     bitrate: int
#     data_bitrate: int
#     sjw_abr: int
#     tseg1_abr: int
#     tseg2_abr: int
#     sam_abr: int
#     sjw_dbr: int
#     tseg1_dbr: int
#     tseg2_dbr: int
#     output_mode: can.interfaces.vector.xldefine.XL_OutputMode
#
#
# channel_can_Params = VectorCanParamsd(
#     bitrate=500000,
#     data_bitrate=2000000,
#     sjw_abr=2,
#     tseg1_abr=63,
#     tseg2_abr=16,
#     sam_abr=1,
#     sjw_dbr=2,
#     tseg1_dbr=15,
#     tseg2_dbr=4,
#     output_mode=can.interfaces.vector.xldefine.XL_OutputMode.XL_OUTPUT_MODE_NORMAL,
# )
# msg = can.Message(
#     is_extended_id=False,
#     is_remote_frame=False,
#     data=[0, 1, 2, 3, 4, 5, 6, 7],
#     dlc=8,
#     channel=0,
#     arbitration_id=0x100,
#     is_rx=False,
#     is_fd=True,
#     timestamp=datetime.datetime.timestamp(datetime.datetime.now()),
# )
#
#
#
# # channel_1 = VectorBus(channel=0, app_name=app_name, fd=True, **channel_1_canfd_Params)
# channel_1=VectorBus(channel=0, app_name=app_name, fd=True)
#
#
# # Refer to isotp documentation for full details about parameters
# isotp_params = {
#  'blocking_send': True,
#  'stmin': 32,                            # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
#  'blocksize': 8,                         # Request the sender to send 8 consecutives frames before sending a new flow control message
#  'wftmax': 0,                            # Number of wait frame allowed before triggering an error
#  'tx_data_length': 8,                    # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
#  # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
#  'tx_data_min_length': None,
#  'tx_padding': 0,                        # Will pad all transmitted CAN messages with byte 0x00.
#  'rx_flowcontrol_timeout': 5000,         # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
#  'rx_consecutive_frame_timeout': 1000,   # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
#  'override_receiver_stmin': 0,      # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
#  'max_frame_size': 4095,                 # Limit the size of receive frame.
#  'can_fd': True,                        # Does not set the can_fd flag on the output CAN messages
#  'bitrate_switch': False,                # Does not set the bitrate_switch flag on the output CAN messages
#  'rate_limit_enable': False,             # Disable the rate limiter
#  'rate_limit_max_bitrate': 1000000,      # Ignored when rate_limit_enable=False. Sets the max bitrate when rate_limit_enable=True
#  'rate_limit_window_size': 0.2,          # Ignored when rate_limit_enable=False. Sets the averaging window size for bitrate calculation when rate_limit_enable=True
#  'listen_mode': False,                   # Does not use the listen_mode which prevent transmission.
# }
#
# uds_config = udsoncan.configs.default_client_config.copy()
# canlister=can.Printer()
# notifier = can.Notifier(channel_1, [])                                       # Add a debug listener that print all messages
# # tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x123, rxid=0x456) # Network layer addressing scheme
# tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA05F1, rxid=0x18DAF105,functional_id=0x18DB33F1)
# #stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)              # isotp v1.x has no notifier support
# stack = isotp.NotifierBasedCanStack(bus=channel_1, notifier=notifier, address=tp_addr, params=isotp_params)  # Network/Transport layer (IsoTP protocol). Register a new listenenr
#
#
# uds_config['data_identifiers'] = {
#    'default' : '>H',                      # Default codec is a struct.pack/unpack string. 16bits little endian
#    # 0x1234 : MyCustomCodecThatShiftBy4,    # Uses own custom defined codec. Giving the class is ok
#    # 0x1235 : MyCustomCodecThatShiftBy4(),  # Same as 0x1234, giving an instance is good also
#    0xF194 : udsoncan.AsciiCodec(10)       # Codec that read ASCII string. We must tell the length of the string
#    }
#
# conn = PythonIsoTpConnection(stack)                                                 # interface between Application and Transport layer
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


# conn.open()
# conn.send(b'\x22\xf1\x94') # Sends ECU Reset, with subfunction = 1
# payload = conn.wait_frame(timeout=2)
# # if payload == b'\x51\x01':
# if payload :
#    print(f'Success!,data{list(payload)}')
# else:
#    print('Reset failed')


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


# for _ in range(100):
#     channel_1.send(msg)
#     time.sleep(0.5)
#
# def on_press(key):
#     try:
#         if key.char == 's':
#             print(key.char)
#     except AttributeError:
#         print(f'特殊键 {key} 被按下')
#
# def on_release(key):
#     # print(f'{key} 被释放')
#     if key == Key.esc:
#         # 停止监听
#         return False
#
# # 启动监听
# with Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()


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




class MainWindows(QWidget,Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.vectorBusType = None
        self.vectorBuscan20 = None
        self.vectorBuscanfd = None
        self.vectorChannelCanParams = None
        self.vectorAvailableConfigs = None
        self.ui = None
        self.vectorBusType = None  # 0:CAN2.2  1: CANFD
        self.is_start = 0
        self.channel_index = None
        self.appName = 'uds_tool'

        # self.ui = uic.loadUi("py_can_tool.ui")
        self.init_vector()

    def init_vector(self):

        self.vectorAvailableConfigs = VectorBus._detect_available_configs()
        # print(self.vectorAvailableConfigs[0]['vector_channel_config'])
        # self.channel_lists = can.interfaces.vector.get_channel_configs()
        if self.vectorAvailableConfigs is not None:
            self.init_ui()  # 根据获取的VECTOR硬件信息初始化ui界面

        self.vectorChannelCanParams = VectorCanParamsd(
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

        self.isotp_params = {
            'blocking_send': True,
            'stmin': 32,
            # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
            'blocksize': 8,
            # Request the sender to send 8 consecutives frames before sending a new flow control message
            'wftmax': 0,  # Number of wait frame allowed before triggering an error
            'tx_data_length': 8,  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
            # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
            'tx_data_min_length': None,
            'tx_padding': 0,  # Will pad all transmitted CAN messages with byte 0x00.
            'rx_flowcontrol_timeout': 5000,
            # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
            'rx_consecutive_frame_timeout': 1000,
            # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
            'override_receiver_stmin': 0,
            # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
            'max_frame_size': 4095,  # Limit the size of receive frame.
            'can_fd': True,  # Does not set the can_fd flag on the output CAN messages
            'bitrate_switch': False,  # Does not set the bitrate_switch flag on the output CAN messages
            'rate_limit_enable': False,  # Disable the rate limiter
            'rate_limit_max_bitrate': 1000000,
            # Ignored when rate_limit_enable=False. Sets the max bitrate when rate_limit_enable=True
            'rate_limit_window_size': 0.2,
            # Ignored when rate_limit_enable=False. Sets the averaging window size for bitrate calculation when rate_limit_enable=True
            'listen_mode': False,  # Does not use the listen_mode which prevent transmission.
        }

    def init_ui(self):

        self.comboBox.activated.connect(self.ui_update_bus_type)
        self.comboBox_2.activated.connect(self.ui_update_bus_params)
        self.pushButton.clicked.connect(self.bus_start)
        self.pushButton_4.clicked.connect(self.send_can_uds)


        # self.comboBox_2.activated.connect(self.set_CANFD_ui)
        self.ui_update_channel()
        self.ui_update_bus_type()

        # self.watch_drive=DeviceWatcher()
        # self.watch_drive.file_watcher.addPath("/dev")  # 监视/dev目录下的设备变化

    def ui_update_channel(self):
        self.comboBox.clear()
        for channel_list in self.vectorAvailableConfigs:
            self.comboBox.addItem(str(channel_list['vector_channel_config'].name) +
                                     ' ' +
                                     str(channel_list['vector_channel_config'].transceiver_name) +
                                     ' ' +
                                     str(channel_list['vector_channel_config'].serial_number))
        # self.set_ui_with_vector_confg()

    def ui_update_bus_type(self):
        self.channel_index = self.comboBox.currentIndex()

        # print(channel_index)
        if self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'].channel_capabilities.value & \
                can.interfaces.vector.xldefine.XL_ChannelCapabilities.XL_CHANNEL_FLAG_CANFD_BOSCH_SUPPORT.value:  # 支持CANfd

            self.comboBox_2.clear()
            self.comboBox_2.addItem('CAN')
            self.comboBox_2.addItem('CANFD')
            self.chooseBusType = 1
            self.comboBox_2.setCurrentIndex(self.chooseBusType)
            # self.comboBox_2.setCurrentIndex(self.vectorBusType)
            # print(self.vectorAvailableConfigs[choose_index]['vector_channel_config'])


        else:
            self.comboBox_2.clear()
            self.comboBox_2.addItem('CAN')
            self.chooseBusType = 0
            self.comboBox_2.setCurrentIndex(self.chooseBusType)
        self.ui_update_bus_params()

    def ui_update_bus_params(self):
        if self.comboBox_2.currentText() == 'CANFD':
            self.chooseBusType = 1
            # print(self.comboBox_2.currentText())

            self.lineEdit_6.setVisible(True)
            self.lineEdit_9.setVisible(True)
            self.lineEdit_5.setVisible(True)
            self.lineEdit_7.setVisible(True)

            self.label_7.setVisible(True)
            self.label_12.setVisible(True)
            self.label_6.setVisible(True)
            self.label_8.setVisible(True)

            self.lineEdit.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.bitrate))
            self.lineEdit_6.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.data_bitrate))
            self.lineEdit_3.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.sjw_abr))
            self.lineEdit_8.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.tseg1_abr))
            self.lineEdit_4.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.tseg2_abr))
            self.lineEdit_9.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.sjw_dbr))
            self.lineEdit_5.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.tseg1_dbr))
            self.lineEdit_7.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.canfd.tseg2_dbr))
        else:
            self.chooseBusType = 0
            # print(self.comboBox_2.currentText())
            self.lineEdit.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.can.bitrate))
            self.lineEdit_3.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.can.sjw))
            self.lineEdit_8.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.can.tseg1))
            self.lineEdit_4.setText(
                str(self.vectorAvailableConfigs[0]['vector_channel_config'].bus_params.can.tseg2))

            self.lineEdit_6.setVisible(False)
            self.lineEdit_9.setVisible(False)
            self.lineEdit_5.setVisible(False)
            self.lineEdit_7.setVisible(False)

            self.label_7.setVisible(False)
            self.label_12.setVisible(False)
            self.label_6.setVisible(False)
            self.label_8.setVisible(False)

    def bus_start(self):
        # if self.is_start == 0:
        #     print('bus_start')
        #     self.bus_thread = busThread(self.appName, self.channel_index,
        #                                 self.vectorAvailableConfigs[self.channel_index], self.chooseBusType,
        #                                 self.vectorChannelCanParams,
        #                                 self.isotp_params)
        #     self.bus_thread.start()
            # self.is_start=1

        # else:
        #     self.bus_thread.conn.close()
        #     self.bus_thread.canbus.shutdown()
        #     self.is_start = 0

        if self.is_start == 0:
            VectorBus.set_application_config(app_name=self.appName, app_channel=self.channel_index, **self.vectorAvailableConfigs[self.channel_index])
            self.canbus = VectorBus(channel=self.channel_index, app_name=self.appName, fd=bool(self.chooseBusType), **self.vectorChannelCanParams)
            # uds_config = udsoncan.configs.default_client_config.copy()
            canlister = can.Printer()
            self.notifier = can.Notifier(self.canbus, [])  # Add a debug listener that print all messages
            # tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x123,
            #                         rxid=0x456)  # Network layer addressing scheme
            tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA05F1, rxid=0x18DAF105,functional_id=0x18DB33F1)
            # # stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)              # isotp v1.x has no notifier support
            self.stack = isotp.NotifierBasedCanStack(bus=self.canbus, notifier=self.notifier, address=tp_addr, params=self.isotp_params)
            self.conn = PythonIsoTpConnection(self.stack)
            self.conn.open()
            self.is_start = 1
            print('打开')
            self.resetCANparams()



        else:
            self.conn.close()
            self.stack.stop()
            self.notifier.stop()
            self.canbus.shutdown()
            self.is_start = 0
            print('关闭')
    def resetCANparams(self):
        self.vectorAvailableConfigs = VectorBus._detect_available_configs()
        self.ui_update_bus_type()
    def send_can_uds(self):
        send_msg=self.textEdit.toPlainText()
        print(send_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindows()
    w.show()
    sys.exit(app.exec_())
