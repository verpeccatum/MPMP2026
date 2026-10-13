from pathlib import Path
import re

ROOT = path //define path
TARGET = ROOT / 'AktuellerStand.circ'


def main_body(lines):
    start = next(i for i, line in enumerate(lines) if '<circuit name="main">' in line)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == '</circuit>')
    return start, end, lines[start + 1:end]


def point_in_rect(point, rect):
    x, y = point
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def loc_of(line):
    m = re.search(r'loc="\((-?\d+),(-?\d+)\)"', line)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def wire_points(line):
    pts = re.findall(r'\((-?\d+),(-?\d+)\)', line)
    if len(pts) != 2:
        return None
    return [(int(x), int(y)) for x, y in pts]


def shift_coords(text, dx, dy):
    def repl(match):
        return f'({int(match.group(1)) + dx},{int(match.group(2)) + dy})'
    return re.sub(r'\((-?\d+),(-?\d+)\)', repl, text)


TRANSLATIONS = {
    'CLK': 'clk',
    'instruction_bus': 'Instruction_bus',
    'CU_op_code': 'CU_Opcode',
    'CMD_CONST_8': 'CMDConst8',
    'CU_const_8_EN': 'CU_const8_en',
    'CU_const_H_8_SET': 'CU_const8_H_set',
    'CU_ALU_RESULT_EN': 'CU_ALU_RESULT_en',
    'CU_ALU_SOURCE_ACC_CONST8': 'CU_Select_ALU_Source_ACC_Const8',
    'CU_Register_write_enable': 'RF_RegW_en',
    'CU_Register_read_enable': 'RF_RegR_en',
    'CU_register_RW': 'CU_Reg_rw',
    'CU_Register_read_select': 'CU_Reg_Read_Select',
    'CU_Register_write_select': 'CU_Reg_Write_Select',
    'Programm_Counter': 'PC_program_counter',
    'PC': 'PC_program_counter',
    'Intruction_Register': 'IW_Instruction_word',
    'cycle_counter': 'CC_cycle_counter',
    'micro_state': 'uP_memory',
}


def translate_labels(text, splash=False):
    for old, new in TRANSLATIONS.items():
        text = text.replace(f'val="{old}"', f'val="{new}"')
    if splash:
        text = text.replace('BLITTER', 'SPLASH')
        text = text.replace('Blitter', 'Splash')
        text = text.replace('blitter', 'splash')
        text = re.sub(r'BLIT_', 'SPLASH_', text)
    return text


def extract_blocks(source, rect, dx, dy, marker, splash=False):
    lines = source.read_text(encoding='utf-8').splitlines(keepends=True)
    _, _, body = main_body(lines)
    out = []
    out.append(f'    <comp lib="9" loc="({rect[0] + dx},{rect[1] + dy - 60})" name="Text">\n')
    out.append('      <a name="font" val="SansSerif bold 18"/>\n')
    out.append(f'      <a name="text" val="{marker}"/>\n')
    out.append('    </comp>\n')

    i = 0
    while i < len(body):
        line = body[i]
        stripped = line.lstrip()
        if stripped.startswith('<comp '):
            block = [line]
            i += 1
            if not stripped.rstrip().endswith('/>'):
                while i < len(body) and '</comp>' not in body[i - 1]:
                    block.append(body[i])
                    i += 1
            loc = loc_of(block[0])
            if loc and point_in_rect(loc, rect):
                text = ''.join(block)
                text = shift_coords(text, dx, dy)
                text = translate_labels(text, splash=splash)
                out.append(text)
            continue
        if stripped.startswith('<wire '):
            pts = wire_points(line)
            if pts and all(point_in_rect(pt, rect) for pt in pts):
                text = shift_coords(line, dx, dy)
                out.append(text)
        i += 1
    return out


def run():
    target = TARGET.read_text(encoding='utf-8').splitlines(keepends=True)
    full = ''.join(target)
    if 'IMPORTED_FROM_B1_PPU_SPRITES' in full or 'SPLASH_IMPORTED_FROM_B2' in full:
        start = next(i for i, line in enumerate(target) if '<!-- Imported game rendering blocks -->' in line)
        _, end, _ = main_body(target)
        del target[start:end]

    # Beispiel1: sprite/PPU/rendering area including sprite memory, color table,
    # player position registers and RGB output. Shifted right of the existing CPU.
    b1_blocks = extract_blocks(
        B1,
        rect=(620, 2150, 2820, 3860),
        dx=3600,
        dy=0,
        marker='IMPORTED_FROM_B1_PPU_SPRITES',
        splash=False,
    )

    # Beispiel2: BLITTER rectangle/move/draw block. Imported as SPLASH.
    b2_blocks = extract_blocks(
        B2,
        rect=(50, 2210, 1800, 3450),
        dx=6600,
        dy=0,
        marker='SPLASH_IMPORTED_FROM_B2',
        splash=True,
    )

    _, end, _ = main_body(target)
    insert = ['\n    <!-- Imported game rendering blocks -->\n'] + b1_blocks + ['\n    <!-- Imported splash logic from Beispiel2 -->\n'] + b2_blocks
    _, end, _ = main_body(target)
    target[end:end] = insert
    TARGET.write_text(''.join(target), encoding='utf-8')


if __name__ == '__main__':
    run()
