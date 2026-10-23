# Unextended V1 无线 NIZ 开发

> **历史 A1，已废弃。当前请使用 [A2 原生 USB 直出方案](direct-usb-A2.zh-CN.md)。下文空格下主控、无 FFC 和 USB 延长线均不再适用。**

已确认目标：V1、ANSI 61 键、6.25U 空格、MX 十字轴键帽、蓝牙 BLE + USB 输入/充电，无独立接收器。新增内容位于 `design/`、`hardware/`、`mechanical/`、`firmware/`、`scripts/`，上游 ALPS 文件继续作为参考。

当前是 A1 一体式工程设计，不是可下单生产版本。原理图、PCB、定位板和固件都已有实际文件；实物静电容扫描、蓝牙、续航、充电及装壳均未验证。机器生成的检查报告位于 `reports/`，未连接网络与 DRC 不能被成功编译替代。

## 架构与装配边界

主板 285 × 94.6 × 1.6 mm，四层，61 个 EC 电极、两颗 CD74HC4051、OPA350 模拟放大器、PMOS 电源门控、26 个 EC60 夹紧孔。逻辑矩阵为 5 × 15，按物理位置分配列，实际只扫描 61 个位置。

nice!nano v2 / nRF52840 直接安装在主板背面，候选中心为 x=95、y=84.8 mm，位于 6.25U 空格左翼下方，不使用 FFC。使用模块而不是裸芯片，保留模块自带 USB、稳压与充电电路。

曾考虑右下角模块和独立 FFC 控制器；右 Ctrl 电极与天线净空冲突，不代表整块主板都放不下控制器。改用空格下空白区域后，主 PCB 已设置 x=103–120、y=78.8–90.8 mm 的全层天线禁布区，定位板预留相应窗口。这是候选净空，不是已通过射频测试的布局。原型独立载板 `UnextendedEC-controller.*` 仅保留为台架研究，不与当前主板直接连接，也不属于装机 BOM。优先聚碳酸酯 V1；铝壳仍需专门的天线窗口。模块底部、USB 插头、电池、O-ring 的装壳净空尚未完成三维验证。

USB 采用模块本体 USB-C 加被动数据延长线到外壳开口，延长线规格和弯折空间尚未选定。现阶段不是能直接插上 C3 JST 的设计，不能将 C3 的 5V 输出接到电池脚。电池经主板 J1、SW1 和 BAT_SW 接到模块电池端，由 nice!nano 自带电源电路负责充电。断开开关时电池不充电。750 mAh、约 3 mm 厚只是 V1 的候选电池指标，需核对保护板、极性和膨胀净空。

定位板初稿为 1.6 mm、14 × 14 mm 圆角轴孔，板底距 PCB 顶面 6 mm 是待量测候选值。大键稳定器槽需用实际采购的板载稳定器测试。先切 `mechanical/niz-fit-coupon.dxf`，核对 housing 卡扣、静音圈、稳定器和全行程，再制作完整定位板。26 个 M2 孔沿用 EC60，螺母、housing、O-ring 干涉仍需检查。

## 固件与校准

普通版和 USB shell 校准版均已本地编译，UF2 在 `firmware/prebuilt/`；仅适用于这里定义的 nice!nano v2 引脚和模拟电路。ADC 使用 D19/P0.02/AIN0 的逻辑通道 1，避开电量驱动占用的逻辑通道 0。

Fn+1/2/3 切换蓝牙配置；Fn+4 清除当前配对；Fn+5 选择 USB；Fn+6 选择 BLE；Fn+H/J/K/L 为方向；Fn+Esc 进入 bootloader。USB 和 BLE 都启用，报告发往当前选择的一个端点。

活跃/空闲/长期空闲等待间隔为 4/8/12 ms，不是实测扫描帧时间或延迟。持续低速扫描保持按键响应，深度睡眠关闭；不承诺月级待机。驱动补丁修复空闲后首键恢复扫描、无效校准和零噪声 SNR 除零，真实 C 函数的 960 组逻辑场景及 61 键同时按下/释放已测试，ADC/GPIO 为模拟输入。

实物上电后先验证电源、模拟输出幅度和门控时序，再刷校准版，通过 USB CDC shell 执行：

```
ec kscan0 calibration start
ec kscan0 calibration export
ec kscan0 calibration save
```

先全键释放采样，再逐个按下全部 61 键。保存导出结果并断电检查恢复，再刷普通版。没有校准的电极不会成为可用按键；重刷时不要清空 settings 分区。

## 可复现构建

使用 KiCad 10 Python 执行 `scripts/generate_pcb.py`；`--controller` 仅生成旧台架载板。普通 Python 执行原理图/固件生成器。CAD 环境安装 `requirements-cad.txt` 后执行 `scripts/generate_mechanical.py`。所有尺寸来自 `design/unextended_ec.json` 和 `scripts/circuit.py`。PCB 生成器会重建未布线种子，不可直接覆盖已有手工布线。

将 `firmware/west-lock.yml` 复制为独立工作区 `config/west.yml`，运行 `west init -l config`、`west update`。容器固定为：

```
zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5
```

将工作区挂载到 `/work`、仓库挂载到 `/repo`，容器内运行：

```
python3 /repo/scripts/build_firmware.py --workspace /work
python3 /repo/scripts/test_ec_driver.py --workspace /work
python3 /repo/scripts/package_firmware.py --workspace /work
```

`prepare_firmware.py` 核对 EC 提交及修改前后哈希后应用补丁。CI 采用同一流程；本轮验证的是本地构建，不声称远程 CI 已运行。

## 下一道放行条件

完成主板布线、KiCad 原生 ERC/DRC 和零未连接检查；完成与真实 V1 的位置对齐，校核模块、电池、USB 延长插头、螺丝和 O-ring；然后才导出首件 PCBA 生产包。首件需测试低电量、充电中、BLE 发射中、全键按下、温度变化、空闲首键和按键释放。通过这些检查前不要按当前文件生产完整整机。

## 渲染、焊接与屏蔽

[焊接与分阶段上电指南](soldering.zh-CN.md) 包含当前 BOM 的焊接顺序、极性、检查点和屏蔽边界。[渲染说明](renders.md) 说明真实 CAD 与概念包络的区别。`website/dist/` 为中英双语宣传站；没有购买入口，也不把开发指标宣传成实测结果。
