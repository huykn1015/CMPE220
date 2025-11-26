import sys
from collections import deque
from instructions import Instructions

DEBUG_PRINT = True

# register names are in order based on RISC-V spec
ABI_NAMES = [
    "zero", "ra", "sp", "gp", "tp",
    "t0", "t1", "t2", "s0", "s1",
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
    "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
    "t3", "t4", "t5", "t6"
]

# construct a lookup table that maps register name to register number
REGISTER_LOOKUP = {name : i for i, name in enumerate(ABI_NAMES)}

# 1. remove newlines and comments from each line
# 2. identify labels and link them with the instruction
#   - labels are anything before a colon
def assembler_preprocess(lines: list[str]) -> list[str, list[str]]:
    line_entries: list[str, list[str]] = []
    for line in lines:
        # remove hashtag comments
        index = line.find("#")
        if (index != -1):
            line = line[:index]
        # remove extra spaces and newlines
        line = line.strip()
        # identify label
        index = line.find(":")
        label = ""
        if (index != -1):
            label = line[:index].strip().upper()
            if index == len(line)-1:
                line = ""
            else:
                line = line[index+1:]
        line_entries.append([
            line,
            [label] if label else []
        ])

    if DEBUG_PRINT:
        print("raw line entries:")
        for entry in line_entries:
            print(f"{entry}")
        print()

    # remove entries with empty line 
    # if removed entry has labels, transfer those labels to
    #   the next entry with non-empty lines
    revised_entries = []
    orphaned_labels = []
    for entry in line_entries:
        line, labels = entry
        # non-empty line
        if line:
            labels.extend(orphaned_labels)
            orphaned_labels.clear()
            revised_entries.append(entry)
        # empty line
        else:
            orphaned_labels.extend(labels)

    if DEBUG_PRINT:
        print("revised line entries:")
        for entry in revised_entries:
            print(f"{entry}")
        print()

    return revised_entries


# splits line into tokens.
# a token is a group of contiguous characters that are alphanumeric, "_", or "-" 
# anything else is a delimiter
# supports hashtag comments at the end of the line.
def assembler_tokenize(line: str) -> deque[str]:
    tokens = [[]]
    for char in line:
        if char.isalnum() or char == "_" or char == "-":
            tokens[-1].append(char)
        elif len(tokens[-1]) > 0:
            tokens.append([])
    tokens = deque("".join(char_list) for char_list in tokens)
    if len(tokens[-1]) == 0:
        tokens.pop()
    return tokens

# converts assembly instruciton to 32 bit machine code
def assembler_parse_line(index: int, line: str, label_lookup: dict[str, int]) -> str:
    if DEBUG_PRINT:
        print(f"Parsing Instruction {index}: {line}")

    tokens = assembler_tokenize(line)

    if DEBUG_PRINT:
        print(f"Tokens: {list(tokens)}")

    binary_strings = deque()

    # first token from left is always the instruction name
    instr_name = tokens.popleft().upper()
    opcode = Instructions[instr_name].value
    opcode_str = f"{opcode:07b}"
    binary_strings.appendleft(opcode_str)

    def process_reg():
        reg_name = tokens.popleft().lower()
        reg_num = REGISTER_LOOKUP[reg_name]
        binary_strings.appendleft(f"{reg_num:06b}")

    # branch = 0: I-type, imm is literal integer
    # branch = 1: Branch, imm is a label and will translate to offset
    # branch = 2: Jump, imm is a label and will translate to direct address
    def process_imm(branch=0):
        token = tokens.popleft()
        imm = 0
        if branch == 0:  # I-Type
            imm = int(token)
        elif branch == 1:  # branch
            label = token.upper()
            target_index = label_lookup[label]
            imm = target_index - index
            if DEBUG_PRINT:
                print(f"branch offset: {imm}")
        else:  # jump
            label = token.upper()
            target_index = label_lookup[label]
            imm = target_index
            if DEBUG_PRINT:
                print(f"jump target: {imm}")

        # python can't do 2's complement so I have to do it myself
        if (imm < 0):
            li = list(f"{-imm:b}")
            flip = False
            for i in reversed(range(len(li))):
                if flip:
                    li[i] = "1" if li[i] == "0" else "0"
                elif li[i] == "1":
                    flip = True
            bin = "".join(li)
        else:
            bin = f"{imm:b}"
        # need to pad with 1s or 0s based on sign
        pad = (branch == 2) and 25 or 11
        binary_strings.appendleft(bin.rjust(pad, "1" if imm < 0 else "0"))

    # NO_OP
    if instr_name == "NO_OP":
        pass
    # LW
    elif instr_name == "LW":
        process_reg()  # rd
        process_imm()  # imm
        process_reg()  # rs1
        # need to swap imm and rs1 to comply with format
        d = binary_strings
        d[0], d[1] = d[1], d[0]
    # SW
    elif instr_name == "SW":
        process_reg()  # rs1
        process_imm()  # imm
        process_reg()  # rs2
        # need to swap imm and rs2 to comply with format
        d = binary_strings
        d[0], d[1] = d[1], d[0]
    # JAL
    elif instr_name == "JAL":
        process_imm(2)  # imm
    # R-Type
    elif opcode_str[1:4] == "001":
        process_reg()  # rd
        process_reg()  # rs1
        process_reg()  # rs2
    # I-Type
    elif opcode_str[1:4] == "011":
        process_reg()  # rd
        process_reg()  # rs1
        process_imm()  # imm
    # Branch
    elif opcode_str[1:4] == "110":
        process_reg()  # rs1
        process_reg()  # rs2
        process_imm(1)  # imm

    if DEBUG_PRINT:
        print(f"Binary Strings: {list(binary_strings)}")

    result = "".join(binary_strings).zfill(32)

    if DEBUG_PRINT:
        print(f"Machine Code: {result}\n")

    return result

# =====================================================================================
# USAGE: python assembler.py <source assembly filename> <destination binary filename>
# (destination binary file can be omitted if you only want to verify console output)
# =====================================================================================
if __name__ == "__main__":
    src_filename = sys.argv[1]
    dest_filename = None
    if (len(sys.argv) >= 3):
        dest_filename = sys.argv[2]

    lines = []
    with open(src_filename, "r") as f:
        lines = f.readlines()
    
    line_entries = assembler_preprocess(lines)
    # extract lines from first column of line_entries
    # and setup a lookup that maps label to current line lumber
    lines = []
    label_lookup: dict[str, int] = {}
    for i, (line, labels) in enumerate(line_entries):
        for label in labels:
            label_lookup[label] = i
        lines.append(line)

    print(label_lookup)
    machine_codes = []
    for index, line in enumerate(lines):
        machine_codes.append(assembler_parse_line(index, line, label_lookup))

    byte_array = []
    for word in machine_codes:
        byte_array.append(int(word[0:8], 2))
        byte_array.append(int(word[8:16], 2))
        byte_array.append(int(word[16:24], 2))
        byte_array.append(int(word[24:32], 2))

    if (DEBUG_PRINT):
        print(f"bytes to be written into binary file:\n{byte_array}")

    if dest_filename:
        with open(dest_filename, "wb") as f:
            f.write(bytes(byte_array))



