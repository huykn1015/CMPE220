from enum import Enum
from cpu import  Bus, RAM, CPU, STDOut
from instructions import Flags


class InstructionsStrings(Enum):
    NO_OP = "00000_00"
    # arithmetic first bit is 0, second bit is 1 if use imm
    ADD = "00010_00"
    SUB = "00010_01"
    MUL = "00010_10"
    SHL = "00010_11"
    SHR = "00011_00"
    SLT = "00011_01"
    

    ADDI = "00110_00"
    SUBI = "00110_01"
    MULI = "00110_10"
    SHLI = "00110_11"
    SHRI = "00111_00"
    SLTI = "00111_01"

    # other if first bit is 1, second bit is 1 if jump
    BEQ = "01100_00"
    BNE = "01100_01"
    BGE = "01100_10"
    BLT = "01100_11"

    LW = "01000_00"
    SW = "01000_10"

    JAL = "00000_01"




def r_type(instr_: InstructionsStrings, rd:int, rs1: int, rs2: int) -> int:
    opcode: str = instr_.value
    instr = int(f"{rs2:06b}{rs1:06b}{rd:06b}{opcode}".replace('_', ''), 2)
    return instr


def i_type(instr_: InstructionsStrings, rd:int, rs1: int, imm:int) -> int: # increment r1
    opcode = instr_.value
    instr = int(f"{imm & 0x7FF:11b}{rs1:06b}{rd:06b}{opcode}".replace('_', ''), 2)
    return instr

def b_type(instr_: InstructionsStrings, rs1: int, rs2: int, imm: int) -> int:
    opcode = instr_.value
    instr = int(f"{imm & 0x7FF:11b}{rs2:06b}{rs1:06b}{opcode}".replace('_', ''), 2)
    return instr

def sw(rs1: int, rs2: int, imm: int) -> int:
    opcode = InstructionsStrings.SW.value
    instr = int(f"{imm & 0x7FF:11b}{rs2:06b}{rs1:06b}{opcode}".replace('_', ''), 2)
    return instr

def lw(rd: int, rs1: int, imm: int) -> int:
    opcode = InstructionsStrings.LW.value
    instr = int(f"{imm & 0x7FF:11b}{rs1:06b}{rd:06b}{opcode}".replace('_', ''), 2)
    return instr



DATA_ADDR = 80

MAX_RAM_ADDR = 99


if __name__ == '__main__':
    ram = RAM(MAX_RAM_ADDR + 1)
    string = "Hello World\n"
    for i, c in enumerate(string):
        ram.write_addr(DATA_ADDR + i, ord(c))

    instr_0 = r_type(InstructionsStrings.ADDI, 1, 0, 10) # r1 = r0 + 10
    instr_1 = r_type(InstructionsStrings.ADDI, 2, 0, DATA_ADDR) # r2 = r0 + DATA_ADDR
    instr_2 = r_type(InstructionsStrings.ADDI, 4, 0, MAX_RAM_ADDR) # r2 = r0 + 100 # addr of mmio
    instr_3 = lw(3, 2, 0)# read value at addr into r3
    instr_4 = b_type(InstructionsStrings.BEQ, 1, 3, 4)# branch to END if r3 == r1
    instr_5 = sw(4, 3, 0)# write r3 to stdout
    instr_6 = r_type(InstructionsStrings.ADDI, 2, 2, 1) # inc r2
    instr_7 = b_type(InstructionsStrings.BEQ, 0, 0, -4) # jump back to start of loop
    instr_8 = sw(4, 3, 1)# write 1 to flush 
    # flush stdout

    instructions = [instr_0, instr_1, instr_2, instr_3, instr_4, instr_5, instr_6, instr_7, instr_8]
    for i, instr in enumerate(instructions):
        ram.write_addr(i, instr)

    std_out = STDOut()
    bus = Bus(ram, MAX_RAM_ADDR, std_out)

    expected_mem_value = 2
    cpu = CPU(num_registers=32, bus=bus)
    while True:
        cpu.cycle()

