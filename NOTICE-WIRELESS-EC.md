# Wireless EC development attribution

The original Unextended design and its licence remain in `LICENCE.md`.
Wireless EC additions are engineering prototypes; they are not released for fabrication.

- V1 case: 4pplet, [Case_V1 release](https://github.com/4pplet/Unextended/releases/tag/Case_V1), `Unextended_V1_220331.step`, downloaded 2026-10-23. Retained as an unmodified reference.
- GH60 outline and 26 clamp holes: Cipulot EC60, [4pplet fork](https://github.com/4pplet/EC60), commit `b9c04625bb9944f6fb806aa571da8592cdff8565`. Reference PCB is unmodified; MIT text in `licenses/EC60-MIT.txt`.
- EC scanner: Pete Johanson and contributors, [EC support module](https://github.com/petejohanson/ec-support-zmk-module), pinned commit in `firmware/config/west.yml`. Source fetched by west; original SPDX notices retained. Hash-checked patch supplied separately.
- Circuit, schematic/firmware generators, footprints, regression harness and scanner corrections adapted from the local YAKB project, copyright 2026 YAKB contributors. MIT text in `licenses/YAKB-MIT.txt`. New ANSI geometry, integrated module placement, an earlier bench carrier and build/check scripts are maintained here. Firmware targets a real nice!nano v2; a generic clone is not assumed pin/electrically identical.
- KiCad standard footprints retain their upstream KiCad library attribution. The EC electrode footprint is inherited through YAKB from Cipulot's EC library; preserve the upstream MIT notice.

The A2 design mounts the module on a low USB-bay carrier and exposes its original USB-C socket directly. The sensing board carries the local analog front end; J2 is a custom GPIO/power/buffered-ADC FFC, not USB or high-impedance SENSE. The internal V1 pocket is modified; the original case reference remains unchanged. Module and plug envelopes are not vendor STEP models or physical qualification. No endorsement by Unextended, NIZ, nice!nano or ZMK maintainers is implied.
