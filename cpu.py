from abc import ABC, abstractmethod
from enum import Enum
from instructions import decode_instruction, Flags

DEBUG_CPU = True

ZERO = 0
STACK_POINTER_REGISTER = 30
PC_REGISTER = 29
RETURN_ADDRESS_REGITSTER = 31


class RegisterFile:
    """Class representing a CPU's register file."""
    def __init__(self, num_register: int):
        self._registers: list[int] = [0] * num_register

    def read_register(self, read_addr: int) -> int:
        return self._registers[read_addr]

    def read_registers(self, rs1_addr: int, rs2_addr: int) -> tuple[int, int]:
        return self._registers[rs1_addr], self._registers[rs2_addr]

    def write_register(self, write_addr: int, write_value: int):
        if write_addr == 0:
            return
        self._registers[write_addr] = write_value

    def update_register(self, write_addr: int, alu_out: int, bus_out: int, flags: int):
        if flags & Flags.REG_WRITE_FLAG.value <= 0:
            return
        write_value = bus_out if flags & Flags.MEM_READ_FLAG.value > 0 else alu_out
        self.write_register(write_addr, write_value)

    def dump_regs(self):
        return self._registers[:]

class Memory(ABC):
    @abstractmethod
    def write_addr(self, addr: int, value: int) -> None:
        raise NotImplementedError("")
    @abstractmethod
    def read_addr(self, addr: int) -> int:
        raise NotImplementedError("")





class STDOut(Memory):
    """Class imitating a basic stdout mmio device"""
    def __init__(self):
        self._buffer: str = ""
    
    def read_addr(self, addr: int) -> int:
        # reads are not allowed, so zero is always returned
        return 0
    
    def write_addr(self, addr: int, value: int) -> None:
        # if any value is written to addr 1, buffer is flushed and printed to stdout
        if addr == 1:
            print(f"STDOUT: {self._buffer}")
            self._buffer = ""
        else:
            # writes to any other address append to the buffer
            self._buffer = self._buffer + (chr(value))



class RAM(Memory):
    """Class representing Random Access Memory"""
    def __init__(self, size: int, stack_addr: int | None = None):
        self._size: int = size
        self._stack_addr: int | None = stack_addr
        self._memory: list[int] = [0] * size

    def load_file(self, file_path: str):
        res: list[int]= []
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4)
                if len(chunk) < 4:
                    break
                res.append(int.from_bytes(chunk, 'big'))
        if self._stack_addr is not None and len(res) > self._stack_addr:
            raise ValueError(f"program too large for RAM (program = {len(res)}, ram = {self._stack_addr})")    
        if len(res) > self._size:
            raise ValueError(f"program too large for RAM (program = {len(res)}, ram = {self._size})")    

        for i, word in enumerate(res):
            self._memory[i] = word          


    def write_addr(self, addr: int, value: int) -> None:
        if addr > self._size:
            raise ValueError(f"Addres out of bounds. Addr: {addr}. Ram size: {self._size}")
        self._memory[addr] = value
        # print('write', addr, self._memory)
    
    def read_addr(self, addr: int) -> int:
        # print('read', addr, self._memory)
        if addr > self._size:
            raise ValueError(f"Addres out of bounds. Addr: {addr}. Ram size: {self._size}")
        return self._memory[addr]


class Bus:
    """Class that handles read/write oeprations to ram and a singular I/O device"""
    def __init__(self, random_access_memory: Memory, max_ram_addr: int | None = None, memory_mapped_io: Memory | None = None):
        self._ram: Memory = random_access_memory 
        self._mmio: Memory | None = memory_mapped_io 
        if memory_mapped_io is not None and max_ram_addr is None:
            raise ValueError("")
        self._max_ram_addr: int | None = max_ram_addr

    def read_addr(self, addr: int) -> int:
        # read an address, if it exceeds the ram max addr, it is a read to the mmio device
        if self._max_ram_addr is None:
            print(f"bus read, addr: {addr} [{self._ram.read_addr(addr)}]")
            return self._ram.read_addr(addr)

        if addr > self._max_ram_addr:
            if self._mmio is None:
                raise ValueError("Address out of bounds")
            return self._mmio.read_addr(addr - self._max_ram_addr)
        # print(f"bus read, addr: {addr} [{self._ram.read_addr(addr)}]")
        return self._ram.read_addr(addr)


    def write_addr(self, addr: int, value: int, flags: int):
        # write to an address, if it exceeds the ram max addr, it is a write to the mmio device
        if flags & Flags.MEM_WRITE_FLAG.value <= 0:
            return
        if self._max_ram_addr is None:
            return self._ram.write_addr(addr, value)

        if addr >= self._max_ram_addr:
            if self._mmio is None:
                raise ValueError("Address out of bounds")
            return self._mmio.write_addr(addr - self._max_ram_addr, value)
        return self._ram.write_addr(addr, value)


class ProgramCounter:
    """Class representing a CPU's program counter."""
    def __init__(self, starting_addr: int):
        self._next_instruction: int = starting_addr
    @property
    def next_instruction(self):
        return self._next_instruction

    def write_next_instruction(self, value: int):
        self._next_instruction = value

    def set_next_instruction(self, alu_out: int, imm: int, flags: int):
        # incremements pc by imm if alu_out != 0, else inc pc
        if ((flags & Flags.BRANCH_FLAG.value) <= 0) or (alu_out <= 0):
            self._next_instruction = self.next_instruction + 1
        else:
            self._next_instruction = self.next_instruction + imm





def alu(flags: int, rs1: int, rs2: int, imm: int):
    rd: int | None= None

    # do operation based off which alu flag is set
    if flags & Flags.USE_IMM_FLAG.value:
        rs2 = imm
    if flags & Flags.ALUOP_ADD_FLAG.value:
        rd = rs1 + rs2
    elif flags & Flags.ALUOP_MUL_FLAG.value:
        rd = rs1 * rs2
    elif flags & Flags.ALUOP_SHL_FLAG.value:
        rd = rs1 << rs2
    elif flags & Flags.ALUOP_SHR_FLAG.value:
        rd = rs1 >> rs2
    elif flags & Flags.ALUOP_SUB_FLAG.value:
        rd = rs1 - rs2
    elif flags & Flags.ALUOP_SLT_FLAG.value:
        rd = 1 if rs1 < rs2 else 0
    elif flags & Flags.ALUOP_SGE_FLAG.value:
        rd = 1 if rs1 >= rs2 else 0
    elif flags & Flags.ALUOP_SNE_FLAG.value:
        rd = 1 if rs1 != rs2 else 0
    elif flags & Flags.ALUOP_SEQ_FLAG.value:
        rd = 1 if rs1 == rs2 else 0
    else:
        # at least 1 alu op flag must be set
        raise ValueError("")
    return rd


class CPU:
    """CPU class that completes one instruction per clock cycle."""
    def __init__(self, num_registers: int, bus: Bus):
        self._reg_file: RegisterFile = RegisterFile(num_registers)
        self._pc: ProgramCounter = ProgramCounter(0)
        self._bus: Bus = bus


    def set_register(self, register_number: int, value: int):
        self._reg_file.write_register(register_number, value)

    def read_register(self, register_number: int):
        return self._reg_file.read_register(register_number)

    def cycle(self):
        # fetch stage
        instr = self._bus.read_addr(self._pc.next_instruction) # read raw instruction bits from bus

        # decode stage
        flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr) # decode instruction
        if flags == 0:
            # if no flags are set, then EOF reached ( EOF coded as no op)
            print(">Reached End of Program")
            exit()
        rs1, rs2 = self._reg_file.read_registers(rs1_addr, rs2_addr) # read register file

        # execute stage
        alu_out = alu(flags, rs1, rs2, imm) # do alu calculation

        # memory stage
        if flags & Flags.MEM_READ_FLAG.value > 0:
            bus_out = self._bus.read_addr(alu_out) # read memory if memory read flag was set
        else:
            bus_out = 0
        self._bus.write_addr(alu_out, rs2, flags) # write to bus if write flag was set

        # write back stage
        self._reg_file.update_register(rd_addr, alu_out, bus_out, flags) # update registers if operation has a return
        self._pc.set_next_instruction(alu_out, imm, flags) # update pc for next instruction 


class CPUStates(Enum):
    STOPPED = -1
    FETCH = 0
    DECODE = 1 
    EXECUTE = 2 
    MEM = 3 
    WB = 4


class CPUClocked:
    def __init__(self, num_registers: int, bus: Bus):
        self._reg_file: RegisterFile = RegisterFile(num_registers)
        self._pc: ProgramCounter = ProgramCounter(0)
        self._bus: Bus = bus
        self._state: CPUStates = CPUStates.FETCH

        self._instr: int = 0
        self._flags: int = 0
        self._rd_addr: int = 0
        self._rs1_addr: int = 0
        self._rs2_addr: int = 0
        self._imm: int = 0
        self._rs1 : int= 0 
        self._rs2: int = 0
        self._alu_out: int = 0
        self._bus_out: int = 0




    def dump_regs(self) -> list[int]:
        return self._reg_file.dump_regs()

    @property
    def next_instruction(self) -> int:
        return self._pc.next_instruction

    @property
    def cur_state(self) -> int:
        return self._state.value

    def set_register(self, register_number: int, value: int):
        self._reg_file.write_register(register_number, value)

    def read_register(self, register_number: int):
        return self._reg_file.read_register(register_number)

    def cycle(self) -> int:
        # print(self._pc.next_instruction)
        cur_state = self._state

        if DEBUG_CPU:
            print(f"\n[STATE = {self._state.name}] [PC = {self._pc.next_instruction}")
            if self._instr != 0 and self._state != CPUStates.FETCH:
                print(f" INSTR = 0x{self._instr:08X} ")

            reg = self._reg_file.dump_regs()
            t0, t1, t2 = reg[5], reg[6], reg[7]
            print(f" r1 = {reg[1]},  r2 = {reg[2]}, r30 = {reg[30]}, r31 = {reg[31]}")


        match self._state:
            # fetch stage
            case CPUStates.FETCH:
                # read raw instruction bits from memory
                self._instr = self._bus.read_addr(self._pc.next_instruction) 
                self._state = CPUStates.DECODE
            # decode stage
            case CPUStates.DECODE:
                # decodes instruction for control flags, and reads register file
                self._flags, self._rd_addr, self._rs1_addr, self._rs2_addr, self._imm =  decode_instruction(self._instr)
                if self._flags == 0:
                    print(">Reached End of Program")
                    return CPUStates.STOPPED.value

                self._rs1, self._rs2 = self._reg_file.read_registers(self._rs1_addr, self._rs2_addr)
                self._state = CPUStates.EXECUTE
            # execute stage
            case CPUStates.EXECUTE:
                # execute alu based on control flags
                self._alu_out = alu(self._flags, self._rs1, self._rs2, self._imm)

                self._state = CPUStates.MEM
            # memory stage
            case CPUStates.MEM:
                # perform memory read/writes if applicable
                if self._flags & Flags.MEM_READ_FLAG.value > 0:
                    
                    self._bus_out = self._bus.read_addr(self._alu_out)
                else:
                    self._bus_out = 0
                self._bus.write_addr(self._alu_out, self._rs2, self._flags)
                self._state = CPUStates.WB

            # write back stage
            case CPUStates.WB:
                # write back to registers if applicable and update pc
                if self._rd_addr == PC_REGISTER:
                    print(f'write to pc reg {self._bus_out}')
                    self._pc.write_next_instruction(self._bus_out)
                elif ((self._flags & Flags.JAL_FLAG.value) > 0):
                    self._reg_file.write_register(RETURN_ADDRESS_REGITSTER, self._pc.next_instruction + 1)
                    self._pc.set_next_instruction(self._alu_out, self._imm, self._flags)
                else:
                    self._reg_file.update_register(self._rd_addr, self._alu_out, self._bus_out, self._flags)
                    self._pc.set_next_instruction(self._alu_out, self._imm, self._flags)
                self._state = CPUStates.FETCH
            case _:
                return CPUStates.STOPPED.value
        return cur_state.value
