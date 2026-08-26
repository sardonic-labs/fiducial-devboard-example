#!/usr/bin/env python3
"""Generate the RP2040 breadboard devboard KiCad schematic.
Uses lib_symbols from the demo-board as a reference, generates components and labels."""
import uuid, re, os

def uid():
    return str(uuid.uuid4())

# === Extract lib_symbols from demo-board ===
demo_path = os.path.join(os.path.dirname(__file__), "fiducial", "examples", "demo-board.kicad_sch")
with open(demo_path, "r", encoding="utf-8") as f:
    demo = f.read()

def extract_lib_symbol(text, name):
    pattern = rf'\(symbol "{re.escape(name)}"'
    match = re.search(pattern, text)
    if not match:
        return ""
    start = match.start()
    depth = 0
    i = start
    while i < len(text):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return ""

# Get symbols from demo-board
rp2040_sym = extract_lib_symbol(demo, "MCU_RaspberryPi:RP2040")
usb_sym = extract_lib_symbol(demo, "Connector:USB_C_Receptacle_USB2.0_16P")
ldo_sym = extract_lib_symbol(demo, "Regulator_Linear:AP2204K-1.5").replace("AP2204K-1.5", "AP2204K-3.3")
flash_sym = extract_lib_symbol(demo, "Memory_Flash:W25Q32JVSS")
r_sym = extract_lib_symbol(demo, "Device:R")
c_sym = extract_lib_symbol(demo, "Device:C")
crystal_sym = extract_lib_symbol(demo, "Device:Crystal_GND24")

# Minimal symbols not in demo-board
sw_sym = '''(symbol "Switch:SW_Push"
		(pin_names (offset 1.016))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "SW" (at 3.175 3.302 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Value" "SW_Push" (at 2.286 -3.302 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Push button switch" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "SW_Push_0_1"
			(circle (center 0 0) (radius 0.762) (stroke (width 0) (type default)) (fill (type none)))
		)
		(symbol "SW_Push_1_1"
			(pin passive line (at 0 5.08 270) (length 4.318) (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
			(pin passive line (at 0 -5.08 90) (length 4.318) (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
		)
		(embedded_fonts no)
	)'''

pwr_3v3_sym = '''(symbol "power:+3V3"
		(power)
		(pin_names (offset 0))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "#PWR" (at 0 -3.81 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Value" "+3V3" (at 0 3.81 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Power symbol creates a global label with name +3V3" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "+3V3_0_1"
			(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
			(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
			(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))
		)
		(symbol "+3V3_1_1"
			(pin power_in line (at 0 0 90) (length 0) (name "+3V3" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
		)
		(embedded_fonts no)
	)'''

gnd_sym = '''(symbol "power:GND"
		(power)
		(pin_names (offset 0))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "#PWR" (at 0 -6.35 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Value" "GND" (at 0 -3.81 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Power symbol creates a global label with name GND" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "GND_0_1"
			(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))
		)
		(symbol "GND_1_1"
			(pin power_in line (at 0 0 270) (length 0) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
		)
		(embedded_fonts no)
	)'''

pwr_flag_sym = '''(symbol "power:PWR_FLAG"
		(power)
		(pin_names (offset 0))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "#FLG" (at 1.016 1.905 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Value" "PWR_FLAG" (at 1.016 -1.905 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Power flag for ERC" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "PWR_FLAG_0_0"
			(pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
		)
		(embedded_fonts no)
	)'''

polyfuse_sym = '''(symbol "Device:Polyfuse"
		(pin_numbers (hide yes))
		(pin_names (offset 0.254))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "F" (at 0.9652 2.54 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (justify left)))
		(property "Value" "Polyfuse" (at 1.27 -2.54 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (justify left)))
		(property "Footprint" "" (at -1.524 -3.81 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Polyfuse / resettable fuse" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "Polyfuse_0_1"
			(polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
			(polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0) (type default)) (fill (type none)))
			(polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
		)
		(symbol "Polyfuse_1_1"
			(pin passive line (at -5.08 0 0) (length 2.54) (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
			(pin passive line (at 5.08 0 180) (length 2.54) (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
		)
		(embedded_fonts no)
	)'''

conn_02x03_sym = '''(symbol "Connector:Conn_02x03_Odd_Even"
		(pin_names (offset 1.016))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J" (at 7.62 5.08 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Value" "Conn_02x03_Odd_Even" (at 7.62 2.54 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Generic connector, double row, 02x03, odd/even pin numbering" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "Conn_02x03_Odd_Even_1_1"
			(pin passive line (at 0 7.62 270) (length 2.54) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 5.08 7.62 270) (length 2.54) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 0 2.54 270) (length 2.54) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 5.08 2.54 270) (length 2.54) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 0 -2.54 270) (length 2.54) (name "Pin_5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 5.08 -2.54 270) (length 2.54) (name "Pin_6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
			(rectangle (start -2.54 10.16) (end 7.62 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(embedded_fonts no)
	)'''

conn_01x12_sym = '''(symbol "Connector:Conn_01x12"
		(pin_names (offset 1.016))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J" (at 5.08 15.24 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Value" "Conn_01x12" (at 5.08 12.7 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Generic connector, single row, 01x12" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "Conn_01x12_1_1"
			(pin passive line (at -5.08 13.97 0) (length 2.54) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 11.43 0) (length 2.54) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 8.89 0) (length 2.54) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 6.35 0) (length 2.54) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 3.81 0) (length 2.54) (name "Pin_5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 1.27 0) (length 2.54) (name "Pin_6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -1.27 0) (length 2.54) (name "Pin_7" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -3.81 0) (length 2.54) (name "Pin_8" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -6.35 0) (length 2.54) (name "Pin_9" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -8.89 0) (length 2.54) (name "Pin_10" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -11.43 0) (length 2.54) (name "Pin_11" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -13.97 0) (length 2.54) (name "Pin_12" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
			(rectangle (start -2.54 16.51) (end 2.54 -16.51) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(embedded_fonts no)
	)'''

conn_01x06_sym = '''(symbol "Connector:Conn_01x06"
		(pin_names (offset 1.016))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J" (at 5.08 7.62 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Value" "Conn_01x06" (at 5.08 5.08 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Datasheet" "~" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(property "Description" "Generic connector, single row, 01x06" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))
		(symbol "Conn_01x06_1_1"
			(pin passive line (at -5.08 6.35 0) (length 2.54) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 3.81 0) (length 2.54) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 1.27 0) (length 2.54) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -1.27 0) (length 2.54) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -3.81 0) (length 2.54) (name "Pin_5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -6.35 0) (length 2.54) (name "Pin_6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
			(rectangle (start -2.54 8.89) (end 2.54 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(embedded_fonts no)
	)'''

ALL_LIB = "\n".join([
    rp2040_sym, usb_sym, ldo_sym, flash_sym,
    r_sym, c_sym, crystal_sym, sw_sym,
    pwr_3v3_sym, gnd_sym, pwr_flag_sym, polyfuse_sym, conn_02x03_sym,
    conn_01x12_sym, conn_01x06_sym,
])

# === Helper functions ===
def make_power_sym(ref, value, x, y, rot=0):
    u = uid()
    lib = "power:+3V3" if "+3V3" in value else "power:GND" if "GND" in value else "power:PWR_FLAG"
    x = round(x, 4)
    y = round(y, 4)
    return f'''\t(symbol
\t\t(lib_id "{lib}")
\t\t(at {x} {y} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{u}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {round(y - 2.54, 4)} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at {x} {round(y + 2.54, 4)} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x} {y} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Description" ""
\t\t\t(at {x} {y} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(pin "1" (uuid "{uid()}"))
\t\t(instances
\t\t\t(project "rp2040-devboard"
\t\t\t\t(path "/{uid()}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''

def make_sym(lib_id, ref, value, x, y, rot=0, fp=""):
    u = uid()
    x = round(x, 4)
    y = round(y, 4)
    lines = [
        f'\t(symbol',
        f'\t\t(lib_id "{lib_id}")',
        f'\t\t(at {x} {y} {rot})',
        f'\t\t(unit 1)',
        f'\t\t(exclude_from_sim no)',
        f'\t\t(in_bom yes)',
        f'\t\t(on_board yes)',
        f'\t\t(dnp no)',
        f'\t\t(uuid "{u}")',
        f'\t\t(property "Reference" "{ref}"',
        f'\t\t\t(at {x} {round(y - 2.54, 4)} 0)',
        f'\t\t\t(effects (font (size 1.27 1.27)))',
        f'\t\t)',
        f'\t\t(property "Value" "{value}"',
        f'\t\t\t(at {x} {round(y + 2.54, 4)} 0)',
        f'\t\t\t(effects (font (size 1.27 1.27)))',
        f'\t\t)',
    ]
    if fp:
        lines += [
            f'\t\t(property "Footprint" "{fp}"',
            f'\t\t\t(at {x} {y} 0)',
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))',
            f'\t\t)',
        ]
    lines += [
        f'\t\t(property "Datasheet" "~"',
        f'\t\t\t(at {x} {y} 0)',
        f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))',
        f'\t\t)',
        f'\t\t(property "Description" ""',
        f'\t\t\t(at {x} {y} 0)',
        f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))',
        f'\t\t)',
    ]
    # Pin stubs
    if "RP2040" in lib_id:
        for p in range(1, 58):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "USB_C" in lib_id:
        for p in ["A1","A4","A5","A6","A7","A8","A9","A12","B1","B4","B5","B6","B7","B8","B9","B12","SHIELD"]:
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "W25Q32" in lib_id:
        for p in range(1, 9):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "AP2204" in lib_id:
        for p in range(1, 6):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "Conn_02x03" in lib_id:
        for p in range(1, 7):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "Conn_01x12" in lib_id:
        for p in range(1, 13):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    elif "Conn_01x06" in lib_id:
        for p in range(1, 7):
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    else:
        for p in ["1", "2"]:
            lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
        if "Crystal" in lib_id:
            for p in ["3", "4"]:
                lines.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
    lines += [
        f'\t\t(instances',
        f'\t\t\t(project "rp2040-devboard"',
        f'\t\t\t\t(path "/{uid()}"',
        f'\t\t\t\t\t(reference "{ref}")',
        f'\t\t\t\t\t(unit 1)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
        f'\t)',
    ]
    return "\n".join(lines)

def make_label(name, x, y, rot=0):
    x = round(x, 4)
    y = round(y, 4)
    return f'''\t(label "{name}"
\t\t(at {x} {y} {rot})
\t\t(effects (font (size 1.27 1.27)) (justify left bottom))
\t\t(uuid "{uid()}")
\t)'''

def make_wire(x1, y1, x2, y2):
    x1, y1, x2, y2 = round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)
    return f'''\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke (width 0) (type default))
\t\t(uuid "{uid()}")
\t)'''

def make_nc(x, y):
    x = round(x, 4)
    y = round(y, 4)
    return f'''\t(no_connect
\t\t(at {x} {y})
\t\t(uuid "{uid()}")
\t)'''

# === Build schematic ===
symbols = []
labels = []
wires = []
ncs = []
pwr_count = 0

def pwr():
    global pwr_count
    pwr_count += 1
    return f"#PWR{pwr_count:02d}"

def P3V3(x, y): symbols.append(make_power_sym(pwr(), "+3V3", x, y))
def PGND(x, y): symbols.append(make_power_sym(pwr(), "GND", x, y))
def PPWR(x, y): symbols.append(make_power_sym(pwr(), "PWR_FLAG", x, y))
def S(lib, ref, val, x, y, rot=0, fp=""): symbols.append(make_sym(lib, ref, val, x, y, rot, fp))
def L(name, x, y, rot=0): labels.append(make_label(name, x, y, rot))
def W(x1, y1, x2, y2): wires.append(make_wire(x1, y1, x2, y2))
def NC(x, y): ncs.append(make_nc(x, y))

# === Placement coordinates (mm, on 2.54mm grid) ===
# All Y-coords in schematic space (positive = down)
RP_X, RP_Y = 152.4, 101.6   # MCU center
USB_X, USB_Y = 38.1, 76.2   # USB-C (moved up)
LDO_X, LDO_Y = 76.2, 38.1  # LDO (moved up)
FLASH_X, FLASH_Y = 254.0, 127  # Flash (moved right)
CRYSTAL_X, CRYSTAL_Y = 101.6, 165.1  # Crystal (moved down)
SWD_X, SWD_Y = 38.1, 165.1  # SWD header (moved down)
BOOT_X, BOOT_Y = 266.7, 156.21  # BOOTSEL (moved right)
RESET_X, RESET_Y = 38.1, 139.7  # Reset (moved down)

# --- U1: RP2040 ---
S("MCU_RaspberryPi:RP2040", "U1", "RP2040", RP_X, RP_Y, fp="Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm")

# RP2040 pin map: pin_num -> (rel_x, rel_y from symbol origin, before y-inversion)
# Right side pins (x=+25.4 in symbol): GPIO0-29
right_pins = [
    (2, "GPIO0"), (3, "GPIO1"), (4, "GPIO2"), (5, "GPIO3"),
    (6, "GPIO4"), (7, "GPIO5"), (8, "GPIO6"), (9, "GPIO7"),
    (11, "GPIO8"), (12, "GPIO9"), (13, "GPIO10"), (14, "GPIO11"),
    (15, "GPIO12"), (16, "GPIO13"), (17, "GPIO14"), (18, "GPIO15"),
    (27, "GPIO16"), (28, "GPIO17"), (29, "GPIO18"), (30, "GPIO19"),
    (31, "GPIO20"), (32, "GPIO21"),
    (34, "GPIO22"), (35, "GPIO23"), (36, "GPIO24"), (37, "GPIO25"),
    (38, "GPIO26"), (39, "GPIO27"), (40, "GPIO28"), (41, "GPIO29"),
]
# Y positions of right-side pins in symbol (from top = pin2 at y=38.1, stepping -2.54)
# Note: hidden IOVDD pin 42 at y=-27.94 creates a 5.08mm gap between GPIO25 and GPIO26
for i, (pnum, gname) in enumerate(right_pins):
    pin_y_sym = 38.1 - i * 2.54
    if i >= 26:
        pin_y_sym -= 2.54
    abs_x = RP_X + 25.4 + 12.7
    abs_y = RP_Y - pin_y_sym
    L(gname, abs_x, abs_y, 0)
    W(RP_X + 25.4, abs_y, abs_x, abs_y)

# Left side pins
left_pins = {
    56: ("QSPI_SS", 5.08), 52: ("QSPI_SCLK", 2.54), 53: ("QSPI_SD0", 0),
    55: ("QSPI_SD1", -2.54), 54: ("QSPI_SD2", -5.08), 51: ("QSPI_SD3", -7.62),
    47: ("USB_DP", 12.7), 46: ("USB_DM", 15.24),
    24: ("SWCLK", -33.02), 25: ("SWDIO", -35.56),
    26: ("RUN", 22.86),
    20: ("XIN", -15.24), 21: ("XOUT", -25.4),
}
for pnum, (net, pin_y_sym) in left_pins.items():
    abs_x = RP_X - 25.4 - 5.08
    abs_y = RP_Y - pin_y_sym
    L(net, abs_x, abs_y, 180)
    W(RP_X - 25.4, abs_y, abs_x, abs_y)

# TESTEN -> GND
abs_y = RP_Y - 30.48
PGND(RP_X - 30.48, abs_y)
W(RP_X - 25.4, abs_y, RP_X - 30.48, abs_y)

# Power pins (top)
for pnum in [1, 10, 22, 33, 42, 49]:  # IOVDD
    P3V3(RP_X - 2.54, RP_Y - 45.72 - 5.08)
    W(RP_X - 2.54, RP_Y - 45.72, RP_X - 2.54, RP_Y - 45.72 - 5.08)
for pnum in [23, 50]:  # DVDD - connect to VREG_VOUT, not +3V3
    L("DVDD", RP_X + 12.7 + 5.08, RP_Y - 45.72, 0)
    W(RP_X + 12.7, RP_Y - 45.72, RP_X + 12.7 + 5.08, RP_Y - 45.72)
# ADC_AVDD, VREG_VIN, USB_VDD
P3V3(RP_X - 10.16, RP_Y - 45.72 - 5.08)
W(RP_X - 10.16, RP_Y - 45.72, RP_X - 10.16, RP_Y - 45.72 - 5.08)
P3V3(RP_X + 2.54, RP_Y - 45.72 - 5.08)
W(RP_X + 2.54, RP_Y - 45.72, RP_X + 2.54, RP_Y - 45.72 - 5.08)
P3V3(RP_X - 12.7, RP_Y - 45.72 - 5.08)
W(RP_X - 12.7, RP_Y - 45.72, RP_X - 12.7, RP_Y - 45.72 - 5.08)
# VREG_VOUT -> DVDD
L("DVDD", RP_X + 7.62 + 5.08, RP_Y - 45.72, 0)
W(RP_X + 7.62, RP_Y - 45.72, RP_X + 7.62 + 5.08, RP_Y - 45.72)
# GND (pin 57, bottom)
PGND(RP_X, RP_Y + 45.72 + 5.08)
W(RP_X, RP_Y + 45.72, RP_X, RP_Y + 45.72 + 5.08)

# --- Decoupling caps C1-C5 (100nF on IOVDD/USB_VDD/ADC_AVDD) ---
cap_locs = [("C1", 127.0), ("C2", 134.62), ("C3", 152.4), ("C4", 170.18), ("C5", 177.8), ("C6", 185.42)]
for cref, cx in cap_locs:
    cy = 55.88
    S("Device:C", cref, "100nF", cx, cy, fp="Capacitor_SMD:C_0402_1005Metric")
    P3V3(cx, cy - 5.08)
    PGND(cx, cy + 5.08)
    W(cx, cy - 3.81, cx, cy - 5.08)
    W(cx, cy + 3.81, cx, cy + 5.08)

# C7 (1µF on VREG_VIN)
S("Device:C", "C7", "1µF", 193.04, 55.88, fp="Capacitor_SMD:C_0402_1005Metric")
P3V3(193.04, 50.8)
PGND(193.04, 60.96)
W(193.04, 52.07, 193.04, 50.8)
W(193.04, 59.69, 193.04, 60.96)

# --- Crystal Y1 ---
S("Device:Crystal_GND24", "Y1", "12MHz", CRYSTAL_X, CRYSTAL_Y, fp="Crystal:Crystal_SMD_HC49-SD")
L("XIN", CRYSTAL_X - 11.43, CRYSTAL_Y, 180)
W(CRYSTAL_X - 6.35, CRYSTAL_Y, CRYSTAL_X - 11.43, CRYSTAL_Y)
L("XOUT", CRYSTAL_X + 11.43, CRYSTAL_Y, 0)
W(CRYSTAL_X + 6.35, CRYSTAL_Y, CRYSTAL_X + 11.43, CRYSTAL_Y)
PGND(CRYSTAL_X, CRYSTAL_Y + 7.62)
W(CRYSTAL_X, CRYSTAL_Y + 5.08, CRYSTAL_X, CRYSTAL_Y + 7.62)

# C8, C9 load caps
S("Device:C", "C8", "12pF", CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62, fp="Capacitor_SMD:C_0402_1005Metric")
L("XIN", CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 - 5.08, 180)
W(CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 - 3.81, CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 - 5.08)
PGND(CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 + 5.08)
W(CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 + 3.81, CRYSTAL_X - 17.78, CRYSTAL_Y + 7.62 + 5.08)

S("Device:C", "C9", "12pF", CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62, fp="Capacitor_SMD:C_0402_1005Metric")
L("XOUT", CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 - 5.08, 0)
W(CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 - 3.81, CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 - 5.08)
PGND(CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 + 5.08)
W(CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 + 3.81, CRYSTAL_X + 17.78, CRYSTAL_Y + 7.62 + 5.08)

# --- USB-C J1 ---
S("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "USB_C", USB_X, USB_Y, fp="Connector_USB:USB_C_Receptacle_GCT_USB4105-xx")

# VBUS
L("VBUS_RAW", USB_X + 25.4, USB_Y - 15.24, 0)
W(USB_X + 15.24, USB_Y - 15.24, USB_X + 25.4, USB_Y - 15.24)
# CC1, CC2
L("CC1", USB_X + 25.4, USB_Y - 10.16, 0)
W(USB_X + 15.24, USB_Y - 10.16, USB_X + 25.4, USB_Y - 10.16)
L("CC2", USB_X + 25.4, USB_Y - 7.62, 0)
W(USB_X + 15.24, USB_Y - 7.62, USB_X + 25.4, USB_Y - 7.62)
# D+/D-
L("USB_DP_RAW", USB_X + 25.4, USB_Y + 2.54, 0)
W(USB_X + 15.24, USB_Y + 2.54, USB_X + 25.4, USB_Y + 2.54)
L("USB_DM_RAW", USB_X + 25.4, USB_Y - 2.54, 0)
W(USB_X + 15.24, USB_Y - 2.54, USB_X + 25.4, USB_Y - 2.54)
# B-side D+/D- (mirror side, same nets) - route to avoid F1 wire overlap
L("USB_DP_RAW", USB_X + 25.4, USB_Y + 5.08, 0)
W(USB_X + 15.24, USB_Y + 5.08, USB_X + 25.4, USB_Y + 5.08)
L("USB_DM_RAW", USB_X + 25.4, USB_Y - 5.08, 0)
W(USB_X + 15.24, USB_Y, USB_X + 15.24, USB_Y - 5.08)
W(USB_X + 15.24, USB_Y - 5.08, USB_X + 25.4, USB_Y - 5.08)
# GND
PGND(USB_X, USB_Y + 27.94)
W(USB_X, USB_Y + 22.86, USB_X, USB_Y + 27.94)
# SHIELD -> GND
PGND(USB_X - 7.62, USB_Y + 27.94)
W(USB_X - 7.62, USB_Y + 22.86, USB_X - 7.62, USB_Y + 27.94)
# NC on SBU1, SBU2
NC(USB_X + 15.24, USB_Y + 12.7)
NC(USB_X + 15.24, USB_Y + 15.24)

# --- Polyfuse F1 ---
S("Device:Polyfuse", "F1", "500mA", 63.5, USB_Y, fp="Fuse:Fuse_1206_3216Metric")
L("VBUS_RAW", 63.5 - 5.08, USB_Y, 180)
L("VBUS", 63.5 + 10.16, USB_Y, 0)
W(63.5 + 5.08, USB_Y, 63.5 + 10.16, USB_Y)

# --- CC pulldown R3, R4 ---
S("Device:R", "R3", "5.1k", 88.9, 76.2, fp="Resistor_SMD:R_0402_1005Metric")
L("CC1", 88.9, 76.2 - 5.08, 180)
W(88.9, 76.2 - 3.81, 88.9, 76.2 - 5.08)
PGND(88.9, 76.2 + 5.08)
W(88.9, 76.2 + 3.81, 88.9, 76.2 + 5.08)

S("Device:R", "R4", "5.1k", 101.6, 76.2, fp="Resistor_SMD:R_0402_1005Metric")
L("CC2", 101.6, 76.2 - 5.08, 180)
W(101.6, 76.2 - 3.81, 101.6, 76.2 - 5.08)
PGND(101.6, 76.2 + 5.08)
W(101.6, 76.2 + 3.81, 101.6, 76.2 + 5.08)

# --- USB series R5, R6 ---
S("Device:R", "R5", "27R", 114.3, 93.98, fp="Resistor_SMD:R_0402_1005Metric")
L("USB_DP_RAW", 114.3, 93.98 - 5.08, 180)
W(114.3, 93.98 - 3.81, 114.3, 93.98 - 5.08)
L("USB_DP", 114.3, 93.98 + 5.08, 0)
W(114.3, 93.98 + 3.81, 114.3, 93.98 + 5.08)

S("Device:R", "R6", "27R", 114.3, 99.06, fp="Resistor_SMD:R_0402_1005Metric")
L("USB_DM_RAW", 114.3, 99.06 - 5.08, 180)
W(114.3, 99.06 - 3.81, 114.3, 99.06 - 5.08)
L("USB_DM", 114.3, 99.06 + 5.08, 0)
W(114.3, 99.06 + 3.81, 114.3, 99.06 + 5.08)

# --- VBUS bulk cap C11 ---
S("Device:C", "C11", "10uF", 76.2, 101.6, fp="Capacitor_SMD:C_0805_2012Metric")
L("VBUS", 76.2, 96.52, 180)
W(76.2, 97.79, 76.2, 96.52)
PGND(76.2, 106.68)
W(76.2, 105.41, 76.2, 106.68)

# --- LDO U2 (AP2204K-3.3) ---
S("Regulator_Linear:AP2204K-3.3", "U2", "AP2204K-3.3", LDO_X, LDO_Y, fp="Package_TO_SOT_SMD:SOT-23-5")
L("VBUS", LDO_X - 12.7, LDO_Y - 2.54, 180)
W(LDO_X - 7.62, LDO_Y - 2.54, LDO_X - 12.7, LDO_Y - 2.54)
L("VBUS", LDO_X - 12.7, LDO_Y, 180)
W(LDO_X - 7.62, LDO_Y, LDO_X - 12.7, LDO_Y)
PGND(LDO_X, LDO_Y + 10.16)
W(LDO_X, LDO_Y + 7.62, LDO_X, LDO_Y + 10.16)
NC(LDO_X + 5.08, LDO_Y)
L("+3V3", LDO_X + 12.7, LDO_Y - 2.54, 0)
W(LDO_X + 7.62, LDO_Y - 2.54, LDO_X + 12.7, LDO_Y - 2.54)

# C10 (output cap)
S("Device:C", "C10", "4.7uF", LDO_X + 17.78, LDO_Y - 2.54, fp="Capacitor_SMD:C_0402_1005Metric")
P3V3(LDO_X + 17.78, LDO_Y - 7.62)
PGND(LDO_X + 17.78, LDO_Y + 2.54)
W(LDO_X + 17.78, LDO_Y - 6.35, LDO_X + 17.78, LDO_Y - 7.62)
W(LDO_X + 17.78, LDO_Y + 1.27, LDO_X + 17.78, LDO_Y + 2.54)

# --- Flash U3 (W25Q32JVSS) ---
S("Memory_Flash:W25Q32JVSS", "U3", "W25Q32JVSS", FLASH_X, FLASH_Y, fp="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm")
# CS -> QSPI_SS
L("QSPI_SS", FLASH_X - 15.24, FLASH_Y - 7.62, 180)
W(FLASH_X - 10.16, FLASH_Y - 7.62, FLASH_X - 15.24, FLASH_Y - 7.62)
# DO -> QSPI_SD1
L("QSPI_SD1", FLASH_X - 15.24, FLASH_Y, 180)
W(FLASH_X - 10.16, FLASH_Y, FLASH_X - 15.24, FLASH_Y)
# WP# -> +3V3
P3V3(FLASH_X - 15.24, FLASH_Y + 2.54)
W(FLASH_X - 10.16, FLASH_Y + 2.54, FLASH_X - 15.24, FLASH_Y + 2.54)
# GND
PGND(FLASH_X, FLASH_Y + 15.24)
W(FLASH_X, FLASH_Y + 12.7, FLASH_X, FLASH_Y + 15.24)
# DI -> QSPI_SD0
L("QSPI_SD0", FLASH_X - 15.24, FLASH_Y - 2.54, 180)
W(FLASH_X - 10.16, FLASH_Y - 2.54, FLASH_X - 15.24, FLASH_Y - 2.54)
# CLK -> QSPI_SCLK
L("QSPI_SCLK", FLASH_X - 15.24, FLASH_Y - 5.08, 180)
W(FLASH_X - 10.16, FLASH_Y - 5.08, FLASH_X - 15.24, FLASH_Y - 5.08)
# HOLD# -> +3V3
P3V3(FLASH_X - 15.24, FLASH_Y + 5.08)
W(FLASH_X - 10.16, FLASH_Y + 5.08, FLASH_X - 15.24, FLASH_Y + 5.08)
# VCC -> +3V3
P3V3(FLASH_X, FLASH_Y - 15.24)
W(FLASH_X, FLASH_Y - 12.7, FLASH_X, FLASH_Y - 15.24)

# --- BOOTSEL SW1 ---
S("Switch:SW_Push", "SW1", "BOOTSEL", BOOT_X, BOOT_Y)
L("QSPI_SS", BOOT_X, BOOT_Y - 7.62, 180)
W(BOOT_X, BOOT_Y - 5.08, BOOT_X, BOOT_Y - 7.62)
PGND(BOOT_X, BOOT_Y + 7.62)
W(BOOT_X, BOOT_Y + 5.08, BOOT_X, BOOT_Y + 7.62)

# R2 (10k pull-up: pin 1=top=+3V3, pin 2=bottom=QSPI_SS)
S("Device:R", "R2", "10k", BOOT_X + 12.7, BOOT_Y, fp="Resistor_SMD:R_0402_1005Metric")
P3V3(BOOT_X + 12.7, BOOT_Y - 5.08)
W(BOOT_X + 12.7, BOOT_Y - 3.81, BOOT_X + 12.7, BOOT_Y - 5.08)
L("QSPI_SS", BOOT_X + 12.7, BOOT_Y + 5.08, 180)
W(BOOT_X + 12.7, BOOT_Y + 3.81, BOOT_X + 12.7, BOOT_Y + 5.08)

# --- Reset SW2 ---
S("Switch:SW_Push", "SW2", "RESET", RESET_X, RESET_Y)
L("RUN", RESET_X, RESET_Y - 7.62, 180)
W(RESET_X, RESET_Y - 5.08, RESET_X, RESET_Y - 7.62)
PGND(RESET_X, RESET_Y + 7.62)
W(RESET_X, RESET_Y + 5.08, RESET_X, RESET_Y + 7.62)

# R1 (10k pull-up: pin 1=top=+3V3, pin 2=bottom=RUN)
S("Device:R", "R1", "10k", RESET_X + 12.7, RESET_Y, fp="Resistor_SMD:R_0402_1005Metric")
P3V3(RESET_X + 12.7, RESET_Y - 5.08)
W(RESET_X + 12.7, RESET_Y - 3.81, RESET_X + 12.7, RESET_Y - 5.08)
L("RUN", RESET_X + 12.7, RESET_Y + 5.08, 180)
W(RESET_X + 12.7, RESET_Y + 3.81, RESET_X + 12.7, RESET_Y + 5.08)

# --- SWD Header J2 ---
S("Connector:Conn_02x03_Odd_Even", "J2", "SWD", SWD_X, SWD_Y, fp="Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical")
# Pin 1 (odd, lib_x=0) = SWCLK, Pin 2 (even, lib_x=5.08) = GND
# Pin 3 (odd, lib_x=0) = SWDIO, Pin 4 (even, lib_x=5.08) = VO(+3V3)
# Pin 5 (odd, lib_x=0) = nRST, Pin 6 (even, lib_x=5.08) = GND
# Y-inversion: schematic_y = symbol_y - lib_y
L("SWCLK", SWD_X - 5.08, SWD_Y - 7.62, 180)
W(SWD_X, SWD_Y - 7.62, SWD_X - 5.08, SWD_Y - 7.62)
PGND(SWD_X + 10.16, SWD_Y - 7.62)
W(SWD_X + 5.08, SWD_Y - 7.62, SWD_X + 10.16, SWD_Y - 7.62)
L("SWDIO", SWD_X - 5.08, SWD_Y - 2.54, 180)
W(SWD_X, SWD_Y - 2.54, SWD_X - 5.08, SWD_Y - 2.54)
P3V3(SWD_X + 10.16, SWD_Y - 2.54)
W(SWD_X + 5.08, SWD_Y - 2.54, SWD_X + 10.16, SWD_Y - 2.54)
L("RUN", SWD_X - 5.08, SWD_Y + 2.54, 180)
W(SWD_X, SWD_Y + 2.54, SWD_X - 5.08, SWD_Y + 2.54)
PGND(SWD_X + 10.16, SWD_Y + 2.54)
W(SWD_X + 5.08, SWD_Y + 2.54, SWD_X + 10.16, SWD_Y + 2.54)

# --- GPIO Breakout Headers ---
# J3: Left header (GPIO0-GPIO11)
J3_X, J3_Y = 12.7, 101.6
S("Connector:Conn_01x12", "J3", "GPIO Left", J3_X, J3_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical")
gpio_left = ["GPIO0", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "GPIO5", "GPIO6", "GPIO7", "GPIO8", "GPIO9", "GPIO10", "GPIO11"]
for j, gname in enumerate(gpio_left):
    pin_y = J3_Y + 13.97 - j * 2.54
    L(gname, J3_X - 7.62, pin_y, 180)
    W(J3_X - 5.08, pin_y, J3_X - 7.62, pin_y)

# J4: Right header (GPIO12-GPIO23)
J4_X, J4_Y = 304.8, 101.6
S("Connector:Conn_01x12", "J4", "GPIO Right", J4_X, J4_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical")
gpio_right = ["GPIO12", "GPIO13", "GPIO14", "GPIO15", "GPIO16", "GPIO17", "GPIO18", "GPIO19", "GPIO20", "GPIO21", "GPIO22", "GPIO23"]
for j, gname in enumerate(gpio_right):
    pin_y = J4_Y + 13.97 - j * 2.54
    L(gname, J4_X - 7.62, pin_y, 180)
    W(J4_X - 5.08, pin_y, J4_X - 7.62, pin_y)

# J5: Bottom header (GPIO24-GPIO29)
J5_X, J5_Y = 152.4, 215.9
S("Connector:Conn_01x06", "J5", "GPIO Bottom", J5_X, J5_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical")
gpio_bottom = ["GPIO24", "GPIO25", "GPIO26", "GPIO27", "GPIO28", "GPIO29"]
for j, gname in enumerate(gpio_bottom):
    pin_y = J5_Y + 6.35 - j * 2.54
    L(gname, J5_X - 7.62, pin_y, 180)
    W(J5_X - 5.08, pin_y, J5_X - 7.62, pin_y)

# --- PWR_FLAG for ERC ---
PPWR(LDO_X - 17.78, LDO_Y - 2.54)
PPWR(LDO_X, LDO_Y + 12.7)

# === Assemble ===
all_sym = "\n".join(symbols)
all_lbl = "\n".join(labels)
all_wire = "\n".join(wires)
all_nc = "\n".join(ncs)

schematic = f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "a0b1c2d3-e4f5-6789-abcd-ef0123456789")
\t(paper "A3")
\t(title_block
\t\t(title "RP2040 Breadboard Devboard")
\t\t(date "2026-08-25")
\t\t(rev "A")
\t\t(comment 1 "USB-C + 3.3V LDO + 4MB QSPI flash")
\t\t(comment 2 "All 30 GPIOs exposed on headers")
\t)
\t(lib_symbols
{ALL_LIB}
\t)
{all_sym}
{all_lbl}
{all_wire}
{all_nc}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rp2040-devboard.kicad_sch")
with open(out, "w", encoding="utf-8") as f:
    f.write(schematic)

print(f"Written {len(schematic):,} bytes to {out}")
print(f"Symbols: {len(symbols)}, Labels: {len(labels)}, Wires: {len(wires)}, NCs: {len(ncs)}")
