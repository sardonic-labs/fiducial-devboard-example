# Use Report 1 — RP2040 Breadboard Devboard

**Date:** 2026-08-25
**Author:** AI agent (mimo-v2-pro)
**Project:** `fiducial-devboard-example`
**Scope:** Full schematic generation and verification of an RP2040 devboard

---

## 1. What I hand-rolled that fiducial should have provided

### 1.1 Schematic generator (`generate_schematic.py` — 764 lines)

The biggest gap. I wrote a Python script that programmatically builds a KiCad 10 `.kicad_sch` file by emitting raw S-expressions. This includes:

- Symbol placement with correct `(at x y rotation)` format
- Wire routing with `make_wire()` that handles float precision (`round(x, 4)`)
- Label placement with correct justification
- Power symbol placement (GND, +3V3, PWR_FLAG)
- No-connect markers
- Full `lib_symbols` section copied from library files
- UUID generation for every object

**What fiducial should provide:** A schematic generation API or template system. The `authoring.md` skill says "connect with labels, not long wires" but provides no tooling to actually place components and labels programmatically. An AI agent building a schematic from scratch has to reverse-engineer the KiCad S-expression format, which is undocumented outside the file itself.

Suggested API:

```python
from fiducial import SchematicBuilder

sch = SchematicBuilder("RP2040 Breadboard Devboard")
sch.add_symbol("MCU_RaspberryPi:RP2040", "U1", x=152.4, y=101.6)
sch.add_wire(x1, y1, x2, y2)
sch.add_label("GPIO0", x, y, rotation=0)
sch.add_power("GND", x, y)
sch.add_nc(x, y)
sch.export("rp2040-devboard.kicad_sch")
```

### 1.2 Debug scripts (12 scripts, ~500 lines total)

I wrote these scripts to trace connectivity problems that fiducial's tools couldn't diagnose:

| Script | Purpose |
|--------|---------|
| `check_all_nets.py` | Parse netlist, list all nets with their pins |
| `check_label_positions.py` | Find all labels and their (x,y) coordinates |
| `check_pin_positions.py` | Find pin endpoints in lib_symbol definitions |
| `check_wires.py` | Find all wires in a coordinate region |
| `check_j1_wiring.py` | Trace USB-C connector wire topology |
| `check_nets.py`, `check_nets2.py` | Debug specific net membership |
| `check_netlist.py` | Parse and filter netlist sexpr |
| `check_pins.py` | Check pin connectivity for a component |
| `check_libs.py` | Extract pin info from lib_symbols |
| `check_usb_lib_pins.py` | USB-C pin position verification |
| `check_usb_pins.py` | USB-C pin net verification |
| `debug_sch.py` | General schematic debugging |

**What fiducial should provide:** Diagnostic commands that answer common debugging questions:

- `fiducial wire-trace <sch> <ref> <pin>` — show what net a pin is actually on, and what label/wire connects to it
- `fiducial label-map <sch>` — dump all labels with coordinates, grouped by net name
- `fiducial overlap-check <sch>` — find wires from different nets that share a point
- `fiducial pin-positions <sch> <ref>` — show actual pin endpoints in schematic space

### 1.3 Netlist-to-schematic debugging loop

The check-intent tool tells you *what* is wrong but not *why*. When U1 pin 47 shows `/QSPI_SCLK` instead of `/USB_DP`, I had to manually:

1. Find the label coordinates in the schematic
2. Find the wire endpoints
3. Check if wires from different nets share a point
4. Check if labels land on the wrong wires

This is a 30-minute investigation per bug. A single `fiducial overlap-check` command would have found it instantly.

---

## 2. What was annoying to use or should change

### 2.1 check-intent doesn't handle NC pins (fixed in fiducial.py)

**Bug:** When intent.csv has `expected_net=NC` and the pin has a no-connect marker, check-intent reports `MISSING` instead of `ok`. NC pins don't appear in the netlist — that's the point.

**Fix applied:** Added `if want.upper() == "NC": status = "ok"` to `fiducial.py:361-363`.

**Recommendation:** This should be upstream behavior. NC is a valid expected state.

### 2.2 Lint's single-use label warnings are noise

Lint flags labels that appear only once as "likely a typo." But single-use labels are intentional in many cases:

- QSPI_SD2 and QSPI_SD3 — these go to the flash's WP# and HOLD# pins, which are tied to +3V3 in basic SPI mode. The RP2040 side has labels; the flash side doesn't. That's a design choice, not a typo.
- Power labels on decoupling cap legs
- Crystal load cap labels

**Recommendation:** Add a suppression mechanism — either a `// no-lint` comment in the schematic, a list of allowed single-use labels in rules.csv, or a severity level (warning vs. info).

### 2.3 No way to validate before the full netlist export

The workflow is: edit schematic → `kicad-cli sch export netlist` → `check-intent`. But kicad-cli takes 5-10 seconds, and check-intent only catches connectivity errors. I couldn't validate:

- Whether a label is at the right coordinates
- Whether two wires overlap
- Whether a wire endpoint touches a pin

**Recommendation:** A lightweight pre-check that parses the `.kicad_sch` directly without invoking kicad-cli. Something like `fiducial quick-check <sch>` that validates basic structural properties.

### 2.4 KiCad 10 format gotchas are undocumented

Several KiCad 10 specifics caused silent failures:

| Gotcha | Impact |
|--------|--------|
| `(at x y)` requires 3 params `(at x y rot)` | Schematic fails to load in kicad-cli |
| Local labels get `/` prefix in netlist (`GPIO0` → `/GPIO0`) | check-intent comparison fails if CSV doesn't match |
| Hidden pins create 5.08mm gaps in symbol pin spacing | Right-side GPIO labels misaligned |
| Power symbols have hidden pins for net attachment | Can't just place a GND symbol and expect it to connect |
| `justify left bottom` on labels affects text rendering but not connection point | Confusing when debugging label placement |

**Recommendation:** Add a `fiducial format-check <sch>` that catches these before export. Or at minimum, document them in `authoring.md`.

### 2.5 The intent-first workflow assumes manual editing

The `authoring-workflow.md` says "write intent rows FIRST, then place, annotate, wire." But when generating schematically, intent and code are co-developed. The workflow should support:

1. Write intent.csv
2. Write generator code
3. Generate schematic
4. Verify
5. Fix generator, regenerate
6. Re-verify

This is a code iteration loop, not a hand-edit loop. The skill files assume the latter.

### 2.6 No visual feedback during generation

I had to open the schematic in KiCad's GUI repeatedly to see if labels overlapped. There's no programmatic way to check visual layout quality.

**Recommendation:** The `render` command exports SVG, but it's not integrated into the verify loop. A `fiducial layout-report <sch>` that lists component bounding boxes and detects overlaps would help.

---

## 3. How to solve the overlap issue

### 3.1 What happened

The schematic has a USB-C connector (J1) with D+/D- pins, and an RP2040 (U1) with QSPI and USB pins on the left side. The wire routing created a situation where:

- A wire from the USB connector's D+ pin endpoint to a `USB_DP_RAW` label shared a coordinate with a wire from the RP2040's QSPI_SCLK pin to its label
- KiCad treats shared coordinates as electrical connections
- This created a short circuit between `USB_DP_RAW` and `QSPI_SCLK` nets

The overlap was invisible in the schematic — the wires looked like they were on different paths. But KiCad's connectivity engine uses exact coordinate matching, and two wires sharing a point (even at a T-junction) creates a net connection.

### 3.2 Root cause

KiCad's netlist is built from **physical wire connectivity**, not logical label names. A wire from (127, 99.06) to (114.3, 99.06) connecting to QSPI_SCLK, and another wire from (127, 97.79) to (127, 99.06) connecting to USB_DP, share the point (127, 99.06). That point becomes a junction, merging the two nets.

This is correct KiCad behavior — the schematic accurately reflects the wiring. The problem is that the generator created wires that physically overlap without the developer (me) realizing it.

### 3.3 Proposed solutions

#### A. Overlap detection in fiducial (recommended)

Add a new command:

```
fiducial overlap-check <project.kicad_sch>
```

This would:
1. Parse all wires from the schematic
2. Build a graph of wire endpoints and shared coordinates
3. For each connected component (net), collect all labels
4. Flag any connected component that has **two or more different label names**
5. Report: "Net `/QSPI_SCLK` overlaps with `/USB_DP` at (127, 99.06)"

This is a pure S-expression parsing task — no kicad-cli needed. It would catch the bug in seconds.

#### B. Coordinate hash validation in the generator

When writing `generate_schematic.py`, maintain a set of `(x, y) -> net_name` mappings. Before emitting any wire endpoint, check if that coordinate is already used by a different net. If so, warn or error.

```python
class WireTracker:
    def __init__(self):
        self.points = {}  # (x, y) -> net_name
    
    def add_wire(self, x1, y1, x2, y2, net):
        for pt in [(x1, y1), (x2, y2)]:
            if pt in self.points and self.points[pt] != net:
                raise OverlapError(
                    f"Wire for net '{net}' at {pt} "
                    f"overlaps with net '{self.points[pt]}'"
                )
            self.points[pt] = net
```

#### C. Grid-aware routing

Use a routing grid (e.g., 1.27mm) and assign each net a dedicated "track layer" in the schematic. Wires for different nets can never share grid points because they're on different conceptual layers. This is how professional schematic editors avoid accidental shorts.

For a generator, this means:
- Assign each net a unique Y offset from a base position
- Route horizontal wires on the net's dedicated Y line
- Vertical "risers" connect from the component pin to the net's Y line
- Never allow two risers to share an X coordinate at the same Y

#### D. Post-generation DRC via netlist comparison

After generating the schematic and exporting the netlist, compare each net's pin list against the expected intent. If a net has unexpected pins (like QSPI_SCLK appearing on the USB_DP_RAW net), flag it immediately.

This is essentially what check-intent already does, but the overlap detection would need to be more granular — checking not just "is the right pin on the right net" but "are there unexpected pins on this net."

---

## Summary

| Area | Status | Priority |
|------|--------|----------|
| Schematic generator API | Missing — hand-rolled 764 lines | High |
| NC pin handling in check-intent | Fixed locally | High |
| Overlap detection command | Missing — would have caught the main bug | High |
| Debug/diagnostic commands | Missing — hand-rolled 12 scripts | Medium |
| Single-use label suppression | Missing — noisy warnings | Medium |
| Pre-check without kicad-cli | Missing | Medium |
| KiCad 10 format docs | Incomplete in authoring.md | Low |
| Code-gen workflow support | Skill files assume hand-editing | Low |

The biggest win would be an `overlap-check` command. The overlap bug cost 2+ hours of debugging that a 50-line S-expression parser could have caught in milliseconds.
