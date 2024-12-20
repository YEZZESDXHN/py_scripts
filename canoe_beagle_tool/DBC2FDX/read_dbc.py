import cantools
print('test0')
# 加载 DBC 文件
db = cantools.database.load_file('Core_Application_Message_protocol.dbc')
print('test')
# 遍历所有报文
for message in db.messages:
    print(f"报文名称: {message.name}")
    print(f"报文 ID: 0x{message.frame_id:x}")
    print(f"报文长度: {message.length} 字节")

    # 遍历报文中的所有信号
    print("信号布局:")
    for signal in message.signals:
        print(f"  - 信号名称: {signal.name}")
        print(f"    起始位: {signal.start}")
        print(f"    信号长度: {signal.length} 位")
        print(f"    字节序: {'大端序' if signal.byte_order == 'big_endian' else '小端序'}")
        print(f"    数据类型: {signal.is_signed and '有符号' or '无符号'}")
        print(f"    缩放因子: {signal.scale}")
        print(f"    偏移量: {signal.offset}")
        print(f"    单位: {signal.unit}")
        print("-" * 20)  # 分隔线

    print("=" * 40)  # 分隔线