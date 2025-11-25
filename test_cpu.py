from cpu import  Bus, RAM, CPU
from instructions import Flags, Instructions, r_type, i_type, b_type, lw, sw


def test_add():
    rd_addr = 1
    rs1_addr = 2
    rs1_value = 4
    rs2_addr = 3
    rs2_value = 5

    instr = r_type(Instructions.ADD, rd_addr, rs1_addr, rs2_addr)

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    cpu.set_register(rs1_addr, rs1_value)
    cpu.set_register(rs2_addr, rs2_value)

    cpu.cycle()

    rd_value = cpu.read_register(rd_addr)
    expected_rd_value = rs1_value + rs2_value
    assert rd_value == expected_rd_value


def test_addi():
    rd_addr = 1
    rs1_addr = 2
    rs1_value = 4
    imm_value = 7
    instr = i_type(Instructions.ADDI, rd_addr, rs1_addr, imm_value)

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    cpu.set_register(rs1_addr, rs1_value)

    cpu.cycle()

    rd_value = cpu.read_register(rd_addr)
    expected_rd_value = rs1_value + imm_value
    assert rd_value == expected_rd_value


def test_sub():
    rd_addr = 1
    rs1_addr = 2
    rs1_value = 4
    rs2_addr = 3
    rs2_value = 5

    instr = r_type(Instructions.SUB, rd_addr, rs1_addr, rs2_addr)
    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(rs1_addr, rs1_value)
    cpu.set_register(rs2_addr, rs2_value)

    cpu.cycle()

    rd_value = cpu.read_register(rd_addr)
    expected_rd_value = rs1_value - rs2_value
    assert rd_value == expected_rd_value


def test_subi():

    
    rd_addr = 1
    rs1_addr = 2
    rs1_value = 4
    imm_value = -2
    instr = i_type(Instructions.SUBI, rd_addr, rs1_addr, imm_value)


    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(rs1_addr, rs1_value)

    cpu.cycle()

    rd_value = cpu.read_register(rd_addr)
    expected_rd_value = rs1_value - imm_value
    assert rd_value == expected_rd_value


def test_addi_negative():
    rd_addr = 1 
    rs1_addr = 1 
    rs1_value = 4
    imm_value = -2

    instr = i_type(Instructions.ADDI, rd_addr, rs1_addr, imm_value)

    ram = RAM(10)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    
    cpu.set_register(rs1_addr, rs1_value)

    cpu.cycle()

    rd_value = cpu.read_register(rd_addr)
    expected_rd_value = rs1_value + imm_value
    assert rd_value == expected_rd_value


def test_beq():

    instr_0 = b_type(Instructions.BEQ, 0, 0, 2) # skip next instr
    instr_1 = r_type(Instructions.ADD, 1, 2, 3) # r1 = r2 + r3
    instr_2 = r_type(Instructions.ADD, 1, 3, 3) # r1 = r3 + r3

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

    instr_0 = i_type(Instructions.ADDI, 1, 1, 1)
    instr_1 = b_type(Instructions.BEQ, 0, 0, -1)

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


def test_beq_no_loop():

    instr_0 = i_type(Instructions.ADDI, 1, 1, 1)
    # instr_1 = beq_r0_r1_p1()
    instr_1 = b_type(Instructions.BEQ, 0, 1, -1)

    ram = RAM(10)

    ram.write_addr(0, instr_0)
    ram.write_addr(1, instr_1)
    ram.write_addr(2, instr_1)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    r1_value = 5
    r2_value = 3 
    r3_value = 1
    cpu.set_register(1, r1_value)
    cpu.set_register(2, r2_value)
    cpu.set_register(3, r3_value)

    rd = 1
    cpu.cycle() # should be r1 += 1
    cpu.cycle() # should be beq instr
    cpu.cycle() # should be beq instr

    rd_value = cpu.read_register(rd)
    expected_rd_value = r1_value + 1
    assert rd_value == expected_rd_value


def test_bne_loop():

    instr_0 = i_type(Instructions.ADDI, 1, 1, 1)
    instr_1 = b_type(Instructions.BNE, 0, 1, -1)

    ram = RAM(10)

    ram.write_addr(0, instr_0)
    ram.write_addr(1, instr_1)
    ram.write_addr(2, instr_1)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    r1_value = 1
    r2_value = 3 
    r3_value = 1
    cpu.set_register(1, r1_value)
    cpu.set_register(2, r2_value)
    cpu.set_register(3, r3_value)

    cpu.cycle() # should be r1 += 1
    cpu.cycle() # should be beq instr
    cpu.cycle() # should be beq instr

    rd = 1
    rd_value = cpu.read_register(rd)
    expected_rd_value = r1_value + 2
    assert rd_value == expected_rd_value






def test_sw():
    instr = sw(0, 2, 10)

    ram = RAM(11)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)

    r2_value = 3
    cpu.set_register(2, r2_value)

    cpu.cycle() 

    mem_value = bus.read_addr(10)
    expected_mem_value = r2_value
    assert mem_value == expected_mem_value



def test_sw_2():
    instr = sw(1, 2, 8)

    ram = RAM(11)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)

    cpu = CPU(num_registers=32, bus=bus)
    r1_value = 2
    r2_value = 3
    cpu.set_register(1, r1_value)
    cpu.set_register(2, r2_value)

    cpu.cycle() 

    mem_value = bus.read_addr(10)
    expected_mem_value = r2_value
    assert mem_value == expected_mem_value


def test_lw():
    instr = lw(2, 0, 10)

    ram = RAM(11)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)
    expected_mem_value = 2
    bus.write_addr(10, expected_mem_value, Flags.MEM_WRITE_FLAG.value)
    cpu = CPU(num_registers=32, bus=bus)

    cpu.cycle() # should be r2 = 2
    r2_value = cpu.read_register(2)
    assert r2_value == expected_mem_value


def test_lw_2():
    instr = lw(2, 1, 8)

    ram = RAM(11)

    ram.write_addr(0, instr)

    bus = Bus(ram, None, None)
    expected_mem_value = 2
    bus.write_addr(10, expected_mem_value, Flags.MEM_WRITE_FLAG.value)
    cpu = CPU(num_registers=32, bus=bus)
    r1_value = 2
    cpu.set_register(1, r1_value)
    cpu.cycle() # should be r2 = 2
    r2_value = cpu.read_register(2)
    assert r2_value == expected_mem_value

