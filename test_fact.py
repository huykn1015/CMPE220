
from enum import Enum
from os import wait
from cpu import  Bus, RAM, CPU, STDOut, CPUClocked
from instructions import Flags, r_type, i_type, b_type, lw, sw, Instructions, jal





STACK_ADDR = 50

MAX_RAM_ADDR = 1000
FACT = 4
RETURN = 10
END = 13

if __name__ == '__main__':
    ram = RAM(MAX_RAM_ADDR + 1)

    instr_0 = i_type(Instructions.ADDI, 1, 0, 5) # r1 = r0 + 10
    # instr_1 = i_type(Instructions.ADDI, 30, 0, STACK_ADDR) # r30 =  STACK_ADDR
    instr_1 = jal(FACT)
    instr_2 = lw(1, 30, 1) # pop from stack 
    instr_3 = lw(31, 30, 0) # pop from stack 
    instr_4 = b_type(Instructions.BEQ, 0, 0, END) # go to end of program 
    instr_5 = i_type(Instructions.ADDI, 2, 0, 1) # ADDI r2, zero, 1 # fact
    instr_6 = b_type(Instructions.BEQ, 1, 2, RETURN) # BEQ r1, r2, return
    instr_7 = sw(30, 31, 0) # push prev return addr onto stack
    instr_8 = sw(30, 1, 1) # push r1 onto stack
    instr_9 = i_type(Instructions.ADDI, 30, 30, 2) # increment stack pointer by 2 
    instr_10 = i_type(Instructions.ADDI, 1, 1, -1) # next arg is r1 - 1 
    instr_11 = jal(-6)
    instr_12 = i_type(Instructions.ADDI, 30, 30, -2) # move a copy of stack ptr to 28
    instr_13 = lw(1, 30, 1) # r1 from stack 
    instr_14 = lw(31, 30, 0) # pop ret addr from stack 
    instr_15 = r_type(Instructions.MUL, 2, 1, 2) # r2 = r1 * r2
    instr_16 = r_type(Instructions.ADD, 29, 0, 31) # jump to r31
    instr_17 = 0


    instructions = [instr_0,
                    instr_1,
                    instr_2, instr_3,
                    instr_4, instr_5, instr_6, instr_7, instr_8, 
                    instr_9, instr_10, instr_11, instr_12, instr_13, instr_14,
                    instr_15, instr_16, instr_17]
    for i, instr in enumerate(instructions):
        ram.write_addr(i, instr)

    std_out = STDOut()
    bus = Bus(ram, MAX_RAM_ADDR, std_out)

    expected_mem_value = 2
    cpu = CPUClocked(num_registers=32, bus=bus)
    cpu.set_register(30, STACK_ADDR)
    while True:
        z = cpu.cycle()
        if z == -1:
            break

