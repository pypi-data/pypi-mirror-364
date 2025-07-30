# TESS NG 二次开发说明：http://jidatraffic.com:82/
import os
from MyPlugin import MyPlugin


if __name__ == "__main__":
    config = {
        "__netfilepath": "",  # TODO 路网文件路径
        "__workspace": os.path.join(os.getcwd(), "WorkSpace"),  # 工作空间路径
        "__simuafterload": True,  # 加载路网后是否自动开启仿真
        "__custsimubysteps": False,  # 是否自定义仿真函数调用频率
    }
    my_tess_plugin = MyPlugin(config)
    my_tess_plugin.build()
