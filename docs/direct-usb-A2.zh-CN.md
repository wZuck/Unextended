# A2：原生 Type-C 直出，静电容前端分离

[English](direct-usb-A2.md) · [当前主板原理图](../hardware/UnextendedEC-schematic.pdf) · [接口板原理图](../hardware/UnextendedEC-controller-schematic.pdf)

本版替代 A0/A1。nice!nano **不再安装在空格下的感应主板上**，而是固定在低位 USB 接口仓；外部 USB 线直接插入模块自带的 Type-C。无内部 USB 延长线、无 C3 USB 转接板，也不拆改模块 USB 插座。蓝牙 + USB、ANSI 61、6.25U 空格和固件 GPIO 分配保持不变。

**仍为开发版，不是生产放行。** 软件测试、几何包络和 DRC 无法证明实物“零电气影响”；真实噪声、扫描稳定性、充电与射频测试是必须通过的条件。

## 实际 USB 口与外壳

`generate_usb_bay.py` 从原 V1 STEP 的 USB 开口内轮廓提取中心，约为世界坐标 `(0, 50.442, 6.9545)` mm。模块插口包络对齐这个中心，朝外壳后方直接插拔。坐标不是照着效果图猜的，但模块插座相对 PCB 的实际高度仍需量测，当前采用 mid-mount 与总厚 3.2 mm 的名义包络。

![接口仓剖视，模块及插头是包络模型](../renders/direct-usb-cutaway.png)

原接口仓与载板/模块存在实体干涉，**原版外壳不能直接安装本版**。已输出保持外部开口不变、局部扩展内部仓位并增加支撑的 `mechanical/Unextended_V1_EC_direct_USB.step`，完整位置关系在 `direct-usb-assembly.step`。包络检查涵盖载板、模块、FFC 接口、电容和 12 × 6 mm 插头外廓；检查结果位于 `reports/direct-usb-mechanical.json`。

接口板为 24 × 52 × 0.8 mm，安装孔为四个 1.6 mm 孔，使用头径不超过 2.5 mm 的 M1.4 塑料自攻螺丝作为候选固定方案；导孔、螺丝长度、保持力与插拔受力需要首件验证。内部仓位底面最低 z=2.8 mm。不要用厚胶带或泡棉代替 USB 插拔的机械支撑。

当前射频基线是**非金属化 PC 外壳**。铝壳需单独设计射频窗口，不以贴铜箔代替。载板天线禁布区为 `(6,26)–(18,44)` mm，全铜层禁止走线、过孔和覆铜；其三维上方不得擅加金属罩、导电泡棉或电池。感应组件的最终 Z 高度及与天线的距离仍需装配验证。

## 电气改动

`EC 电极 → U2/U3 选通 → U4 本地放大 → R37 串阻 → J2 排线 → C6 → nano ADC`

- 高阻 `SENSE` 与反馈网络全部留在感应主板，不经排线。
- U4 移近选通器；反馈接在串阻之前的 `AMP_OUT`，不把排线当作反馈环路。
- 主板 R37=47 Ω 隔离输出与线缆负载；接口板 C6=1 nF C0G/NP0 在 ADC 侧与 GND 相连。实际稳定性和采样建立时间需示波器检查。
- J2 为 24 针 0.5 mm FH12，ADC 使用 20 针，19/21 针均接地。排线不携带高阻 SENSE、USB D+/D− 或 5 V VBUS。
- 使用同针号一对一的电缆连接，但接触面/插座翻面不能凭外观推断；断电逐针测通后才能接电池。50 mm 线长是候选，弯曲路径尚未做完整公差验证。
- USB 的 CC、数据、ESD 和充电路径保留在原版 nice!nano 上。不要往 J2 或 BAT_SW 注入 USB 5 V。

| J2 针号 | 信号 | J2 针号 | 信号 |
| --- | --- | --- | --- |
| 1/2/4/10/16/19/21/24 | GND | 3 | VCC |
| 5–9 | ROW_DRV0–4 | 11/12/13 | MUX_A/B/C |
| 14/15 | MUX0_INH / MUX1_INH | 17/18 | DRAIN / AFE_ON_N |
| 20 | 缓冲 ADC | 22/23 | BAT_SW / RESET |

针号也保存在 `design/interconnect-map.csv`，GPIO 对应见 `design/pin-map.csv`。两块原理图和 PCB 的网络一致性由 `verify_design.py` 检查。

## 焊接与分阶段检查

1. 不连接任何电源，按两份 BOM 点料。主板先焊 0805 阻容，再焊 U2/U3、U4、Q1；R37 在主板，不在载板；C6 在载板。U4 的 6 脚为 AMP_OUT，不是直接到排线的 ADC。不要混淆 C4=220 pF 与 C6=1 nF。
2. 主板 J2 在 B 面；载板 J2、U1 在 F 面，C6 在 B 面。核对 U1 的 270° 方向，USB 口必须朝载板前端和机壳开口。先核对原理图与实物模块的全部引脚再焊；禁止照旧 A1 空格布局安装。
3. 焊电池插座 J1、SW1 电源开关与 SW2 复位线束。电池暂不接。先验证模块单独的 USB 枚举和刷写，再连接已逐针确认的排线。
4. 不接电池，以限流/可观察电流的 USB 供电检查 VCC 约 3.3 V、GND、AFE_3V3 门控与异常发热。出现持续限流立即断开，不提高限流硬顶。
5. 刷校准版，用示波器比较 AMP_OUT 与 ADC，确认两组 MUX 不同时使能、输出不饱和、采样能建立。分别记录 USB、BLE 发射和 USB 充电三种工况的全键原始 ADC/噪声，之后才校准阈值。
6. 检查受保护单节电池的真实极性，再测试电池独立启动和充电。路径为 `J1.1 → SW1 → J2.22 → U1.24`，负极接 GND。保持模块默认低电流充电配置，暂不启用快充跳线；电缆、接点和电池规格都未批准快充。
7. NIZ 轴体、橡胶碗和锥簧为机械装配，**锥簧不焊接到电极**。先做 fit coupon，确认 housing 卡扣、稳定器和全行程，再装整板。主板 1.6 mm、定位板 1.6 mm、6 mm 间距仍是待实物确认的候选。
8. USB shell 运行 `ec kscan0 calibration start`，按提示全松开和按遍 61 键，再执行 `export`、`save`。保存导出并断电检查恢复，然后刷普通版，保留 settings 分区。

验收须覆盖逐键按下/松开、长按、同时多键、空闲首键、USB/BLE 切换与重连、低电量和充电；装上最终外壳、稳定器、线缆和电池后重测。只有这些实测通过，才能说改位未导致可观察的电气退化。

## 复现与已知边界

普通 Python：`generate_schematic.py`（两板）、`generate_firmware.py`。KiCad 10 Python：`generate_pcb.py`（两板）；默认拒绝覆盖已布线 PCB，仅在一次性副本内用 `--overwrite-routed` 重新生成未布线种子。主板再运行 `prepare_routing.py`、`import_routing.py UnextendedEC --proxy --session UnextendedEC`，导出 `UnextendedEC-routed-candidate.kicad_pcb`；接口板用 `import_routing.py UnextendedEC-controller` 导入。两份已保留的 `.ses` 按网络名导入走线，不替换原生元件位置；必须重新运行原生 DRC，不能把路由器结果直接当作验收。CadQuery：`generate_mechanical.py`、`generate_usb_bay.py`；Blender：`render_usb_bay.py`。固件仍使用冻结 west manifest、同一 nice!nano v2 GPIO 和两份 UF2；模拟回归不代表实物验证。

原厂参考：[nice!nano 规格](https://nicekeyboards.com/nice-nano/)、[引脚](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/)、[OPA350](https://www.ti.com/lit/ds/symlink/opa350.pdf)。渲染中的模块是尺寸包络，不是厂商完整 STEP。当前不提供已放行的整机生产包。
