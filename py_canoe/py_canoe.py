import sys

import can
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from can.interfaces.vector import VectorBus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import udsoncan.configs
import isotp
from my_ui import Ui_MainWindow


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


class busThread(QThread):
    uds_tx_finished = pyqtSignal(object)
    uds_rx_finished = pyqtSignal(object)

    def __init__(self, conn, bytes_msg):
        super().__init__()
        self.conn = conn
        self.bytes_msg = bytes_msg

    def run(self):
        try:
            self.conn.send(self.bytes_msg)
            self.uds_tx_finished.emit(True)
        except isotp.errors.IsoTpError as e:
            print("错误:", e)
            self.uds_tx_finished.emit(str(e))
            return

        try:
            x_bytes_msg = self.conn.wait_frame(timeout=2)

            self.uds_rx_finished.emit(x_bytes_msg)
        except ValueError as e:
            print("错误:", e)
            self.uds_rx_finished.emit(str(e))


class MainWindows(QMainWindow, Ui_MainWindow):

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
            'rx_flowcontrol_timeout': 1000,
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
        # print(self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'])
        if self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'].channel_capabilities.value & \
                can.interfaces.vector.xldefine.XL_ChannelCapabilities.XL_CHANNEL_FLAG_CANFD_BOSCH_SUPPORT.value:  # 支持CANfd
            self.comboBox_2.clear()
            self.comboBox_2.addItem('CAN')
            self.comboBox_2.addItem('CANFD')
            if self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'].is_on_bus:
                # print(self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'].bus_params.can.can_op_mode)
                if self.vectorAvailableConfigs[self.channel_index]['vector_channel_config'].bus_params.can.can_op_mode == \
                        can.interfaces.vector.xldefine.XL_CANFD_BusParams_CanOpMode.XL_BUS_PARAMS_CANOPMODE_CAN20:
                    self.chooseBusType = 0
                    self.comboBox_2.setCurrentIndex(self.chooseBusType)
                else:
                    self.chooseBusType = 1
                    self.comboBox_2.setCurrentIndex(self.chooseBusType)

            else:
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
        if self.is_start == 0:
            VectorBus.set_application_config(app_name=self.appName, app_channel=self.channel_index,
                                             **self.vectorAvailableConfigs[self.channel_index])
            try:
                self.canbus = VectorBus(channel=self.channel_index, app_name=self.appName, fd=bool(self.chooseBusType),
                                        **self.vectorChannelCanParams)
            except can.CanInitializationError as e:
                self.canbus = VectorBus(channel=self.channel_index, app_name=self.appName)
                print('CanInitializationError:',e)
            # uds_config = udsoncan.configs.default_client_config.copy()
            canlister = can.Printer()
            self.notifier = can.Notifier(self.canbus, [])  # Add a debug listener that print all messages
            # tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x123,
            #                         rxid=0x456)  # Network layer addressing scheme
            tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA05F1, rxid=0x18DAF105,
                                    functional_id=0x18DB33F1)
            # # stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)              # isotp v1.x has no notifier support
            self.stack = isotp.NotifierBasedCanStack(bus=self.canbus, notifier=self.notifier, address=tp_addr,
                                                     params=self.isotp_params)
            self.conn = PythonIsoTpConnection(self.stack)
            self.conn.open()
            self.is_start = 1

            self.comboBox.setDisabled(True)
            self.comboBox_2.setDisabled(True)
            self.pushButton_6.setDisabled(True)
            self.lineEdit.setDisabled(True)
            self.lineEdit_3.setDisabled(True)
            self.lineEdit_8.setDisabled(True)
            self.lineEdit_6.setDisabled(True)
            self.lineEdit_4.setDisabled(True)
            self.lineEdit_9.setDisabled(True)
            self.lineEdit_5.setDisabled(True)
            self.lineEdit_7.setDisabled(True)

            self.resetCANparams()



        else:
            self.conn.close()
            self.stack.stop()
            self.notifier.stop()
            self.canbus.shutdown()
            self.is_start = 0

            self.comboBox.setDisabled(False)
            self.comboBox_2.setDisabled(False)
            self.pushButton_6.setDisabled(False)
            self.lineEdit.setDisabled(False)
            self.lineEdit_3.setDisabled(False)
            self.lineEdit_8.setDisabled(False)
            self.lineEdit_6.setDisabled(False)
            self.lineEdit_4.setDisabled(False)
            self.lineEdit_9.setDisabled(False)
            self.lineEdit_5.setDisabled(False)
            self.lineEdit_7.setDisabled(False)

    def resetCANparams(self):
        self.vectorAvailableConfigs = VectorBus._detect_available_configs()
        self.ui_update_bus_type()

    def send_can_uds(self):
        self.uds_send_str = self.textEdit.toPlainText()
        # print(self.to_hex_string(self.uds_send_str))
        try:
            self.uds_send_bytes = self.str_to_bytes(self.uds_send_str)
            # # self.conn.send(uds_send_bytes)
            self.bus_thread = busThread(self.conn, self.uds_send_bytes)
            self.bus_thread.start()
            self.pushButton_4.setDisabled(True)
            self.bus_thread.uds_tx_finished.connect(self.send_finshed)
            self.bus_thread.uds_rx_finished.connect(self.rec_finshed)
        except ValueError as e:
            print("错误:", e)

    def send_finshed(self, info):
        # print(object)
        # self.pushButton_4.setDisabled(False)
        if info == True:
            self.textBrowser_2.insertPlainText('TX:' + self.uds_send_bytes.hex() + '\r')
        else:
            self.textBrowser_2.insertPlainText(info + '\r')
            self.pushButton_4.setDisabled(False)

    def rec_finshed(self, info):
        self.pushButton_4.setDisabled(False)
        if type(info) is bytes:
            self.textBrowser_2.insertPlainText('RX:' + info.hex() + '\r')
        elif info is None:
            # self.textBrowser_2.insertPlainText(str(info) + '\r')
            pass
        else:
            self.textBrowser_2.insertPlainText(str(info) + '\r')
    def str_to_bytes(self, input_str):
        # 移除输入字符串中的空格
        input_str = input_str.replace(' ', '')

        # 检查输入字符串是否是有效的十六进制字符串
        if not input_str:
            raise ValueError("输入字符串为空")
        if len(input_str) % 2 != 0:
            raise ValueError("字符串长度必须是偶数")
        if not all(c in '0123456789abcdefABCDEF' for c in input_str):
            raise ValueError("字符串包含非法字符")

        # 尝试将字符串转换为字节对象
        try:
            bytes_list = bytes.fromhex(input_str)
            return bytes_list
        except ValueError:
            raise ValueError("无效的十六进制字符串")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindows()
    w.show()
    sys.exit(app.exec_())
