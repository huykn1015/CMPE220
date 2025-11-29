# Software CPU Design
## Supported instructions (RISC V)
- NO_OP
- ADD/ADDI
- SUB/SUBI
- MUL/MULI
- SHL/SHLI
- SHR/SHRI
- SLT/SLTI
- BEQ
- BNE
- BGE
- BLT
- LW
- SW
- JAL
## Register Information
Size: 32 bit  
For ALU operations using 2 source registers and LW:  
>[0:6] — op code  
>[7:13] — destination register  
>[14:20] — source register 1  
>[21:26] — source register 2  
>[27:31] — padding  

For ALU operations using an immediate value:  
>[0:6] — opcode  
>[7:13] — destination register  
>[14:20] — source register  
>[21:31] — immediate value  

For branch operations and SW:  
>[0:6] — op code  
>[7:13] — source register 1  
>[14:20] — source register 2  
>[21:31] — immediate value  

For JAL:  
>[0:6] — op code  
>[7:31] — immediate value

## How to download and run the program  
1. Clone this github repo and cd into its directory
2. Assemble the respective program by running `python3 assembler.py Fibsq.asm Fibsq.bin` or `python3 assembler.py hello_world.asm hello_world.bin`
3. Run the respective CPU emulator with `python3 test_fib.py` or `python3 test_hello.py`

## CPU Architecture Schematic
![alt text](https://github.com/huykn1015/CMPE220/blob/main/misc/cpu.png)
