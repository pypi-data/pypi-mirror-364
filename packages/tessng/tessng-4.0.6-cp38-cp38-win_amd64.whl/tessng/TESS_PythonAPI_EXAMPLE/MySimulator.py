import random
from datetime import datetime
from PySide2.QtCore import QObject, Qt, Signal

from tessng import PyCustomerSimulator, tessngIFace, Online, m2p, p2m


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
class MySimulator(PyCustomerSimulator, QObject):
    # 停止仿真的信号
    forStopSimu = Signal()
    # 启动仿真的信号
    forReStartSimu = Signal()
    # 在自定义面板的信息窗上显示信息的信号
    showRunInfo = Signal(str)

    def __init__(self):
        PyCustomerSimulator.__init__(self)
        QObject.__init__(self)
        # 代表TESS NG的接口
        self.iface = tessngIFace()
        # 代表TESS NG 的路网子接口
        self.netiface = self.iface.netInterface()
        # 代表TESS NG 的仿真子接口
        self.simuiface = self.iface.simuInterface()
        # 代表TESS NG 的界面子接口
        self.guiiface = self.iface.guiInterface()
        # 主面板
        self.main_window = self.guiiface.mainWindow()

        # 关联信号和槽函数
        # 将信号关联到主窗体的槽函数doStopSimu，可以安全地停止仿真
        self.forStopSimu.connect(self.main_window.doStopSimu, Qt.QueuedConnection)
        # 将信号关联到主窗体的槽函数doStartSimu，可以安全地启动仿真
        self.forReStartSimu.connect(self.main_window.doStartSimu, Qt.QueuedConnection)

        # 车辆方阵的车辆数
        self.square_vehi_count: int = 28
        # 飞机速度，飞机后面的车辆速度会被设定为此数据
        self.plane_speed: float = 0
        # 当前正在仿真计算的路网名称
        self.current_net_name: str = ""
        # 相同路网连续仿真次数
        self.max_simu_count: int = 0

    # 重写父类方法：TESS NG 在仿真开启前调用此方法
    def beforeStart(self, ref_keep_on: bool) -> None:
        # 获取当前路网名称
        current_net_name: str = self.netiface.netFilePath()
        if current_net_name != self.current_net_name:
            self.current_net_name = current_net_name
            self.max_simu_count = 1
        else:
            self.max_simu_count += 1

    # 重写父类方法：TESS NG 在仿真开启后调用此方法
    def afterStart(self) -> None:
        pass

    # 重写父类方法：TESS NG 在仿真结束后调用此方法
    def afterStop(self) -> None:
        # 最多连续仿真2次
        if self.max_simu_count >= 2:
            return
        # 通知主窗体开启仿真
        self.forReStartSimu.emit()

    # 重写父类方法：TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self) -> None:
        # = == == == == == = 以下是获取一些仿真过程数据的方法 == == == == == ==
        # 仿真精度
        simu_accuracy: int = self.simuiface.simuAccuracy()
        # 仿真倍速
        simu_multiples: int = self.simuiface.acceMultiples()
        # 当前仿真计算批次
        batch_number = self.simuiface.batchNumber()
        # 当前已仿真时间，单位：毫秒
        simu_time = self.simuiface.simuTimeIntervalWithAcceMutiples()
        # 开始仿真的现实时间，单位：毫秒
        start_realtime = self.simuiface.startMSecsSinceEpoch()
        # 如果仿真时间大于等于600秒，通知主窗体停止仿真
        if simu_time >= 600 * 1000:
            self.forStopSimu.emit()

        # 当前正在运行车辆列表
        all_vehicles = self.simuiface.allVehiStarted()
        # 打印当前在运行车辆ID列表
        # print([item.id() for item in all_vehicles])
        # 当前在ID为1的路段上车辆
        vehicles = self.simuiface.vehisInLink(1)

        # 在信息窗显示信息
        if batch_number % simu_accuracy == 0:
            # 路段数量
            link_count: int = self.netiface.linkCount()
            # 车辆数
            vehicle_count: int = len(all_vehicles)
            run_info: str = f"路段数：{link_count}\n运行车辆数：{vehicle_count}\n仿真时间：{simu_time}(毫秒)"
            self.showRunInfo.emit(run_info)

        # 动态发车，不通过发车点发送，直接在路段和连接段中间某位置创建并发送，每50个计算批次发送一次
        if batch_number % 50 == 1:
            r = hex(256 + random.randint(0,256))[3:].upper()
            g = hex(256 + random.randint(0,256))[3:].upper()
            b = hex(256 + random.randint(0,256))[3:].upper()
            color = f"#{r}{g}{b}"
            # 路段上发车
            dvp = Online.DynaVehiParam()
            dvp.vehiTypeCode = random.randint(0, 4) + 1
            dvp.roadId = 6
            dvp.laneNumber = random.randint(0, 3)
            dvp.dist = 50
            dvp.speed = 20
            dvp.color = color
            vehicle1 = self.simuiface.createGVehicle(dvp)
            if vehicle1 is not None:
                pass

            # 连接段上发车
            dvp2 = Online.DynaVehiParam()
            dvp2.vehiTypeCode = random.randint(0, 4) + 1
            dvp2.roadId = 3
            dvp2.laneNumber = random.randint(0, 3)
            dvp2.toLaneNumber = dvp2.laneNumber # 默认为 - 1，如果大于等于0, 在连接段上发车
            dvp2.dist = 50
            dvp2.speed = 20
            dvp2.color = color
            vehicle2 = self.simuiface.createGVehicle(dvp2)
            if vehicle2 is not None:
                pass

        # 信号灯组相位颜色
        lPhoneColor = self.simuiface.getSignalPhasesColor()
        #print("信号灯组相位颜色", [(pcolor.signalGroupId, pcolor.phaseNumber, pcolor.color, pcolor.mrIntervalSetted, pcolor.mrIntervalByNow) for pcolor in lPhoneColor])
        # 获取当前仿真时间完成穿越采集器的所有车辆信息
        lVehiInfo = self.simuiface.getVehisInfoCollected()
        #if len(lVehiInfo) > 0:
        #    print("车辆信息采集器采集信息：", [(vinfo.collectorId, vinfo.vehiId) for vinfo in lVehiInfo])
        # 获取最近集计时间段内采集器采集的所有车辆集计信息
        lVehisInfoAggr = self.simuiface.getVehisInfoAggregated()
        #if len(lVehisInfoAggr) > 0:
        #    print("车辆信息采集集计数据：", [(vinfo.collectorId, vinfo.vehiCount) for vinfo in lVehisInfoAggr])
        # 获取当前仿真时间排队计数器计数的车辆排队信息
        lVehiQueue = self.simuiface.getVehisQueueCounted()
        #if len(lVehiQueue) > 0:
        #    print("车辆排队计数器计数：", [(vq.counterId, vq.queueLength) for vq in lVehiQueue])
        # 获取最近集计时间段内排队计数器集计数据
        lVehiQueueAggr = self.simuiface.getVehisQueueAggregated()
        #if len(lVehiQueueAggr) > 0:
        #    print("车辆排队集计数据：", [(vqAggr.counterId, vqAggr.avgQueueLength) for vqAggr in lVehiQueueAggr])
        # 获取当前仿真时间行程时间检测器完成的行程时间检测信息
        lVehiTravel = self.simuiface.getVehisTravelDetected()
        #if len(lVehiTravel) > 0:
        #    print("车辆行程时间检测信息：", [(vtrav.detectedId, vtrav.travelDistance) for vtrav in lVehiTravel])
        # 获取最近集计时间段内行程时间检测器集计数据
        lVehiTravAggr = self.simuiface.getVehisTravelAggregated()
        #if len(lVehiTravAggr) > 0:
        #    print("车辆行程时间集计数据：", [(vTravAggr.detectedId, vTravAggr.vehiCount, vTravAggr.avgTravelDistance) for vTravAggr in lVehiTravAggr])

    # 重写父类方法：在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehicle) -> None:
        # 设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        self.set_steps_per_call(vehicle)

        # 车辆ID，不含首位数，首位数与车辆来源有关，如发车点、公交线路
        tmp_vehicle_id = vehicle.id() % 100000
        # 车辆所在路段名或连接段名
        road_name = vehicle.roadName()
        # 车辆所在路段ID或连接段ID
        road_id = vehicle.roadId()
        if road_name == '曹安公路':
            # 飞机
            if tmp_vehicle_id == 1:
                vehicle.setVehiType(12)
                vehicle.initLane(3, m2p(105), 0)
            # 工程车
            elif tmp_vehicle_id >= 2 and tmp_vehicle_id <= 8:
                vehicle.setVehiType(8)
                vehicle.initLane((tmp_vehicle_id - 2) % 7, m2p(80), 0)
            # 消防车
            elif tmp_vehicle_id >= 9 and tmp_vehicle_id <= 15:
                vehicle.setVehiType(9)
                vehicle.initLane((tmp_vehicle_id - 2) % 7, m2p(65), 0)
            # 消防车
            elif tmp_vehicle_id >= 16 and tmp_vehicle_id <= 22:
                vehicle.setVehiType(10)
                vehicle.initLane((tmp_vehicle_id - 2) % 7, m2p(50), 0)
            # 最后两队列小车
            elif tmp_vehicle_id == 23:
                vehicle.setVehiType(1)
                vehicle.initLane(1, m2p(35), 0)
            elif tmp_vehicle_id == 24:
                vehicle.setVehiType(1)
                vehicle.initLane(5, m2p(35), 0)
            elif tmp_vehicle_id == 25:
                vehicle.setVehiType(1)
                vehicle.initLane(1, m2p(20), 0)
            elif tmp_vehicle_id == 26:
                vehicle.setVehiType(1)
                vehicle.initLane(5, m2p(20), 0)
            elif tmp_vehicle_id == 27:
                vehicle.setVehiType(1)
                vehicle.initLane(1, m2p(5), 0)
            elif tmp_vehicle_id == 28:
                vehicle.setVehiType(1)
                vehicle.initLane(5, m2p(5), 0)
            # 最后两列小车的长度设为一样长，这个很重要，如果车长不一样长，加上导致的前车距就不一样，会使它们变道轨迹长度不一样，就会乱掉
            if tmp_vehicle_id >= 23 and tmp_vehicle_id <= 28:
                vehicle.setLength(m2p(4.5), True)

    # 自定义方法：设置本类实现的过载方法被调用频次，即多少个计算周期调用一次，过多的不必要调用会影响运行效率
    def set_steps_per_call(self, vehicle) -> None:
        # 设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        net_file_name = self.netiface.netFilePath()
        # 范例打开临时路段会会创建车辆方阵，需要进行一些仿真过程控制
        if "Temp" in net_file_name:
            # 允许对车辆重绘方法的调用
            vehicle.setIsPermitForVehicleDraw(True)
            # 计算限制车道方法每10个计算周期被调用一次
            vehicle.setSteps_calcLimitedLaneNumber(10)
            # 计算安全变道距离方法每10个计算周期被调用一次
            vehicle.setSteps_calcChangeLaneSafeDist(10)
            # 重新计算车辆期望速度方法每一个计算周期被调用一次
            vehicle.setSteps_reCalcdesirSpeed(1)
            # 重新设置车速方法每一个计算周期被调用一次
            vehicle.setSteps_reSetSpeed(1)
        else:
            # 仿真精度，即每秒计算次数
            steps = self.simuface.simuAccuracy()
            # ======设置本类过载方法被TESSNG调用频次，以下是默认设置，可以修改======
            # ======车辆相关方法调用频次======
            # 是否允许对车辆重绘方法的调用
            vehicle.setIsPermitForVehicleDraw(False)
            # 计算下一位置前处理方法被调用频次
            vehicle.setSteps_beforeNextPoint(steps * 300)
            # 计算下一位置方法方法被调用频次
            vehicle.setSteps_nextPoint(steps * 300)
            # 计算下一位置完成后处理方法被调用频次
            vehicle.setSteps_afterStep(steps * 300)
            # 确定是否停止车辆运行便移出路网方法调用频次
            vehicle.setSteps_isStopDriving(steps * 300)
            # ======驾驶行为相关方法调用频次======
            # 重新设置期望速度方法被调用频次
            vehicle.setSteps_reCalcdesirSpeed(steps * 300)
            # 计算最大限速方法被调用频次
            vehicle.setSteps_calcMaxLimitedSpeed(steps * 300)
            # 计算限制车道方法被调用频次
            vehicle.setSteps_calcLimitedLaneNumber(steps)
            # 计算车道限速方法被调用频次
            vehicle.setSteps_calcSpeedLimitByLane(steps)
            # 计算安全变道方法被调用频次
            vehicle.setSteps_calcChangeLaneSafeDist(steps)
            # 重新计算是否可以左强制变道方法被调用频次
            vehicle.setSteps_reCalcToLeftLane(steps)
            # 重新计算是否可以右强制变道方法被调用频次
            vehicle.setSteps_reCalcToRightLane(steps)
            # 重新计算是否可以左自由变道方法被调用频次
            vehicle.setSteps_reCalcToLeftFreely(steps)
            # 重新计算是否可以右自由变道方法被调用频次
            vehicle.setSteps_reCalcToRightFreely(steps)
            # 计算跟驰类型后处理方法被调用频次
            vehicle.setSteps_afterCalcTracingType(steps * 300)
            # 连接段上汇入到车道前处理方法被调用频次
            vehicle.setSteps_beforeMergingToLane(steps * 300)
            # 重新跟驰状态参数方法被调用频次
            vehicle.setSteps_reSetFollowingType(steps * 300)
            # 计算加速度方法被调用频次
            vehicle.setSteps_calcAcce(steps * 300)
            # 重新计算加速度方法被调用频次
            vehicle.setSteps_reSetAcce(steps * 300)
            # 重置车速方法被调用频次
            vehicle.setSteps_reSetSpeed(steps * 300)
            # 重新计算角度方法被调用频次
            vehicle.setSteps_reCalcAngle(steps * 300)
            vehicle.setSteps_recentTimeOfSpeedAndPos(steps * 300)
            vehicle.setSteps_travelOnChangingTrace(steps * 300)
            vehicle.setSteps_leaveOffChangingTrace(steps * 300)
            # 计算后续道路前处理方法被调用频次
            vehicle.setSteps_beforeNextRoad(steps * 300)

    # 重写父类方法：停止指定车辆运行，退出路网，但不会从内存删除，会参数各种统计
    def isStopDriving(self, vehicle) -> bool:
        # 范例车辆进入ID等于2的路段或连接段，路离终点小于100米，则驰出路网
        if vehicle.roadId() == 2:
            # 车头到当前路段或连接段终点距离
            dist = vehicle.vehicleDriving().distToEndpoint(True)
            # 如果距终点距离小于100米，车辆停止运行退出路网
            if dist < m2p(100):
                return True
        return False

    # 重写父类方法：在车辆被移除时被TESS NG调用一次
    def afterStopVehicle(self, vehicle) -> None:
        pass

    # 重写父类方法，重新计算车辆的加速度，即设置车辆的期望速度，只对当前帧生效
    def ref_reSetAcce(self, vehicle, inOutAcce) -> bool:
        """
        :param vehicle: 车辆对象
        :param inOutAcce: 车辆加速度，inOutAcce.value是TESS NG已计算的车辆加速度，此方法可以改变它
        :return: True：接受此次修改，False：忽略此次修改
        """
        roadName = vehicle.roadName()
        if roadName == "连接段1":
            if vehicle.currSpeed() > m2p(20 / 3.6):
                inOutAcce.value = m2p(-5)
                return True
            elif vehicle.currSpeed() > m2p(20 / 3.6):
                inOutAcce.value = m2p(-1)
                return True
        return False

    # 重写父类方法：重新计算车辆的期望速度，即设置车辆的期望速度，只对当前帧生效
    def ref_reCalcdesirSpeed(self, vehicle, ref_desirSpeed) -> bool:
        """
        :param vehicle: 车辆对象
        :param ref_desirSpeed: 期望速度，ref_desirSpeed.value，是已计算好的车辆期望速度，此方法可以改变它
        :return: True：接受此次修改，False：忽略此次修改
        """
        tmp_vehicle_id = vehicle.id() % 100000
        road_name = vehicle.roadName()
        if road_name == '曹安公路':
            if tmp_vehicle_id <= self.square_vehi_count:
                simu_time = self.simuiface.simuTimeIntervalWithAcceMutiples()
                if simu_time < 5 * 1000:
                    ref_desirSpeed.value = 0
                elif simu_time < 10 * 1000:
                    ref_desirSpeed.value = m2p(20 / 3.6)
                else:
                    ref_desirSpeed.value = m2p(40 / 3.6)
            return True
        return False

    # 重写父类方法：重新计算车辆的当前速度，即直接修改车辆的当前速度，只对当前帧生效
    def ref_reSetSpeed(self, vehicle, ref_inOutSpeed) -> bool:
        """
        :param vehicle: 车辆对象
        :param ref_inOutSpeed: 速度，ref_inOutSpeed.value，是已计算好的车辆速度，此方法可以改变它
        :return: True：接受此次修改，False：忽略此次修改
        """
        tmp_vehicle_id = vehicle.id() % 100000
        road_name = vehicle.roadName()
        if road_name == "曹安公路":
            if tmp_vehicle_id == 1:
                self.plane_speed = vehicle.currSpeed()
            elif 2 <= tmp_vehicle_id <= self.square_vehi_count:
                ref_inOutSpeed.value = self.plane_speed
            return True
        return False

    # 重写父类方法：重新计算车辆跟驰参数，安全时距及安全距离，只对当前帧生效
    def ref_reSetFollowingParam(self, vehicle, ref_inOutSi, ref_inOutSd) -> bool:
        """
        :param vehicle: 车辆对象
        :param ref_inOutSi: 安全时距，ref_inOutSi.value是TESS NG已计算好的值，此方法可以改变它
        :param ref_inOutSd: 安全距离，ref_inOutSd.value是TESS NG已计算好的值，此方法可以改变它
        :return: True：接受此次修改，False：忽略此次修改
        """
        road_name = vehicle.roadName()
        if road_name == "连接段2":
            ref_inOutSd.value = m2p(30)
            return True
        return False

    # 重写父类方法：计算车辆是否要左自由变道
    def reCalcToLeftFreely(self, vehicle) -> bool:
        """
        :param vehicle: 车辆对象
        :return: True：车辆向左自由变道，False：TESS NG 自行判断是否要向左自由变道
        """
        # 车辆到路段终点距离小于20米不变道
        if vehicle.vehicleDriving().distToEndpoint() - vehicle.length() / 2 < m2p(20):
            return False
        tmp_vehicle_id = vehicle.id() % 100000
        road_name = vehicle.roadName()
        if road_name == "曹安公路":
            if 23 <= tmp_vehicle_id <= 28:
                lane_number = vehicle.vehicleDriving().laneNumber()
                if lane_number in [1, 4]:
                    return True
        return False

    # 重写父类方法：计算车辆是否要右自由变道
    def reCalcToRightFreely(self, vehicle) -> bool:
        """
        :param vehicle: 车辆对象
        :return: True：车辆向右自由变道，False：TESS NG 自行判断是否要向右自由变道
        """
        tmp_vehicle_id = vehicle.id() % 100000
        # 车辆到路段终点距离小于20米不变道
        if vehicle.vehicleDriving().distToEndpoint() - vehicle.length() / 2 < m2p(20):
            return False
        road_name = vehicle.roadName()
        if road_name == "曹安公路":
            if 23 <= tmp_vehicle_id <= 28:
                lane_number = vehicle.vehicleDriving().laneNumber()
                if lane_number in [2, 5]:
                    return True
        return False

    # 重写父类方法：计算车辆当前禁行车道的序号列表，只对当前帧生效
    def calcLimitedLaneNumber(self, vehicle) -> list:
        """
        :param vehicle: 车辆对象
        :return: 禁行车道的序号的列表
        """
        # 如果当前车辆在路段上，且路段ID等于2，则小车走内侧，大车走外侧
        if vehicle.roadIsLink():
            link = vehicle.lane().link()
            if link is not None and link.id() == 2:
                lane_count = link.laneCount()
                # 小车走内侧，大车走外侧，设长度小于8米为小车
                if vehicle.length() < m2p(8):
                    return [num for num in range(lane_count // 2 - 1)]
                else:
                    return [num for num in range(lane_count // 2 - 1, lane_count)]
        return []

    # 重写父类方法：设置信号灯的灯色，需要每帧都调用，否则被TESS NG 计算的灯色覆盖
    def calcLampColor(self, signal_lamp) -> bool:
        """
        :param signal_lamp: 信号灯头对象
        :return: True：接受此次修改，False：忽略此次修改
        """
        if signal_lamp.id() == 5:
            signal_lamp.setLampColor("红")
            return True
        return False

    # 重写父类方法：车道限速，只对当前帧生效
    def ref_calcSpeedLimitByLane(self, link, lane_number: int, ref_outSpeed) -> bool:
        """
        :param link: 路段对象
        :param lane_number: 车道序号，从0开始，从右向左
        :param ref_outSpeed: 可以改变ref_outSpeed.value为设定的限速值，单位：km/h
        :return: True：接受此次修改，False：忽略此次修改
        """
        # ID为2路段，车道序号为0，速度不大于30千米/小时
        if link.id() == 2 and lane_number <= 1:
            ref_outSpeed.value = 30
            return True
        return False

    # 重写父类方法：对发车点一增加发车时间段
    #   此范例展示了以飞机打头的方阵全部驰出路段后为这条路段的发车点增加发车间隔
    def calcDynaDispatchParameters(self) -> list:
        # 当前仿真时间
        current_simu_time = self.simuiface.simuTimeIntervalWithAcceMutiples()
        # ID等于1的路段上的车辆
        vehicles = self.simuiface.vehisInLink(1)
        if current_simu_time < 1000 * 10 or len(vehicles) > 0:
            return []
        now = datetime.now()
        # 当前时间秒
        current_second = now.hour * 3600 + now.minute * 60 + now.second
        # 仿真10秒后且ID等于1的路段上车辆数为0，则为ID等于1的发车点增加发车间隔
        di = Online.DispatchInterval()
        di.dispatchId = 1
        di.fromTime = current_second
        di.toTime = di.fromTime + 300 - 1
        di.vehiCount = 300
        di.mlVehicleConsDetail = [
            Online.VehiComposition(1, 60),
            Online.VehiComposition(2, 40)
        ]
        return [di]

    # 重写父类方法：动态修改决策点不同路径流量比
    def calcDynaFlowRatioParameters(self) -> list:
        # 当前仿真计算批次
        batch_number = self.simuiface.batchNumber()
        # 在计算第20批次时修改某决策点各路径流量比
        if batch_number == 20:
            # 一个决策点某个时段各路径车辆分配比
            dfi = Online.DecipointFlowRatioByInterval()
            # 决策点编号
            dfi.deciPointID = 5
            # 起始时间 单位：秒
            dfi.startDateTime = 1
            # 结束时间 单位：秒
            dfi.endDateTime = 999999
            # 路径流量比
            rfr1 = Online.RoutingFlowRatio(10, 3)
            rfr2 = Online.RoutingFlowRatio(11, 4)
            rfr3 = Online.RoutingFlowRatio(12, 3)
            dfi.mlRoutingFlowRatio = [rfr1, rfr2, rfr3]
            return [dfi]
        return []
