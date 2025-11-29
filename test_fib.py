from cpu import RAM, Bus, CPUClocked, CPUStates

def main():

    ram = RAM(size=256)

    ram.load_file("Fibsq.bin")

    bus = Bus(random_access_memory=ram) 
    cpu = CPUClocked(num_registers=32, bus=bus)


    while True:
        state = cpu.cycle()
        if state == CPUStates.STOPPED.value:
            break

    T1_INDEX = 6
    result = cpu.read_register(T1_INDEX)
    print("t1 =", result)
    print("All regs:", cpu.dump_regs())

if __name__ == "__main__":
    main()
