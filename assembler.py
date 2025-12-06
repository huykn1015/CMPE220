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

# add alternative r register names to lookup
# r1 = 1, r2 = 2, r3 = 3, ... , r31 = 31
for i in range(1, 31+1):
    REGISTER_LOOKUP["r" + str(i)] = i

# remove comments and newlines from each line
# if resulting line is empty, remove it
def assembler_clean(lines: list[str]) -> list[str]:
    clean_lines = []
    for line in lines:
        # remove hashtag comments
        index = line.find("#")
        if (index != -1):
            line = line[:index]
        # remove extra spaces and newlines
        line = line.strip()
        # only add non-empty lines
        if len(line) > 0:
            clean_lines.append(line)
    return clean_lines

def assembler_process_data(lines):
    words: list[int] = []
    label_lookup  = {}
    for line in lines:
        # identify labels
        label_tokens = line.split(":")
        # last token is non-label instruction
        for i in range(len(label_tokens) - 1):
            label = label_tokens[i].strip().upper()
            # labels come before the words on the same line
            label_lookup[label] = len(words)
        words.extend(int(s) for s in label_tokens[-1].split())
    return (words, label_lookup)


# 1. remove newlines and comments from each line
# 2. identify labels and link them with the instruction
#   - labels are anything before a colon
def assembler_preprocess(lines: list[str]) -> list[str, list[str]]:
    line_entries: list[str, list[str]] = []
    for line in lines:
        # identify labels
        tokens = line.split(":")
        labels = []
        # last token is non-label instruction
        for i in range(len(tokens) - 1):
            labels.append(tokens[i].strip())
        line_entries.append([tokens[-1], labels])

    # Add an extra NO_OP instruction at the very end to catch the end labels
    #  (labels that are placed after the final instruction in the assembly code)
    line_entries.append(["NO_OP", []])

    # if DEBUG_PRINT:
    #     print("raw line entries:")
    #     for entry in line_entries:
    #         print(f"{entry}")
    #     print()

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
        print(".text line entries:")
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
def assembler_parse_line(index: int, line: str, text_label_lookup: dict, data_label_lookup: dict) -> str:
    if DEBUG_PRINT:
        print(f"Parsing Instruction {index}: {line}")

    tokens = assembler_tokenize(line)

    if DEBUG_PRINT:
        print(f"Tokens: {list(tokens)}")

    binary_strings: deque[str] = deque()

    # first token from left is always the instruction name
    instr_name = tokens.popleft().upper()
    opcode = Instructions[instr_name].value
    opcode_str = f"{opcode:07b}"
    binary_strings.appendleft(opcode_str)

    def process_reg():
        reg_name = tokens.popleft().lower()
        reg_num = REGISTER_LOOKUP[reg_name]
        binary_strings.appendleft(f"{reg_num:06b}")

    # branch = 0: I-type, imm is either a .data variable or literal integer
    # branch = 1 or 2: Branch/Jump, imm is a label and will translate to offset
    # NOTE: unlike the MIPS jump, the RISCV jump does relative addressing
    def process_imm(branch=0):
        token = tokens.popleft()
        imm = 0
        if branch == 0:  # I-Type
            t = token.upper()
            if t in data_label_lookup:
                imm = int(data_label_lookup[t]) + 1000  # data offset
                print(f"variable address: {imm}")
            else:
                imm = int(token)
        elif branch == 1 or branch == 2:  # branch/jump
            label = token.upper()
            target_index = text_label_lookup[label]
            imm = target_index - index
            if DEBUG_PRINT:
                if branch == 1:
                    print(f"branch offset: {imm}")
                else:
                    print(f"jump offset: {imm}")

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

    operand_names = ["opcode"]

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
        operand_names.extend(["rd", "rs1", "imm"])
    # SW
    elif instr_name == "SW":
        process_reg()  # rs2
        process_imm()  # imm
        process_reg()  # rs1
        # need to swap imm and rs2 to comply with format
        d = binary_strings
        d[0], d[1] = d[1], d[0]
        operand_names.extend(["rs2", "rs1", "imm"])
    # JAL
    elif instr_name == "JAL":
        process_imm(2)  # imm
        operand_names.extend(["imm"])
    # R-Type
    elif opcode_str[1:4] == "001":
        process_reg()  # rd
        process_reg()  # rs1
        process_reg()  # rs2
        operand_names.extend(["rd", "rs1", "rs2"])
    # I-Type
    elif opcode_str[1:4] == "011":
        process_reg()  # rd
        process_reg()  # rs1
        process_imm()  # imm
        operand_names.extend(["rd", "rs1", "imm"])
    # Branch
    elif opcode_str[1:4] == "110":
        process_reg()  # rs1
        process_reg()  # rs2
        process_imm(1)  # imm
        operand_names.extend(["rs1", "rs2", "imm"])

    if DEBUG_PRINT:
        operand_names.reverse()
        line1, line2 = "| ", "| "
        for i, bin in enumerate(binary_strings):
            name = operand_names[i]
            max_width = max(len(bin), len(name))
            line1 += name.rjust(max_width) + " | "
            line2 += bin.rjust(max_width) + " | "
        border = "-" * (len(line1) - 1)
        print(border)
        print(line1[:-1])
        print(line2[:-1])
        print(border)

    # if DEBUG_PRINT:
    #     print(f"Binary Strings: {list(binary_strings)}")

    result = "".join(binary_strings).zfill(32)

    if DEBUG_PRINT:
        print(f"Machine Code: {result}\n")
        print(f"Machine Code: 0x{int(result, 2):08X}\n")

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

    clean_lines = assembler_clean(lines)

    text_lines = []
    data_lines = []
    section = text_lines
    for line in clean_lines:
        if line == ".data":
            section = data_lines
        elif line == ".text":
            section = text_lines
        else:
            section.append(line)

    if (DEBUG_PRINT):
        print(".data lines:")
        for line in data_lines:
            print("\t" + line)
        print(".text lines:")
        for line in text_lines:
            print("\t" + line)
        print()
       
    # process the data lines first
    data_words, data_label_lookup = assembler_process_data(data_lines)

    if (DEBUG_PRINT):
        print(".data words: " + str(data_words))
        print(".data label lookup:" + str(data_label_lookup))
        print()


    line_entries = assembler_preprocess(text_lines)
    # extract lines from first column of line_entries
    # and setup a lookup that maps label to current line number
    lines = []
    text_label_lookup: dict[str, int] = {}
    for i, (line, labels) in enumerate(line_entries):
        for label in labels:
            text_label_lookup[label] = i
        lines.append(line)

    if DEBUG_PRINT:
        print(f".text label lookup: {text_label_lookup}\n")

    machine_codes = []
    for index, line in enumerate(lines):
        machine_codes.append(assembler_parse_line(index, line, text_label_lookup, data_label_lookup))

    text_byte_array = []
    for word in machine_codes:
        text_byte_array.append(int(word[0:8], 2))
        text_byte_array.append(int(word[8:16], 2))
        text_byte_array.append(int(word[16:24], 2))
        text_byte_array.append(int(word[24:32], 2))

    text_zero_array = []
    if (len(text_byte_array) < 1000 * 4):
        text_zero_array = [0] * (1000 * 4 - len(text_byte_array))

    data_byte_array = []
    for word in data_words:
        word_bin = "{0:b}".format(word).rjust(32, "0")
        data_byte_array.append(int(word_bin[0:8], 2))
        data_byte_array.append(int(word_bin[8:16], 2))
        data_byte_array.append(int(word_bin[16:24], 2))
        data_byte_array.append(int(word_bin[24:32], 2))

    data_zero_array = []
    if (len(data_zero_array) < 1000 * 4):
        data_zero_array = [0] * (1000 * 4 - len(data_byte_array))

    if (DEBUG_PRINT):
        print("Binary File Output:")

        print(".text section [0000 - 0999]")
        address = 0
        for i in range(0, len(text_byte_array), 4):
            line = "\t" + str(address).rjust(4, "0") + ": "
            line += " ".join(str(n).rjust(3) for n in text_byte_array[i:i+4])
            address += 1
            print(line)
        print("\t------------------------")
        print(f"\t{address:04} to 0999: all zeroes")

        print(".data section [1000 - 1999]")
        address = 1000
        for i in range(0, len(data_byte_array), 4):
            line = "\t" + str(address).rjust(4, "0") + ": "
            line += " ".join(str(n).rjust(3) for n in data_byte_array[i:i+4])
            address += 1
            print(line)
        print("\t------------------------")
        print(f"\t{address:04} to 1999: all zeroes")

    if dest_filename:
        with open(dest_filename, "wb") as f:
            f.write(bytes(text_byte_array))
            f.write(bytes(text_zero_array))
            f.write(bytes(data_byte_array))
            f.write(bytes(data_zero_array))
