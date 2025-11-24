from abc import ABC, abstractmethod

from instructions import decode_instruction, Flags



ZERO = 0
STACK_POINTER_REGISTER = 30
RETURN_ADDRESS_REGITSTER = 31



class RegisterFile:
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



class Memory(ABC):
    @abstractmethod
    def write_addr(self, addr: int, value: int) -> None:
        raise NotImplementedError("")
    @abstractmethod
    def read_addr(self, addr: int) -> int:
        raise NotImplementedError("")





class RAM(Memory):
    def __init__(self, size: int):
        self._size = size
        self._memory: list[int] = [0] * size

    def load_file(self, file_path: str):
        res: list[int]= []
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4)
                if len(chunk) < 4:
                    break
                res.append(int.from_bytes(chunk, 'little'))
        self._memory = res
        self._size = len(res)


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
    def __init__(self, random_access_memory: Memory, max_ram_addr: int | None = None, memory_mapped_io: Memory | None = None):
        self._ram: Memory = random_access_memory 
        self._mmio: Memory | None = memory_mapped_io 
        if memory_mapped_io is not None and max_ram_addr is None:
            raise ValueError("")
        self._max_ram_addr: int | None = max_ram_addr

    def read_addr(self, addr: int) -> int:
        if self._max_ram_addr is None:
            return self._ram.read_addr(addr)

        if addr > self._max_ram_addr:
            if self._mmio is None:
                raise ValueError("Address out of bounds")
            return self._mmio.read_addr(addr - self._max_ram_addr)
        return self._ram.read_addr(addr)


    def write_addr(self, addr: int, value: int, flags: int):
        if flags & Flags.MEM_WRITE_FLAG.value <= 0:
            return
        if self._max_ram_addr is None:
            return self._ram.write_addr(addr, value)

        if addr > self._max_ram_addr:
            if self._mmio is None:
                raise ValueError("Address out of bounds")
            return self._mmio.write_addr(addr - self._max_ram_addr, value)
        return self._ram.write_addr(addr, value)


class ProgramCounter:
    def __init__(self, starting_addr: int):
        self._next_instruction: int = starting_addr
    @property
    def next_instruction(self):
        return self._next_instruction
    def set_next_instruction(self, alu_out: int, imm: int, flags: int):
        print(f"cur: {self._next_instruction}")
        if ((flags & Flags.BRANCH_FLAG.value) <= 0) or (alu_out <= 0):
            self._next_instruction = self.next_instruction + 1
        else:
            self._next_instruction = self.next_instruction + imm
        print('pc', flags & Flags.BRANCH_FLAG.value, alu_out,)
        print(f"next: {self._next_instruction}")





def alu(flags: int, rs1: int, rs2: int, imm: int):
    rd: int | None= None

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
        raise ValueError("")
    return rd


class CPU:
    def __init__(self, num_registers: int, bus: Bus):
        self._reg_file: RegisterFile = RegisterFile(num_registers)
        self._pc: ProgramCounter = ProgramCounter(0)
        self._bus: Bus = bus


    def set_register(self, register_number: int, value: int):
        self._reg_file.write_register(register_number, value)

    def read_register(self, register_number: int):
        return self._reg_file.read_register(register_number)

    def cycle(self):
        # print(self._pc.next_instruction)
        instr = self._bus.read_addr(self._pc.next_instruction)

        # decode 
        flags, rd_addr, rs1_addr, rs2_addr, imm =  decode_instruction(instr)
        rs1, rs2 = self._reg_file.read_registers(rs1_addr, rs2_addr)
        
        # execute 

        alu_out = alu(flags, rs1, rs2, imm)

        # mem 
        if flags & Flags.MEM_READ_FLAG.value > 0:
            bus_out = self._bus.read_addr(alu_out)
        else:
            bus_out = 0
        self._bus.write_addr(alu_out, rs2, flags)

        # write back
        self._reg_file.update_register(rd_addr, alu_out, bus_out, flags)
        self._pc.set_next_instruction(alu_out, imm, flags)




