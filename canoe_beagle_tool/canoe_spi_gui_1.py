import sys
import queue
import time
import socket

from beagle_py import *

from py_canoe import CANoe

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from PyQt5.QtWidgets import QApplication, QMainWindow

from beagle_canoe import Ui_MainWindow


class CANoeThread(QThread):
    canoe_status = pyqtSignal(object)

    def __init__(self, canoe_path):
        super().__init__()
        self.path = canoe_path

    def run(self):
        canoe = CANoe()
        canoe.open(canoe_cfg=self.path)
        canoe.get_canoe_version_info()
        self.canoe_status.emit(1)

class CANoeFDXserverThread(QThread):
    spi_message_id=pyqtSignal(object)
    def __init__(self,udp_socket):
        super().__init__()
        self.daemon = True
        self.udp_socket=udp_socket

    def getCANoeFDXDataExchange(self,byte_data: bytes, a: int) -> bytes:

        """
        查找字节类型是否以字节序列[43 41 4e 6f 65 46 44 58 02]开头，
        如果是则查找是否有字节序列[(a+8)>>8&0xFF (a+8)&0xFF 00 ff a>>8&0xFF a&0xFF],
        如果有提取字节序列后面长度a的数据

        Args:
            byte_data (bytes): 字节数据
            a (int): 数据长度

        Returns:
            bytes: 提取的数据，如果未找到则返回空字节
        """
        header = b"\x43\x41\x4e\x6f\x65\x46\x44\x58\x02"
        if not byte_data.startswith(header):
            print('if not byte_data.startswith(header)')
            return b""

        search_pattern = bytes([
            (a + 8) >> 8 & 0xFF,
            (a + 8) & 0xFF,
            0x00,
            0x05,
            0x00,
            0xFF,
            a >> 8 & 0xFF,
            a & 0xFF,
        ])

        index = byte_data.find(search_pattern)
        if index == -1:
            return b""

        data_start = index + len(search_pattern)
        data_end = data_start + a
        return byte_data[data_start:data_end]

    def run(self):
        # udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # server_address = ('127.0.0.1', 1234)
        # udp_socket.bind(server_address)
        while True:

            data, address = self.udp_socket.recvfrom(4096)
            # print(data.hex(' '))
            CANoeFDXbytes = self.getCANoeFDXDataExchange(data, 4)
            if CANoeFDXbytes != b'' and CANoeFDXbytes[0] == 0 and CANoeFDXbytes[1] == 0:
                spi_id = CANoeFDXbytes[3] + CANoeFDXbytes[2] * 0x100
                self.spi_message_id.emit(spi_id)






class CANoeFDXClientThread(QThread):
    canoe_status = pyqtSignal(object)

    def __init__(self, to_canoe_data_queue,udp_socket,ip_port):
        super().__init__()
        self.daemon = True
        self.to_canoe_data_queue = to_canoe_data_queue
        self.udp_socket=udp_socket
        self.ip_port=ip_port

    def run(self):
        count = 0



        while True:
            count = count + 1
            if count == 0xffff:
                count = 0
            try:
                # 使用阻塞式的 get() 方法，如果没有数据，线程会阻塞在这里
                # 直到有数据可用或超时
                data = self.to_canoe_data_queue.get(block=True, timeout=1)  # 设置超时时间，例如 1 秒
                if data == 'start canoe':
                    byte_array = bytearray([0x43, 0x41, 0x4E, 0x6F, 0x65, 0x46, 0x44, 0x58,
                                            0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                                            0x00, 0x4, 0x00, 0x01])
                    byte_array[12] = (count >> 8) & 0xFF
                    byte_array[13] = count & 0xFF
                    self.udp_socket.sendto(byte_array, self.ip_port)
                    self.canoe_status.emit(2)
                elif data == 'stop canoe':
                    byte_array = bytearray([0x43, 0x41, 0x4E, 0x6F, 0x65, 0x46, 0x44, 0x58,
                                            0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                                            0x00, 0x4, 0x00, 0x02])
                    byte_array[12] = (count >> 8) & 0xFF
                    byte_array[13] = count & 0xFF
                    self.udp_socket.sendto(byte_array, self.ip_port)
                    self.canoe_status.emit(1)
                else:

                    byte_array = bytearray([0x43, 0x41, 0x4E, 0x6F, 0x65, 0x46, 0x44, 0x58,
                                            0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                                            0x02, 8, 0x00, 0x05, 0x00, 0xfe, 0x02, 0])
                    data2 = bytearray()
                    for b in data:
                        data2.extend([0x00, 0x00, 0x00, b])
                    byte_array.extend(data2)

                    if data[8] == 0x10:
                        time.sleep(0.01)

                    byte_array[12] = (count >> 8) & 0xFF
                    byte_array[13] = count & 0xFF
                    # byte_array[14]=byte_array[14]+1

                    self.udp_socket.sendto(byte_array, self.ip_port)


            except queue.Empty:
                # 处理队列为空的情况，例如打印日志或进行其他操作
                pass
                # print("队列为空，等待数据...")


class BeagleThread(QThread):
    spi_id_received = pyqtSignal(int)
    def __init__(self, to_canoe_data_queue):
        super().__init__()
        self.spi_message_id=0x41
        self.to_canoe_data_queue = to_canoe_data_queue
        self.port = 0  # open port 0 by default
        self.beagle = 0

        self.samplerate = 50000  # in kHz
        self.timeout = 500  # in milliseconds
        self.latency = 200  # in milliseconds
        self.length = 0
        self.num = 0

        self.length = 128
        self.num = 0
    def update_spi_message_id(self,spi_id):
        self.spi_message_id=spi_id


    def run(self):

        # Open the device
        self.beagle = bg_open(self.port)

        if (self.beagle <= 0):
            print("Unable to open Beagle device on port %d" % self.port)
            print("Error code = %d" % self.beagle)
            sys.exit(1)

        print("Opened Beagle device on port %d" % self.port)

        # Set the samplerate
        samplerate = bg_samplerate(self.beagle, self.samplerate)
        if (samplerate < 0):
            print("error: %s" % bg_status_string(samplerate))
            sys.exit(1)

        print("Sampling rate set to %d KHz." % samplerate)

        # Set the idle timeout.
        # The Beagle read functions will return in the specified time
        # if there is no data available on the bus.
        bg_timeout(self.beagle, self.timeout)
        print("Idle timeout set to %d ms." % self.timeout)

        # Set the latency.
        # The latency parameter allows the programmer to balance the
        # tradeoff between host side buffering and the latency to
        # receive a packet when calling one of the Beagle read
        # functions.
        bg_latency(self.beagle, self.latency)
        print("Latency set to %d ms." % self.latency)

        speed = ""
        if (bg_host_ifce_speed(self.beagle)):
            speed = "high speed"
        else:
            speed = "full speed"

        print("Host interface is %s." % speed)

        # Configure the device for SPI
        bg_spi_configure(self.beagle,
                         BG_SPI_SS_ACTIVE_LOW,
                         BG_SPI_SCK_SAMPLING_EDGE_FALLING,
                         BG_SPI_BITORDER_LSB)

        # There is usually no need for target power when using the
        # Beagle as a passive monitor.
        bg_target_power(self.beagle, BG_TARGET_POWER_OFF);

        print("")

        self.spidump(self.length, self.num)

    def print_general_status(self, status):
        """ General status codes """
        print("", end=' ')
        if (status == BG_READ_OK):
            print("OK", end=' ')

        if (status & BG_READ_TIMEOUT):
            print("TIMEOUT", end=' ')

        if (status & BG_READ_ERR_MIDDLE_OF_PACKET):
            print("MIDDLE", end=' ')

        if (status & BG_READ_ERR_SHORT_BUFFER):
            print("SHORT BUFFER", end=' ')

        if (status & BG_READ_ERR_PARTIAL_LAST_BYTE):
            print("PARTIAL_BYTE(bit %d)" % (status & 0xff), end=' ')

    def spidump(self, max_bytes, num_packets):
        # Get the size of timing information for each transaction of size
        # max_bytes
        timing_size = bg_bit_timing_size(BG_PROTOCOL_SPI, max_bytes)

        # Get the current sampling rate
        samplerate_khz = bg_samplerate(self.beagle, 0)

        # Start the capture
        if (bg_enable(self.beagle, BG_PROTOCOL_SPI) != BG_OK):
            print("error: could not enable SPI capture; exiting...")
            sys.exit(1)

        # print("index,time(ns),SPI,status,mosi0/miso0 ... mosiN/misoN")
        sys.stdout.flush()

        i = 0

        # Allocate the arrays to be passed into the read function
        data_mosi = array_u08(max_bytes)
        data_miso = array_u08(max_bytes)
        bit_timing = array_u32(timing_size)

        # Capture and print information for each transaction
        while (i < num_packets or num_packets == 0):

            # Read transaction with bit timing data
            (count, status, time_sop, time_duration, time_dataoffset, data_mosi, \
             data_miso, bit_timing) = \
                bg_spi_read_bit_timing(self.beagle, data_mosi, data_miso, bit_timing)

            # Translate timestamp to ns
            # time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

            # sys.stdout.write("%d,%u,SPI,(" % (i, time_sop_ns))

            if (count < 0):
                print("error=%d,", count)

            if (status != BG_READ_OK):
                self.print_general_status(status)

            # print_spi_status(status)
            # sys.stdout.write(")")

            # Check for errors
            i += 1
            if (count <= 0):
                print("")
                sys.stdout.flush()

                if (count < 0):
                    break;

                # If zero data captured, continue
                continue;
            # if (data_mosi[6] == 0):
            #     if (data_mosi[8] == 0x10 or data_mosi[8] == 0x41 or data_mosi[8] == 0x06 or data_mosi[8] == 0x63 or
            #             data_mosi[8] == 0x64 or data_mosi[8] == 0x65):
            #         self.to_canoe_data_queue.put(data_mosi)
            if (data_mosi[6] == 0):
                if (data_mosi[8] == self.spi_message_id):
                    byte_array = bytearray(data_mosi)
                    try:
                        self.to_canoe_data_queue.put(byte_array,block=False)
                        # print(self.to_canoe_data_queue.qsize())
                    except queue.Full:
                        print("队列已满")
                    # print('beagle:')
                    # print(data_mosi)

            # Display the data
            # for n in range(count):
            #     if (n != 0):         sys.stdout.write(", ")
            #     if ((n & 0xf) == 0): sys.stdout.write("\n    ")
            #     print("%02x/%02x" % (data_mosi[n], data_miso[n]), end=' ')
            # sys.stdout.write("\n")
            # sys.stdout.flush()

        # Stop the capture
        bg_disable(self.beagle)


class MainWindows(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.canoe_cfg_path = r'C:/Workspace/02 INEOS/03 Project/CANoe_INEOS/INEOS_CANoe14_V1.0.cfg'
        self.canoe_status = 0
        self.init()

    def init(self):
        # 创建线程安全的队列
        self.to_canoe_data_queue = queue.Queue(maxsize=30)  # 需要处理的spi message id
        # self.to_beagle_data_queue = queue.Queue()  # spi数据队列

        # 创建线程实例
        self.canoe_thread = CANoeThread(self.canoe_cfg_path)
        self.beagle_thread = BeagleThread(self.to_canoe_data_queue)




        # 链接信号与槽
        self.PB_OpenCANoe.clicked.connect(self.open_canoe)
        self.PB_StartCANoe.clicked.connect(self.run_canoe)
        self.PB_StartBeagle.clicked.connect(self.run_beagle)
        self.PB_CANoeFDX.clicked.connect(self.creatCANoeFDX)


        self.lineEdit_SPI_Id.editingFinished.connect(self.get_spi_id)
        self.beagle_thread.spi_id_received.connect(self.beagle_thread.update_spi_message_id)

        self.lineEdit_SPI_Id.setText('0x41')





    def get_spi_id(self):
        id_text=self.lineEdit_SPI_Id.text()
        try:
            # 尝试将字符串解释为十六进制数
            spi_id= int(id_text, 10)
            self.beagle_thread.spi_id_received.emit(spi_id)
        except ValueError:
            # 如果不是有效的十六进制数，则尝试将其解释为十进制数
            try:
                spi_id = int(id_text, 16)
                self.beagle_thread.spi_id_received.emit(spi_id)
            except ValueError:
                print(' 不是有效的十六进制或十进制字符串')
    def update_lineEdit_SPI_Id(self,spi_id):
        self.lineEdit_SPI_Id.setText(str(hex(spi_id)))


    def creatCANoeFDX(self):
        try:
            self.client = socket.socket(socket.AF_INET,
                                        socket.SOCK_DGRAM)  # udp协议
            self.client.bind(('127.0.0.1', 2810))
            self.ip_port = ('127.0.0.1', 2809)


            self.canoe_FDX_client_thread = CANoeFDXClientThread(self.to_canoe_data_queue,self.client,self.ip_port)
            self.canoe_FDX_client_thread.start()
            self.canoe_FDX_server_thread = CANoeFDXserverThread(self.client)
            self.canoe_FDX_server_thread.start()


            self.canoe_FDX_server_thread.spi_message_id.connect(self.beagle_thread.update_spi_message_id)
            self.canoe_FDX_server_thread.spi_message_id.connect(self.update_lineEdit_SPI_Id)

            self.canoe_FDX_client_thread.canoe_status.connect(self.set_canoe_status)
            self.canoe_thread.canoe_status.connect(self.set_canoe_status)
        except Exception as e:
            print(f"Error in UDP server: {e}")






    def open_canoe(self):
        self.canoe_thread.start()
        self.PB_StartCANoe.setText("startCANoe")
        self.PB_StartCANoe.setDisabled(False)
        self.PB_OpenCANoe.setDisabled(True)

    def set_canoe_status(self, status):
        self.canoe_status = status
        if self.canoe_status == 0:  # 未打开
            self.PB_StartCANoe.setDisabled(True)
        elif self.canoe_status == 1:  # 打开
            self.PB_OpenCANoe.setDisabled(False)
            self.PB_StartCANoe.setText("startCANoe")
            self.PB_StartCANoe.setDisabled(False)
        elif self.canoe_status == 2:  # 打开
            self.PB_StartCANoe.setDisabled(False)
            self.PB_StartCANoe.setText("stopCANoe")

    def run_canoe(self):

        if self.canoe_status == 1 or self.canoe_status == 0:  # 打开
            self.to_canoe_data_queue.put('start canoe')
        elif self.canoe_status == 2:  # 运行
            self.to_canoe_data_queue.put('stop canoe')

    # 运行/停止beagle
    def run_beagle(self):
        self.beagle_thread.start()


if __name__ == "__main__":
    spi_message_id=0x41
    app = QApplication(sys.argv)
    w = MainWindows()
    w.show()
    sys.exit(app.exec_())
