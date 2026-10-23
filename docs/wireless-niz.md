# Unextended V1 wireless NIZ development

> **Historical A1, superseded. Use [A2 native direct USB](direct-usb-A2.md). The spacebar module, no-FFC architecture and USB extension below are obsolete.**

Confirmed target: V1, ANSI 61 keys, 6.25u spacebar, MX keycaps, Bluetooth BLE plus USB input/charging; no dongle. This is an A1 integrated engineering design, not a fabrication release. Native sources, mechanical candidates, compiled firmware and check reports are delivered; physical EC, RF, runtime, charging and case fit remain untested.

The 285 × 94.6 × 1.6 mm four-layer mainboard has 61 EC cells, two CD74HC4051 multiplexers, an OPA350 amplifier, switched amplifier power and 26 EC60 clamp holes. Its 5 × 15 matrix masks unused physical columns. A nice!nano v2 module mounts directly on the back at candidate center x=95, y=84.8 mm, beneath the left wing of the spacebar. No FFC is used. The module supplies the radio, USB, regulator and charging circuit; this is not a bare-chip RF design.

The earlier bottom-right placement conflicted with RCtrl but did not rule out every integrated location. The revised mainboard has an all-copper-layer keepout at x=103–120, y=78.8–90.8 mm and a matching plate window. This is provisional, not measured antenna performance. The earlier 55 × 24 mm `UnextendedEC-controller.*` is retained only for bench research, is not part of the build BOM, and has no mating FFC connector on this mainboard. Its ADC filter is not present on the integrated board. Module underside, battery, USB plug and O-ring clearances are unqualified. The actual V1 STEP is included; no assembled-case clearance is claimed. Prefer polymer V1; aluminum needs a separately tested RF window.

USB uses the module's own USB-C socket and a passive data extension to the case opening. The exact extension and bend space are unresolved; no C3 JST interface is provided. Never connect C3 VBUS to BATTERY+. Battery J1 connects through SW1 and BAT_SW to the module's battery terminal; charging requires SW1 on. A protected 750 mAh, approximately 3 mm cell is a candidate, subject to pocket, polarity and swelling clearance checks.

The 1.6 mm candidate plate uses 14 mm rounded cutouts, plate-mount stabilizer slots and the EC60 clamp pattern. The provisional 6 mm PCB-top-to-plate-bottom dimension requires actual NIZ housing/dome preload measurement. Cut the fit coupon before a full plate. Verify clamp nuts, housing, stabilizers and O-ring travel physically.

## Firmware

Normal and USB calibration-shell UF2 images are in `firmware/prebuilt/`, with hashes. Both compiled locally for `nice_nano@2.0.0/nrf52840/zmk`; neither was flashed to hardware. D19/P0.02/AIN0 uses logical ADC channel 1, distinct from battery channel 0.

Fn+1/2/3 selects BLE profiles; Fn+4 clears the selected pairing; Fn+5/6 chooses USB/BLE; Fn+H/J/K/L provides arrows; Fn+Esc enters the bootloader. Both transports are enabled, with one selected output endpoint. Scan waits are 4/8/12 ms, not measured frame times. Deep sleep is disabled to retain periodically scanned EC wake; no months-long standby claim is made.

The hash-checked EC patch restores fast polling on a first raw transition and guards invalid calibration/zero-noise division. The regression runs actual patched C functions with mocked inputs: 960 timing scenarios, all 61 presses/releases and battery/EC ADC allocation. It does not measure hardware latency or current.

After power and analog waveform checks, flash the calibrator, connect its USB CDC shell and run `ec kscan0 calibration start`. Release all keys for initial sampling, then press all 61 keys as prompted. Export with `ec kscan0 calibration export`, save with `ec kscan0 calibration save`, power cycle and verify restoration before flashing the normal image. Preserve the settings partition.

## Reproduction and release gates

Run schematic/firmware generators with Python. Use KiCad 10 Python for `generate_pcb.py` and `verify_design.py`; `--controller` only regenerates the older bench carrier. The PCB generator overwrites the unrouted seed: do not run it over manual routing. Install `requirements-cad.txt` for `generate_mechanical.py`. Generate KiCad XML netlists as `reports/schematic.net.xml` and `reports/controller.net.xml` before verification.

Initialize a separate west workspace from `firmware/west-lock.yml` as `config/west.yml`, then `west init -l config` and `west update`. In `zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5`, mount the workspace at `/work` and repository at `/repo`, then run `build_firmware.py`, `test_ec_driver.py`, and `package_firmware.py` with `--workspace /work`. Preparation checks upstream revision and before/after hashes before applying the patch. CI uses this flow; no remote CI run is claimed.

Complete mainboard routing/ERC/DRC/zero-unconnected checks and real V1 assembly alignment before releasing PCBA files. Verify module, battery, USB extension/plug, screw and O-ring clearances. First articles must test BLE activity, charging, low battery, temperature, idle first taps, NKRO and releases. Do not manufacture a complete keyboard from the current files. See [soldering/shielding](soldering.md), [render boundaries](renders.md), [Chinese notes](wireless-niz.zh-CN.md) and [attribution](../NOTICE-WIRELESS-EC.md). The bilingual promotional site is in `website/dist/`, with explicit development status and no purchase flow.
