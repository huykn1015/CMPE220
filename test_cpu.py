from enum import Enum
from cpu import RegisterFile, Bus, RAM, alu, ProgramCounter, CPU
from instructions import decode_instruction, Flags

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


def beq_r0_r0_2():
    # skip next instruction
    opcode = InstructionsStrings.BEQ.value
    rs1 = "000000"
    rs2 = "000000"
    imm_src = "0010"

    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)
    return instr

def beq_r0_r0_p1():
    # skip next instruction
    opcode = InstructionsStrings.BEQ.value
    rs1 = "000000"
    rs2 = "000000"
    imm_src = "1111_1111_111" # -2

    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)
    return instr

def add_r1_r2_r3():
    opcode = InstructionsStrings.ADD.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)
    return instr

def add_r1_r3_r3():
    opcode = InstructionsStrings.ADD.value
    rd = "000001"
    rs1 = "000011"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)
    return instr

def addi_r1_r1_1():
    opcode = InstructionsStrings.ADDI.value
    rd = "000001"
    rs1 = "000001"
    imm_src = "1"

    rd_int = int(rd, 2)
    rs1_int = int(rs1, 2)
    imm_int = int(imm_src, 2)
    rs1_value = 4
    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    return instr

def test_add():
    opcode = InstructionsStrings.ADD.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    rd_int = int(rd, 2)
    rs1_int = int(rs1, 2)
    rs2_int = int(rs2, 2)

    rs1_value = 4
    rs2_value = 5

    instr = add_r1_r2_r3()

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(2, rs1_value)
    cpu.set_register(3, rs2_value)

    cpu.cycle()

    rd_int = int(rd, 2)
    rd_value = cpu.read_register(rd_int)
    expected_rd_value = rs1_value + rs2_value
    assert rd_value == expected_rd_value

def test_addi():
    opcode = InstructionsStrings.ADDI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    rd_int = int(rd, 2)
    rs1_int = int(rs1, 2)
    imm_int = int(imm_src, 2)
    rs1_value = 4
    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(rs1_int, rs1_value)

    cpu.cycle()

    rd_int = int(rd, 2)
    rd_value = cpu.read_register(rd_int)
    expected_rd_value = rs1_value + imm_int
    assert rd_value == expected_rd_value


def test_addi_negative():
    opcode = InstructionsStrings.ADDI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "1111_1111_110" # -2

    rd_int = int(rd, 2)
    rs1_int = int(rs1, 2)
    imm_int = -2
    rs1_value = 4
    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(rs1_int, rs1_value)

    cpu.cycle()

    rd_int = int(rd, 2)
    rd_value = cpu.read_register(rd_int)
    expected_rd_value = rs1_value + imm_int
    assert rd_value == expected_rd_value


def test_beq():

    instr_0 = beq_r0_r0_2()
    instr_1 = add_r1_r2_r3()
    instr_2 = add_r1_r3_r3()

    ram = RAM(10)

    ram.write_addr(0, instr_0)
    ram.write_addr(1, instr_1)
    ram.write_addr(2, instr_2)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    r1_value = 5
    r2_value = 3 
    r3_value = 6
    cpu.set_register(1, r1_value)
    cpu.set_register(2, r2_value)
    cpu.set_register(3, r3_value)

    cpu.cycle() # should be beq instr
    cpu.cycle() # should be r1 = r3 + r3

    rd = 1
    rd_value = cpu.read_register(rd)
    expected_rd_value = r3_value + r3_value
    assert rd_value == expected_rd_value

def test_beq_loop():

    instr_0 = addi_r1_r1_1()
    instr_1 = beq_r0_r0_p1()

    ram = RAM(10)

    ram.write_addr(0, instr_0)
    ram.write_addr(1, instr_1)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    r1_value = 5
    r2_value = 3 
    r3_value = 1
    cpu.set_register(1, r1_value)
    cpu.set_register(2, r2_value)
    cpu.set_register(3, r3_value)

    cpu.cycle() # should be r1 += 1
    cpu.cycle() # should be beq instr
    cpu.cycle() # should be r1 += 1

    rd = 1
    rd_value = cpu.read_register(rd)
    expected_rd_value = r1_value + 2
    assert rd_value == expected_rd_value
