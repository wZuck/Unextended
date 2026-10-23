# Unextended EC soldering and staged power-up

> **Historical A1 only. Use [A2 soldering and staged checks](direct-usb-A2.md#soldering-and-staged-checks); do not assemble the obsolete spacebar module layout below.**

[简体中文](soldering.zh-CN.md) · [Engineering notes](wireless-niz.md)

For the A1 integrated nice!nano v2 mainboard. **Routing and fabrication qualification are incomplete. This is a first-article procedure draft, not instructions for a released kit.** Require native DRC/zero-unconnected, component review and case-clearance approval before making the circuit. The older `-controller` carrier is not used; do not buy an FFC.

## Preparation and assembly

Use a temperature-controlled iron, suitable tip/solder/flux for 0805 and SOIC, tweezers, magnification, multimeter and current-limited/monitored USB supply. Analog debugging also needs an oscilloscope. Follow the actual solder, PCB and component process limits rather than a universal temperature. Never solder with USB or battery connected.

Check [`BOM.csv`](../hardware/BOM.csv). Components mount on B; the electrodes/springs face F. This **mirrored bottom-view component-center diagram is not a pad-orientation reference**. Use the native PCB, schematic and exact purchased part's datasheet together.

![Bottom component centers](../renders/assembly-bottom.svg)

| Group | Parts and values |
| --- | --- |
| Row drivers | R1–R5: 100 Ω, not 100 kΩ |
| Column bleed | R10–R24: 100 kΩ |
| Feedback/discharge | R30: 100 kΩ; R31/R32: 1 kΩ; nominal non-inverting gain 101 is not a measured signal gain |
| Startup/gating | R33–R35: 100 kΩ; R36: 1 kΩ; do not omit pull-ups |
| Decoupling | C1–C3: 100 nF; C5: 1 µF, nonpolar ceramic, appropriate voltage rating |
| Sensing capacitor | C4: **220 pF**, not 220 nF, C0G/NP0; first-article tuning required |
| ICs | U2/U3: CD74HC4051M96; U4: OPA350UA; do not substitute HCT or OPA2350 blindly |
| PMOS | Q1: AO3401A, SOT-23, 1=G/2=S/3=D; verify the actual supplier datasheet |
| Connections | J1: JST PH2; SW1 battery switch harness; SW2 normally-open reset harness, 2.54 mm solder holes rather than a vendor-specific switch footprint |
| Controller | U1: genuine nice!nano v2, on B; module/header/USB-plug case clearance not yet qualified |

1. Inspect bare-board copper, masks, flatness and holes. Do not tin, sand or apply foil to EC electrodes. Check for obvious power-to-ground shorts.
2. Solder passives first; inspect each group for wrong values and bridges. Keep the high-impedance SENSE node free of residue and debris.
3. Tack one IC pin, verify orientation/alignment, then finish U2/U3/U4/Q1. U2/U3 pin16=VCC, pins7/8=GND. U4 pin7=AFE_3V3, pin4=GND, pin3=SENSE, pin6=ADC. Datasheet top views are mirrored relative to a PCB bottom view.
4. Install J1 and insulated, strain-relieved SW1/SW2 harnesses; no battery yet. SW1 interrupts battery positive. SW2 connects RESET to GND, not power.
5. Before permanently installing U1, check module USB enumeration/flashing separately and verify native pad mapping: pad21=VCC, pad23=GND, pad24=BAT_SW, pad22=RESET, pad18=D19/P0.02. These are this PCB's physical pad numbers, not nRF package pins. Header/socket height requires case qualification; no approved socket height is specified.
6. Inspect bridges, joints and solder balls. Clean the PCB solder area and dry fully; keep cleaners away from housings, domes, lubricant and batteries.

Vendor references: [nice!nano installation](https://nicekeyboards.com/docs/nice-nano/getting-started/), [pinout](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/), [TI CD74HC4051](https://www.ti.com/lit/gpn/CD74HC4051), [TI OPA350](https://www.ti.com/lit/ds/symlink/opa350.pdf). Recheck the exact purchased orderable part/package.

## Staged checks

Battery path: `J1.1 BAT_RAW → SW1 → BAT_SW → U1.24`; `J1.2 → GND`. A fitting JST housing does not establish polarity: meter the actual cell plug.

| Stage | Conditions | Check / stop condition |
| --- | --- | --- |
| A | No USB/battery; U1 not fitted | No obvious BAT_RAW, VCC or AFE_3V3 shorts to GND; correct switch operation. Repair before power. |
| B | U1 installed; USB current-limited; SW1 off; no battery | USB enumeration/reset, VCC approximately 3.3 V, no abnormal heat or sustained limiting. Disconnect on failure; do not raise the limit to force operation. |
| C | USB/calibrator, no battery | AFE_ON_N gating, U4 supply/output, only one MUX enabled at a time, ADC not stuck saturated. Check nets/values/timing/contamination before adjusting thresholds. |
| D | Disconnect USB, connect verified protected single-cell battery, SW1 on | Battery boot; reconnect USB to check charging; SW1 off disconnects battery path. Disconnect immediately for abnormal heat/current. |

BAT_SW is a single-cell lithium battery domain, **never 5 V**. Match cell capacity/charge-current limits to the module's charging configuration; do not modify fast-charge settings without verifying the cell. Insulate from sharp leads/screws and provide swelling space; do not compress the pouch with foam.

## EC mechanics and calibration

EC1–EC61 are sensing electrodes, not MX solder pads. **Do not solder cone springs to the PCB.** NIZ housings/sliders, domes and centered springs are retained mechanically. Test actual parts with `niz-fit-coupon.dxf` first. The 1.6 mm plate, 14 mm housing cuts and 6 mm spacing are candidates, not universal NIZ compatibility.

Qualify clips, stabilizers, preload and full travel. Assemble stabilizers/housings, sliders, domes, springs, PCB and clamps with a fixture that prevents spring displacement. Tighten gradually/evenly; do not use screws to flatten a warped board. Test on a nonconductive fixture before battery/case installation; nearby fingers/metal alter the baseline.

Flash `unextended-ec-calibrator.uf2`, run `ec kscan0 calibration start` in USB CDC shell, follow released/all-61-pressed prompts, then `ec kscan0 calibration export` and `ec kscan0 calibration save`. Retain export, power-cycle to check persistence, then flash normal firmware without erasing settings. See [firmware notes](wireless-niz.md#firmware).

Verify each press/release/hold, modifiers, stabilizers and simultaneous keys; then BLE/USB switching, reconnects, idle first taps, low battery and charging. Repeat with the final case, shielding, battery and plate; bare-board calibration is insufficient. Runtime, latency, temperature drift, RF and charging temperature still require measured records.

## Shielding boundaries

Metal near electrodes adds parasitic capacitance; metal near antennas changes RF behavior. Insulation prevents shorts but does not remove those effects.

| Material | Candidate use | Restrictions |
| --- | --- | --- |
| Local ground copper/guards | Digital regions and controlled return paths | Never fill EC inner-layer or antenna keepouts |
| Copper/aluminum foil | Insulated, securely grounded local digital-region experiments | Not directly under electrodes or around antenna; ordinary solder is not a reliable aluminum bond |
| Metal shield can | Later digital/power-region option | Needs clearance/ground/RF testing; no released solder frame or lid file exists |
| Polyimide/PET film | Electrical isolation | Not EMI shielding; avoid changing EC stack height or filling RF window |
| Foam/silicone | Local vibration/contact protection | Not EMI shielding; do not compress battery/domes, touch electrodes or obstruct heat sources |

Provisional all-layer RF window in top-view coordinates: x=103–120, y=78.8–90.8 mm; preserve the plate opening and inspect the case below the module. Compare raw ADC noise and travel before/after each material change under USB, BLE and charging, then recalibrate. Foil is not approval for a fully enclosed aluminum wireless build.
