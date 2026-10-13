from dataclasses import dataclass
from typing import Union
import re

LABEL_REGEX = r"^[A-Za-z_][A-Za-z0-9_]*$"

# Constants for the 2+5+3+3+3 Group
LOAD_OP =   0b0100_000
STORE_OP =  0b0100_001
MOV_OP =    0b0100_010
ADDREG_OP = 0b0100_011
SUBREG_OP = 0b0100_100
MULREG_OP = 0b0100_101
DIVREG_OP = 0b0100_110
JZ_OP =     0b100
JNZ_OP =    0b101

OPCODES = {
    # 0000_0000_0000_0000 NOP
    "NOP":  0b0000_0000,
    # 11xx_xxx_xxxx_xxxx 5+3+8 Group 
    "MOV0L":0b1110_0000,
    "MOVH": 0b1110_1000,
    "ADD":  0b1100_0000,
    "SUB":  0b1100_1000,
    "OUT":  0b1101_1000,
    "JUMPS":0b1111_0000,
    "IN":   0b1101_0000,
    # 01xx_xxxx_xxxx_xxxx 7+3+3+3 Group 
    "LOAD": 0b0100_000, 
    "STORE": 0b0100_001,
    "MOV": 0b0100_010,
    "ADDREG": 0b0100_011, # Add 2 Registers // Destination, Source1, Source2
    "SUBREG": 0b0100_100, # Subtract 2 Registers // Destination, Source1, Source2
    "MULREG": 0b0100_101, # Multiply 2 Registers // Destination, Source1, Source2
    "DIVREG": 0b0100_110, # Divide 2 Registers // Destination, Source1, Source2
    # 10xx_xxxx_xxxx_xxxx 3+3+10 Group
    "JZ": 0b100,
    "JNZ": 0b101
}

def format_binary(value: int, bits: int | None = 1, group_size: int = 4) -> str:
    if bits is None:
        binary = bin(value)[2:]
    else:
        binary = f"{value:0{bits}b}"

    reversed_binary = binary[::-1]

    grouped_reversed = "_".join(
        reversed_binary[i:i + group_size]
        for i in range(0, len(reversed_binary), group_size)
    )

    return grouped_reversed[::-1]

def read_source_code() -> str:
    with open("programs/first Programm.asm", "r", encoding="utf-8") as f:
        return f.read()

@dataclass
class Register:
    value: int

@dataclass
class Immediate:
    value: int

@dataclass
class CharLiteral:
    value: int

@dataclass
class LabelRef:
    name: str
    value: int = 0

@dataclass
class Label:
    name: str
    address: int

@dataclass
class Instruction:
    name: str
    opcode: int
    args: list[Union[Register, Immediate, CharLiteral, LabelRef]]
    address: int
    line_number: int


def parse_argument(arg: str) -> Union[Register, Immediate, CharLiteral, LabelRef]:
    arg = arg.strip()
    if arg.startswith("'") and arg.endswith("'") and len(arg) == 3:
        if arg[1].isascii():
            return CharLiteral(ord(arg[1]))

    if arg.lower().startswith("r") and len(arg) == 2:
        register = int(arg[1], 10)
        if 0 <= register <= 7:
            return Register(register)

    if arg.startswith('#'):
        const = int(arg[1:], 0)
        if 0 <= const <= 255:
            return Immediate(const)

    if re.fullmatch(LABEL_REGEX, arg):
        return LabelRef(arg)

    raise Exception(f"Invalid argument: {arg}")


def to_maschine_code(instruction: Instruction, labels: dict[str, int]) -> int:
    for arg in instruction.args:
        if isinstance(arg, LabelRef):
            if arg.name not in labels:
                raise Exception(f"Invalid label reference on line {instruction.line_number}:\n {instruction} \n Label '{arg.name}' does not exist")
            arg.value = labels[arg.name]
    #3Regop

    print("\nCurrent Instruction: ", instruction, instruction.args)
    args: list[Union[Register, Immediate, CharLiteral, LabelRef]] = instruction.args
    op = instruction.opcode
    if op == JZ_OP or op == JNZ_OP: 
        if not (len(args) == 1 and isinstance(args[0], (LabelRef)) and args[0].value <= 1023):
            raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid argument")
        maschine_instruction: int = instruction.opcode << 13 # get 3 bits to front 15,14,13
        maschine_instruction = maschine_instruction | args[0].value
        return maschine_instruction 
    # startet mit 1
    if instruction.opcode & 0b1000_0000: #prüft ob höchstes bit 1 ist
        if instruction.opcode & 0b0100_0000: # prüfe ob zweithöchstes bit 1 ist
            
            if not (len(args) == 2 and isinstance(args[0], Register) and isinstance(args[1], (LabelRef, Immediate,CharLiteral))):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid argument")
            maschine_instruction: int = instruction.opcode << 8
            maschine_instruction = maschine_instruction | args[0].value << 8
            maschine_instruction = maschine_instruction | args[1].value
            return maschine_instruction
        else:
            raise Exception(f"Unsupported opcode on line {instruction.line_number}: 0b{instruction.opcode:08b} - highest bit set but second highest not set")
    # 3*REG Gruppe: 2+5+3+3+3  
    elif instruction.opcode & 0b0100_000: # prüfe ob zweithöchstes bit 1 ist
        DEST = 6
        SRC1_DATA = 3
        SRC2_RAM_ADDR = 0
        SRC2_DATA = 0
        
        op = instruction.opcode
        
        # op-code
        maschine_instruction: int = instruction.opcode << 9 # 9er bit shift weil int=****_****_*01x_xxxx <-9- 01xx_xxxR_egRe_gReg
        # args
        if op == LOAD_OP:
            if not (len(args) == 2 and isinstance(args[0], Register) and isinstance(args[1], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid LOAD Instruction")
            # ARG[0] DEST ARG[1] SRC2
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC2_RAM_ADDR
        elif op == STORE_OP:
            if not (len(args) == 2 and isinstance(args[0], Register) and isinstance(args[1], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid STORE Instruction")
            # ARG[0] SRC2 ARG[1] SRC1
            maschine_instruction = maschine_instruction | args[0].value << SRC2_RAM_ADDR
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
        elif op == MOV_OP:
            if not (len(args) == 2 and isinstance(args[0], Register) and isinstance(args[1], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid MOV Instruction")
            # ARG[0] DEST ARG[1] SRC1
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
        elif op == ADDREG_OP:
            if not (len(args) == 3 and isinstance(args[0], Register) and isinstance(args[1], Register) and isinstance(args[2], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid ADDACC Instruction")
            # ARG[0] DEST ARG[1] SRC1
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
            maschine_instruction = maschine_instruction | args[2].value << SRC2_DATA
        elif op == SUBREG_OP:
            if not (len(args) == 3 and isinstance(args[0], Register) and isinstance(args[1], Register) and isinstance(args[2], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid SUBREG Instruction")
            # ARG[0] DEST ARG[1] SRC1 ARG[2] SRC2
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
            maschine_instruction = maschine_instruction | args[2].value << SRC2_DATA
        elif op == MULREG_OP:
            if not (len(args) == 3 and isinstance(args[0], Register) and isinstance(args[1], Register) and isinstance(args[2], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid MULREG Instruction")
            # ARG[0] DEST ARG[1] SRC1 ARG[2] SRC2
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
            maschine_instruction = maschine_instruction | args[2].value << SRC2_DATA
        elif op == DIVREG_OP:
            if not (len(args) == 3 and isinstance(args[0], Register) and isinstance(args[1], Register) and isinstance(args[2], Register)):
                raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid DIVREG Instruction")
            # ARG[0] DEST ARG[1] SRC1 ARG[2] SRC2
            maschine_instruction = maschine_instruction | args[0].value << DEST
            maschine_instruction = maschine_instruction | args[1].value << SRC1_DATA
            maschine_instruction = maschine_instruction | args[2].value << SRC2_DATA
        
        return maschine_instruction
            
        '''
        # LÄNGE NICHT IMMER 3!!! UNTERSCHIEDLICH JE NACH OP
        if not (len(args) == 3 and isinstance(args[0], Register) and isinstance(args[1], Register) and isinstance(args[2], Register)):
            raise Exception(f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid 3Regop Instruction")
        # MUSS PRÜFEN WELCHE ARGUMENTE WICHTIG SIND, GESETZT WERDEN MÜSSEN
        # load, store, move, addacc
        maschine_instruction = maschine_instruction | args[0].value << 6
        maschine_instruction = maschine_instruction | args[1].value << 3
        maschine_instruction = maschine_instruction | args[2].value
        '''   
        
        

# 0b0000_0000_0000_0000
    # 16 bit zahl
    else:
        args: list[Union[Register, Immediate, CharLiteral, LabelRef]] = instruction.args
        if not (len(args) == 0):
            raise Exception(
                f"Invalid argument on line {instruction.line_number}:\n {instruction} \n {args} is not a valid argument")
        maschine_instruction: int = instruction.opcode << (8)
        return maschine_instruction


def main() -> None:
    source_code: str = read_source_code()
    maschine_code: list[int] = []
    instructions: list[Instruction] = [Instruction("NOP", OPCODES["NOP"], [], 0, 0)]
    labels: dict[str, int] = {}
    for line_number, line in enumerate(source_code.split('\n')):
        line = line.split(';', 1)[0] # Remove comments
        line = line.strip() # Remove leading and trailing whitespace
        if len(line) == 0: # Skip empty instructions
            continue

        if line.endswith(':'):
            lable = line[:-1]
            if not re.fullmatch(LABEL_REGEX, lable):
                raise Exception(f"Invalid label on line {line_number}:\n {line} \n {lable} does not match regex {LABEL_REGEX}")
            labels[lable] = len(instructions)
            continue

        name = line.split(' ', 1)[0].upper()
        args_str = line.split(' ', 1)[1] if len(line.split(' ')) > 1 else ''

        if name not in OPCODES.keys():
            raise Exception(f"Invalid command on line {line_number}:\n {line} \n {name} does not exit")

        if args_str:
            args: list[Union[Register, Immediate, CharLiteral, LabelRef]] = [parse_argument(arg) for arg in args_str.split(',')]
            instructions.append(Instruction(name, OPCODES[name], args, len(instructions), line_number))
        else:
            instructions.append(Instruction(name, OPCODES[name], [], len(instructions), line_number))


    for label in labels:
        print(label)
    for line in instructions:
        print(line)


    for instruction in instructions:
        maschine_code.append(to_maschine_code(instruction, labels))
        print(format_binary(maschine_code[-1], 16), f'{maschine_code[-1]:04X}', instruction)

    with open('programm.hex', 'w', encoding='UTF-8') as hex_file:
        hex_file.write('v2.0 raw\n')
        for code in maschine_code:
            hex_file.write(f'{code:04X}\n')
            print(f'{code:04X}\n')
    print("done")
main()
