# PLAYBOOK — RP2040 Devboard Agent Workflow

This document guides an AI agent through designing an RP2040 devboard using fiducial's verification tooling. Follow each phase in order. Do not skip ahead — each phase gates the next.

---

## Phase 0: Bootstrap

**Goal:** Environment verified, tools ready.

1. Read `fiducial/AGENTS.md` — this is the entry point for all fiducial instructions.
2. Read `fiducial/README.md` — understand the toolset and philosophy.
3. Run the environment check:

```sh
python fiducial/scripts/fiducial.py doctor
```

4. Confirm `kicad-cli` is available. If not, stop — you cannot proceed without it.

**Gate:** `doctor` exits 0.

---

## Phase 1: Design Intent

**Goal:** `intent.csv` written from datasheet, before any schematic work.

1. Open the RP2040 datasheet (or use `fiducial/skills/reference/datasheets.md` for guidance on reading it correctly).
2. Create `intent.csv` with one row per critical connection:

```
ref,pin,expected_net
U1,1,+3V3
U1,46,/USB_DM
U1,47,/USB_DP
U1,20,/XIN
U1,19,/XOUT
U1,23,SWDIO
U1,24,SWCLK
```

3. Cover at minimum:
   - Every RP2040 power pin → correct rail
   - USB D+/D− → correct pins (no swap)
   - Crystal XIN/XOUT → correct pins
   - SWD pins → debug header
   - Boot pin → correct pull state

4. Verify the CSV by running:

```sh
python fiducial/scripts/fiducial.py check-intent <project>.kicad_sch intent.csv
```

(Will fail until schematic exists — that's fine. The CSV is your source of truth.)

**Gate:** `intent.csv` exists and covers all critical connections.

---

## Phase 2: Schematic Authoring

**Goal:** Complete `.kicad_sch` with all blocks wired.

1. Read `fiducial/skills/schematic/authoring.md` before any edit.
2. Author the schematic block by block, in this order:
   - **Power section** — LDO, input/output caps, fuse, power LED
   - **RP2040 MCU** — all power pins decoupled, ground pins connected
   - **USB** — connector, CC resistors, series resistors, D+/D−
   - **Crystal** — crystal, load caps, short traces
   - **SWD header** — SWDIO, SWCLK, GND, 3V3
   - **GPIO headers** — break out as many pins as practical
   - **Buttons** — BOOT, USER, RESET with pull-ups/pull-downs
   - **LEDs** — power LED, user LED

3. After each block, run:

```sh
python fiducial/scripts/fiducial.py lint <project>.kicad_sch
python fiducial/scripts/fiducial.py erc <project>.kicad_sch
```

4. Fix any violations before moving to the next block. Do not batch edits across blocks without verifying.

**Gate:** `lint` and `erc` both exit 0.

---

## Phase 3: Verify Connectivity

**Goal:** Every pin wired to the correct net, proven by tooling.

1. Run the full intent audit:

```sh
python fiducial/scripts/fiducial.py check-intent <project>.kicad_sch intent.csv
```

2. Every `MISSING` or `WRONG` row is a bug. Fix the schematic, not the CSV.
3. Spot-check critical parts:

```sh
python fiducial/scripts/fiducial.py pins <project>.kicad_sch U1
python fiducial/scripts/fiducial.py nets <project>.kicad_sch
```

4. Check specifically:
   - Every power pin reaches a power net (no floating VDD)
   - Crystal pins on the right nets
   - USB D+/D− not swapped
   - SWD header wired to SWD pins, not neighboring GPIO
   - Boot pin pull state correct

5. Check for orphan nets (single-pin connections):

```sh
python fiducial/scripts/fiducial.py check-intent <project>.kicad_sch intent.csv --orphans
```

6. Run the full check again after any fix.

**Gate:** `check-intent` exits 0, no orphans on critical nets.

---

## Phase 4: PCB Layout

**Goal:** Component placement and routing complete.

1. Read `fiducial/skills/pcb/layout.md` before starting.
2. Set up the board:
   - 2-layer, 33×80 mm outline (or per brief)
   - Design rules matching your fab (JLC-class: 0.2 mm trace, 0.15 mm clearance)
3. Place components:
   - RP2040 centered
   - USB connector on board edge
   - Crystal close to MCU, short traces
   - Decoupling caps at power pins
   - Headers along edges
4. Route signals:
   - Power: wide traces or pour
   - USB: differential pair, same length, over ground
   - Crystal: short, guarded, nothing else nearby
   - SWD/GPIO: standard routing
5. Add ground pour on bottom layer, stitch with vias.
6. Add 3 asymmetric fiducials and 4 mounting holes.
7. Silkscreen: designators, pin-1 marks, board name.

**Gate:** Visual inspection in KiCad or via `render`.

---

## Phase 5: DRC

**Goal:** Zero DRC violations.

1. Read `fiducial/skills/pcb/drc-workflow.md` before starting.
2. Run DRC:

```sh
python fiducial/scripts/fiducial.py drc <project>.kicad_pcb
```

3. Fix violations one category at a time:
   - Clearance violations → increase spacing or move traces
   - Unrouted nets → complete routing
   - Silkscreen overlap → move text
4. Re-run DRC after each batch of fixes.
5. When clean, render and inspect:

```sh
python fiducial/scripts/fiducial.py render <project>.kicad_sch <project>.kicad_pcb --outdir renders/
```

6. Visually inspect both copper layers, silkscreen, and drill hits.

**Gate:** `drc` exits 0, renders inspected.

---

## Phase 6: Report

**Goal:** Document what happened for fiducial improvement.

1. Open `REPORT.md` (template provided).
2. Fill in every section honestly:
   - What worked well
   - What was painful or broke
   - Tooling gaps
   - Suggested changes to fiducial
   - Suggested inclusions for future examples
   - Agent experience notes
3. Be specific — include command outputs, error messages, and file paths.

**Gate:** `REPORT.md` complete.

---

## Verification Summary

| Phase | Gate Command | Expected Exit |
|-------|-------------|---------------|
| 0 | `doctor` | 0 |
| 1 | `intent.csv` exists | — |
| 2 | `lint` + `erc` | 0, 0 |
| 3 | `check-intent` | 0 |
| 4 | Visual inspection | — |
| 5 | `drc` | 0 |
| 6 | `REPORT.md` complete | — |

---

## Tips

- **One edit at a time, then verify.** Do not batch ten edits before running `lint`.
- **Never guess pinouts.** Always check the datasheet. fiducial's tools catch wrong pins; your memory does not.
- **Labels > wires.** Use net labels for everything except short local connections.
- **Exit codes are gates.** A non-zero exit means stop and fix. Do not proceed.
- **Read before editing.** KiCad files are S-expressions. Understand the section you're changing.
