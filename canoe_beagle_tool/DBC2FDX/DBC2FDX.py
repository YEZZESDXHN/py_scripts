import time

import cantools
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString


def generate_dbc_xml(dbc_file, xml_file):
    """
    根据 DBC 文件信息生成格式良好的 XML 文件。

    Args:
        dbc_file (str): DBC 文件路径。
        xml_file (str): XML 文件保存路径。
    """
    db = cantools.database.load_file(dbc_file,cache_dir='./temp')
    root = ET.Element("systemvariables", {"version": "4"})
    namespace1 = ET.SubElement(root, "namespace", {"name": "", "comment": "", "interface": ""})
    namespace2 = ET.SubElement(namespace1, "namespace", {"name": "FDX", "comment": "", "interface": ""})

    # 获取消息名称作为第三层命名空间的名称
    message_name = ""
    for message in db.messages:
        message_name = message.name
        message_namespace = ET.SubElement(namespace2, "namespace", {"name": message_name+"_"+str(hex(message.frame_id)), "comment": "", "interface": ""}) # message name
        for signal in message.signals:
            signal_len=signal.length
            if signal_len<=32:
                bitcount_str='32'
            elif signal_len<=64:
                bitcount_str = '64'
            else:
                print("signal length is to long")
            # signal_name
            signal_element= ET.SubElement(message_namespace, "variable",
                                          {"anlyzLocal": "2",
                                           "readOnly": "true",
                                           "valueSequence": "false",
                                           "unit": "",
                                           "name": signal.name,
                                           "comment": "",
                                           "bitcount": bitcount_str,
                                           "isSigned": "false",
                                           "encoding": "65001",
                                           "type": "int"})


    # 格式化 XML 输出
    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root).decode()
    dom = parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")

    # 写入文件
    with open(xml_file, "w") as f:
        f.write(pretty_xml)




def generate_dbc_FDX(dbc_file, xml_file):
    db = cantools.database.load_file(dbc_file,cache_dir='./temp')
    root = ET.Element("canoefdxdescription", {"version": "1.0"})
    for message in db.messages:
        dategroup = ET.SubElement(root,"datagroup",{"groupID":str(message.frame_id),"size":""})
        identifier = ET.SubElement(dategroup, "identifier").text = message.name+' '+str(message.frame_id)
        offset=0
        size=0
        type="uint8"
        for signal in message.signals:
            offset = offset + size
            if signal.length>0 and signal.length<=8:
                size=1
                if signal.is_signed:
                    type="int8"
                else:
                    type = "uint8"

            elif signal.length>8 and signal.length<=16:
                size = 2
                if signal.is_signed:
                    type="int16"
                else:
                    type = "uint16"
            elif signal.length>16 and signal.length<=32:
                size = 4
                if signal.is_signed:
                    type="int32"
                else:
                    type = "uint32"
            elif signal.length>32 and signal.length<=64:
                size = 8
                if signal.is_signed:
                    type="int64"
                else:
                    type = "uint64"
            else:
                print("signal size to long")
            item=ET.SubElement(dategroup,"item",{"offset":str(offset), "size":str(size), "type":type})
            ET.SubElement(item, "sysvar", {"name": signal.name, "namespace": "FDX::"+message.name+"_"+str(hex(message.frame_id)), "value": "raw"})


        dategroup.set("size",str(offset+size))


    # 格式化 XML 输出
    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root).decode()
    dom = parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")

    # 写入文件
    with open(xml_file, "w") as f:
        f.write(pretty_xml)







if __name__ == "__main__":
    # dbc_file = "CANFD1.dbc"
    # 打印格式化时间

    dbc_file = "Core_Application_Message_protocol.dbc"
    # dbc_file = "CANFD1.dbc"
    sys_xml_file = "FDX_sys.xml"

    FDX_xml_file = "FDX_Description.xml"


    generate_dbc_xml(dbc_file, sys_xml_file)
    generate_dbc_FDX(dbc_file, FDX_xml_file)

