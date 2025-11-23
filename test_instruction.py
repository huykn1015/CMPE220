from enum import Enum
from instructions import Instructions, Flags, decode_instruction

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

def test_add():
    opcode = InstructionsStrings.ADD.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_ADD_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_addi():
    opcode = InstructionsStrings.ADDI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_ADD_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)

def test_sub():
    opcode = InstructionsStrings.SUB.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SUB_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_subi():
    opcode = InstructionsStrings.SUBI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_SUB_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)

def test_mul():
    opcode = InstructionsStrings.MUL.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_MUL_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_muli():
    opcode = InstructionsStrings.MULI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_MUL_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)

def test_shl():
    opcode = InstructionsStrings.SHL.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SHL_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_shli():
    opcode = InstructionsStrings.SHLI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_SHL_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)


def test_shr():
    opcode = InstructionsStrings.SHR.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SHR_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_shri():
    opcode = InstructionsStrings.SHRI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_SHR_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)

def test_slt():
    opcode = InstructionsStrings.SLT.value
    rd = "000001"
    rs1 = "000010"
    rs2 = "000011"
    instr = int(f"{rs2}{rs1}{rd}{opcode}".replace('_', ''), 2)

    # instr = 0b_000011_000010_000001_0001000
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SLT_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)


def test_slti():
    opcode = InstructionsStrings.SLTI.value
    rd = "000001"
    rs1 = "000010"
    imm_src = "111"

    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)
    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_SLT_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)

def test_beq():
    opcode = InstructionsStrings.BEQ.value
    rs1 = "000010"
    rs2 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SEQ_FLAG.value) > 0
    assert (flags & Flags.BRANCH_FLAG.value) > 0
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)
    assert imm == int(imm_src, 2)

def test_bne():
    opcode = InstructionsStrings.BNE.value
    rs1 = "000010"
    rs2 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SNE_FLAG.value) > 0
    assert (flags & Flags.BRANCH_FLAG.value) > 0
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)
    assert imm == int(imm_src, 2)

def test_blt():
    opcode = InstructionsStrings.BLT.value
    rs1 = "000010"
    rs2 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SLT_FLAG.value) > 0
    assert (flags & Flags.BRANCH_FLAG.value) > 0
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)
    assert imm == int(imm_src, 2)

def test_bge():
    opcode = InstructionsStrings.BGE.value
    rs1 = "000010"
    rs2 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 2
    assert (flags & Flags.ALUOP_SGE_FLAG.value) > 0
    assert (flags & Flags.BRANCH_FLAG.value) > 0
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)
    assert imm == int(imm_src, 2)

def test_sw():
    opcode = InstructionsStrings.SW.value
    rs1 = "000010"
    rs2 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs2}{rs1}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 3
    assert (flags & Flags.ALUOP_ADD_FLAG.value) > 0
    assert (flags & Flags.MEM_WRITE_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rs1_addr == int(rs1, 2)
    assert rs2_addr == int(rs2, 2)
    assert imm == int(imm_src, 2)

def test_lw():
    opcode = InstructionsStrings.LW.value
    rd = "000010"
    rs1 = "000011"
    imm_src = "111"
    instr = int(f"{imm_src}{rs1}{rd}{opcode}".replace('_', ''), 2)

    flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)

    num_set_flags = flags.bit_count()
    assert num_set_flags == 4
    assert (flags & Flags.ALUOP_ADD_FLAG.value) > 0
    assert (flags & Flags.REG_WRITE_FLAG.value) > 0
    assert (flags & Flags.MEM_READ_FLAG.value) > 0
    assert (flags & Flags.USE_IMM_FLAG.value) > 0
    assert rd_addr == int(rd, 2)
    assert rs1_addr == int(rs1, 2)
    assert imm == int(imm_src, 2)
