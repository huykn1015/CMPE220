from cpu import RAM, Bus, CPUClocked, CPUStates, STDOut

STACK_ADDR = 2500
MAX_RAM_ADDR = 3000

def main():
    ram = RAM(size=MAX_RAM_ADDR + 1)
    ram.load_file("fact.bin")

    mmio = STDOut()
    bus = Bus(random_access_memory=ram, max_ram_addr=MAX_RAM_ADDR, memory_mapped_io=mmio)
    cpu = CPUClocked(num_registers=32, bus=bus)

    cpu.set_register(30, STACK_ADDR)
    while True:
        state = cpu.cycle()
        if state == CPUStates.STOPPED.value:
            break

if __name__ == "__main__":
    main()
