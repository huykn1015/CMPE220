from cpu import RegisterFile, Bus, RAM, alu, ProgramCounter
from instructions import decode_instruction, Flags


reg_file = RegisterFile(num_register=32)

pc = ProgramCounter(starting_addr=0)

ram = RAM(10)

bus = Bus(ram, None, None)













if __name__ == "__Main__":
    while True:
    # fetch
        instr = bus.read_addr(pc.next_instruction)

        # decode 
        flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)
        rs1, rs2 = reg_file.read_registers(rs1_addr, rs2_addr)
        
        # execute 

        alu_out = alu(flags, rs1, rs2, imm)

        # mem 

        bus_out = bus.read_addr(alu_out)
        bus.write_addr(alu_out, rs2, flags)

        # write back
        reg_file.update_register(rd_addr, alu_out, bus_out, flags)
        pc.set_next_instruction(alu_out, imm, flags)
    
    




