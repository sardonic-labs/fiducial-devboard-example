# fiducial-devboard-example

Testing ground for [fiducial](fiducial/) — hand a fresh AI agent a blank repo with fiducial as a submodule, and see how well it designs a devboard when steering + verification tooling are present from the first turn.

## Layout

```
fiducial/       verification skills submodule (MIT) — instruction library +
                zero-dependency checkers: lint → erc → check-intent → drc → render
PLAYBOOK.md     step-by-step workflow for the agent
REPORT.md       template for post-run findings
```

## Design Brief — RP2040 Devboard

Design a minimal RP2040 development board with the following blocks:

### Power
- USB-C connector supplying 5V VBUS
- 3.3V LDO regulator (AMS1117-3.3 or equivalent) from VBUS → 3V3
- Bulk decoupling: 10 µF on input, 10 µF on output
- 100 nF ceramic on every RP2040 power pin (VDDIO, DVDD, AVDD)
- Power LED (green) on 3V3 rail with current-limiting resistor
- Polyfuse or 500 mA resettable fuse on VBUS

### USB
- USB-C connector with CC1/CC2 pulldown resistors (5.1 kΩ to GND)
- D+ and D− connected to RP2040 USB_DP (pin 47) and USB_DM (pin 46)
- 22 Ω series resistors on D+ and D−

### Clock
- 12 MHz crystal (HC-49S or 3215 package)
- 20 pF load capacitors on XIN (pin 20) and XOUT (pin 19)
- Crystal traces short, no other signals nearby

### Debug
- SWD header (2×5 pin, ARM standard): SWDIO (pin 23), SWCLK (pin 24), GND, 3V3
- Optional: nRST pulled high through 10 kΩ with reset button to GND

### GPIO Access
- 2×20 pin headers breaking out RP2040 GPIO0–GPIO29
- Pin 1 marked on silkscreen
- Decouple header power pins with 100 nF

### Buttons
- BOOT button: pull GP29 low (active boot-on-reset when held at reset)
- USER button: general-purpose input with debouncing capacitor

### Indicators
- User LED on GP25 (internal LED on some modules, or external with resistor)

### Resets
- 10 kΩ pull-up on nRST, 100 nF cap to GND, reset tactile switch to GND

### PCB
- 2-layer board, 33×80 mm (Arduino Nano form factor)
- JLC-class DRC rules (0.2 mm trace, 0.15 mm clearance, 0.3 mm via drill)
- Ground pour on bottom layer
- 3 asymmetric fiducials, 4 mounting holes (M3)
- Silkscreen: designator labels, pin-1 marks, board name, revision

## How to Work Here

1. Read `fiducial/AGENTS.md` and `fiducial/README.md` before anything else.
2. Run `python fiducial/scripts/fiducial.py doctor` to verify your environment.
3. Write design intent as `intent.csv` (`ref,pin,expected_net`) from the datasheet **before** wiring the schematic.
4. Author the schematic under fiducial's rules; gate every step: `lint → erc → check-intent`; exit codes are gates, not suggestions.
5. Only after all checks pass: layout, `drc` until clean, `render`, inspect.
6. Write `REPORT.md` with your findings (see template).

## Submodule

```
fiducial/   verification skills submodule (MIT) — instruction library +
            zero-dependency checkers: lint → erc → check-intent → drc → render
```

Update with:

```sh
git submodule update --remote fiducial
```
