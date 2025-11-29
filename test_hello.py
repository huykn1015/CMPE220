from cpu import RAM, Bus, CPUClocked, CPUStates, STDOut

def main():
    ram = RAM(size=256)
    ram.load_file("hello_world.bin")

    mmio = STDOut()
    bus = Bus(random_access_memory=ram, max_ram_addr=256, memory_mapped_io=mmio)
    cpu = CPUClocked(num_registers=32, bus=bus)

    while True:
        state = cpu.cycle()
        if state == CPUStates.STOPPED.value:
            break

if __name__ == "__main__":
    main()
