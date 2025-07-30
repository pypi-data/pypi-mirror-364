import os
import shutil
from PySide2.QtWidgets import QApplication
from tessng.Tessng import *
from tessng.Tessng import _Link, _Lane, _Connector, _LaneConnector, _DecisionPoint, _RoutingFLowRatio, _VehicleType


print("\033[94m欢迎使用 TessNG Python 二次开发软件包！调用 “tessng.get_demo_files()” 函数可以生成示例代码文件.\033[0m")
print("\033[94m如需了解更详细的使用说明，请访问网址：http://jidatraffic.com:82/.\033[0m")
print()


def get_demo_files() -> None:
    # 源路径和目标路径
    source_folder: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TESS_PythonAPI_EXAMPLE")
    destination_folder: str = os.path.join(os.getcwd(), "TESS_PythonAPI_EXAMPLE")

    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"案例文件夹 TESS_PythonAPI_EXAMPLE 不存在，无法生成！")
        return

    # 检查目标文件夹是否已经存在
    if os.path.exists(destination_folder):
        print(f"案例文件夹 TESS_PythonAPI_EXAMPLE 已经存在！")
        return

    try:
        # 复制文件夹
        shutil.copytree(source_folder, destination_folder)
        print(f"基础案例代码文件已经生成到当前路径：{destination_folder}")
    except Exception as e:
        print(f"基础案例代码文件生成失败：{e}")
    print()
