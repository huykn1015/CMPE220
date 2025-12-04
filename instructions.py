from enum import Enum, unique

@unique
class Instructions(Enum):
    # Instructions support by the CPU and their respective opcodes
    NO_OP = 0b_0000_00
    # arithmetic first bit is 0, second bit is 1 if use imm
    ADD = 0b_0010_00
    SUB = 0b_0010_01
    MUL = 0b_0010_10
    SHL = 0b_0010_11
    SHR = 0b_0011_00
    SLT = 0b_0011_01
    

    ADDI = 0b_0110_00
    SUBI = 0b_0110_01
    MULI = 0b_0110_10
    SHLI = 0b_0110_11
    SHRI = 0b_0111_00
    SLTI = 0b_0111_01

    # other if first bit is 1, second bit is 1 if jump
    BEQ = 0b_1100_00
    BNE = 0b_1100_01
    BGE = 0b_1100_10
    BLT = 0b_1100_11

    LW = 0b_1000_00
    SW = 0b_1000_10

    JAL = 0b_0000_01



@unique
class Flags(Enum):
    # Flags used by the CPU
    USE_IMM_FLAG   = 0b_1000_0000_0000_0000_00
    ALUOP_ADD_FLAG = 0b_0100_0000_0000_0000_00
    ALUOP_SUB_FLAG = 0b_0010_0000_0000_0000_00
    ALUOP_MUL_FLAG = 0b_0001_0000_0000_0000_00
    ALUOP_SHR_FLAG = 0b_0000_1000_0000_0000_00
    ALUOP_SHL_FLAG = 0b_0000_0100_0000_0000_00
    ALUOP_SLT_FLAG = 0b_0000_0010_0000_0000_00
    ALUOP_SEQ_FLAG = 0b_0000_0001_0000_0000_00
    ALUOP_SNE_FLAG = 0b_0000_0000_1000_0000_00
    ALUOP_SGE_FLAG = 0b_0000_0000_0100_0000_00
    REG_WRITE_FLAG = 0b_0000_0000_0010_0000_00
    MEM_WRITE_FLAG = 0b_0000_0000_0001_0000_00
    MEM_READ_FLAG  = 0b_0000_0000_0000_0000_01

    JAL_FLAG = 0b_0000_0000_0000_1000_00
    BRANCH_NE_FLAG = 0b_0000_0000_0000_0100_00
    BRANCH_GE_FLAG = 0b_0000_0000_0000_0010_00
    BRANCH_LT_FLAG = 0b_0000_0000_0000_0001_00

    BRANCH_FLAG    = 0b_0000_0000_0000_0000_10



USE_IMM_FLAG = Flags.USE_IMM_FLAG.value
ALUOP_ADD_FLAG = Flags.ALUOP_ADD_FLAG.value
ALUOP_SUB_FLAG = Flags.ALUOP_SUB_FLAG.value
ALUOP_MUL_FLAG = Flags.ALUOP_MUL_FLAG.value
ALUOP_SHR_FLAG = Flags.ALUOP_SHR_FLAG.value
ALUOP_SHL_FLAG = Flags.ALUOP_SHL_FLAG.value
ALUOP_SLT_FLAG = Flags.ALUOP_SLT_FLAG.value
ALUOP_SEQ_FLAG = Flags.ALUOP_SEQ_FLAG.value
ALUOP_SNE_FLAG = Flags.ALUOP_SNE_FLAG.value
ALUOP_SGE_FLAG = Flags.ALUOP_SGE_FLAG.value
REG_WRITE_FLAG = Flags.REG_WRITE_FLAG.value
MEM_WRITE_FLAG = Flags.MEM_WRITE_FLAG.value

BRANCH_FLAG = Flags.BRANCH_FLAG.value

JAL_FLAG = Flags.JAL_FLAG.value
BRANCH_NE_FLAG = Flags.BRANCH_NE_FLAG.value
BRANCH_GE_FLAG = Flags.BRANCH_GE_FLAG.value
BRANCH_LT_FLAG = Flags.BRANCH_LT_FLAG.value

MEM_READ_FLAG = Flags.MEM_READ_FLAG.value



#  [] [opcode] [0] [rd] [0] [rs1] [rs2] -> alu ops w/o imm + lw
# [] [opcode] [0] [rd] [0] [rs1] [imm] -> alu ops w/ imm 
# [opcode] [0] [rs1] [0] [rs2] [imm] -> sw / branch
# [opcode] [0] [imm] -> jal

# opcode [0:6]

# RD [7: 13]

# RS1 [14: 20]
# RS2 [21: 26]
# Padding [26: 31]

# IMM [21: 31]

# RS
OPCODE_OFFSET = 0
RD_OFFSET = 7
RS1_OFFSET = 13 # 5 bits for rd 6 for opcode
RS2_OFFSET = 19
IMM_OFFSET = 19
JAL_IMM_OFFSET = 7

OPCODE_MASK = 0b111111
REGISTER_MASK = 0b11111
IMM_MASK = 0b_0111_1111_111
IMM_SIGN_BIT_MASK = 0b_1000_0000_000
JAL_IMM_SIGN_BIT_MASK = 0b_1000_0000_0000_0000_0000_0000_0
JAL_IMM_MASK = 0b_0111_1111_1111_1111_1111_1111_1


def decode_instruction(instruction: int) -> tuple[int, int, int, int, int]:
    """Decodes raw instruction bits into the flags, registers and intermediates needed to execute the instruction"""

    # decode opcode, and register addresses
    opcode = (instruction >> OPCODE_OFFSET) & OPCODE_MASK
    rd_addr = (instruction >> RD_OFFSET) & REGISTER_MASK
    rs1_addr = (instruction >> RS1_OFFSET) & REGISTER_MASK
    rs2_addr = (instruction >> RS2_OFFSET) & REGISTER_MASK
    # convert intermediate to signed integer
    imm = (instruction >> IMM_OFFSET) & IMM_MASK
    imm -= IMM_SIGN_BIT_MASK & (instruction >> IMM_OFFSET)




    flags = 0

    instr = Instructions(opcode)

    match instr:
        # get the flags based on hte instruction opcode
        case Instructions.ADD:
            flags = ALUOP_ADD_FLAG | REG_WRITE_FLAG
        case Instructions.SUB:
            flags = ALUOP_SUB_FLAG | REG_WRITE_FLAG
        case Instructions.MUL:
            flags = ALUOP_MUL_FLAG | REG_WRITE_FLAG
        case Instructions.SHL:
            flags = ALUOP_SHL_FLAG | REG_WRITE_FLAG
        case Instructions.SHR:
            flags = ALUOP_SHR_FLAG | REG_WRITE_FLAG
        case Instructions.SLT:
            flags = ALUOP_SLT_FLAG | REG_WRITE_FLAG


        case Instructions.ADDI:
            flags = ALUOP_ADD_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        case Instructions.SUBI:
            flags = ALUOP_SUB_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        case Instructions.MULI:
            flags = ALUOP_MUL_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        case Instructions.SHLI:
            flags = ALUOP_SHL_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        case Instructions.SHRI:
            flags = ALUOP_SHR_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        case Instructions.SLTI:
            flags = ALUOP_SLT_FLAG | REG_WRITE_FLAG | USE_IMM_FLAG
        
        case Instructions.LW:
            flags = REG_WRITE_FLAG | ALUOP_ADD_FLAG | USE_IMM_FLAG | MEM_READ_FLAG

        case Instructions.SW:
            flags = MEM_WRITE_FLAG | ALUOP_ADD_FLAG | USE_IMM_FLAG

        case Instructions.BEQ:
            flags = BRANCH_FLAG | ALUOP_SEQ_FLAG 
        case Instructions.BNE:
            flags = BRANCH_FLAG | ALUOP_SNE_FLAG 
        case Instructions.BGE:
            flags = BRANCH_FLAG | ALUOP_SGE_FLAG 
        case Instructions.BLT:
            flags = BRANCH_FLAG | ALUOP_SLT_FLAG 

        case Instructions.JAL:
            # for jal, use BEQ instruct but both registers 0 for more imm room
            flags = BRANCH_FLAG | ALUOP_SEQ_FLAG | JAL_FLAG
            
            # JAL imm is larger so use different offsets to calculate it 
            imm = (instruction >> JAL_IMM_OFFSET) & JAL_IMM_MASK
            imm -= JAL_IMM_SIGN_BIT_MASK & (instruction >> (JAL_IMM_OFFSET - 1))
            # print(f"{instruction >> JAL_IMM_OFFSET:24b}")
            # print(f"{JAL_IMM_SIGN_BIT_MASK:24b}")
            # print(f"{instruction >> JAL_IMM_OFFSET}")
            # print(f"{JAL_IMM_SIGN_BIT_MASK & (instruction >> (JAL_IMM_OFFSET - 1))}")
            # print(f"jal imm: {imm}")        
            rs1_addr = 0 
            rs2_addr = 0 
        case _:
            flags = 0

    no_rd_instructions = [Instructions.SW, Instructions.BEQ, Instructions.BNE, Instructions.BGE, Instructions.BLT]
    print(Instructions(opcode))
    if Instructions(opcode) in no_rd_instructions:
            # if an instruction has no destination register, then rs1 is where rd should be, and rs2 is where rs1 should be 
            # rs2 is where rs1 is normally
            rs2_addr = rs1_addr
            # rs1 is where rd is normally
            rs1_addr = rd_addr
    return flags, rd_addr, rs1_addr, rs2_addr, imm

# functions for construction instructions as 32bit integers
def r_type(instr_: Instructions, rd:int, rs1: int, rs2: int) -> int:
    opcode: int = instr_.value
    instr = int(f"{rs2:06b}{rs1:06b}{rd:06b}{opcode:07b}".replace('_', ''), 2)
    return instr


def i_type(instr_: Instructions, rd:int, rs1: int, imm:int) -> int: # increment r1
    opcode: int = instr_.value
    instr = int(f"{imm & 0x7FF:11b}{rs1:06b}{rd:06b}{opcode:07b}".replace('_', ''), 2)
    return instr

def b_type(instr_: Instructions, rs1: int, rs2: int, imm: int) -> int:
    opcode = instr_.value
    instr = int(f"{imm & 0x7FF:11b}{rs2:06b}{rs1:06b}{opcode:07b}".replace('_', ''), 2)
    return instr

def sw(rs1: int, rs2: int, imm: int) -> int:
    opcode = Instructions.SW.value
    instr = int(f"{imm & 0x7FF:11b}{rs2:06b}{rs1:06b}{opcode:07b}".replace('_', ''), 2)
    return instr

def lw(rd: int, rs1: int, imm: int) -> int:
    opcode = Instructions.LW.value
    instr = int(f"{imm & 0x7FF:11b}{rs1:06b}{rd:06b}{opcode:07b}".replace('_', ''), 2)
    return instr

def jal(imm: int) -> int:
    opcode = Instructions.JAL.value
    instr = int(f"{imm & 0xFFFFFF:24b}{opcode:07b}".replace('_', ''), 2)
    return instr

