import can
from can.interfaces.vector import VectorBus
import datetime
import time

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



# channel_1 = VectorBus(channel=0, app_name=app_name, fd=True, **channel_1_canfd_Params)
channel_1=VectorBus(channel=0, app_name=app_name, fd=True)


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

for _ in range(100):
    channel_1.send(msg)
    time.sleep(0.5)
