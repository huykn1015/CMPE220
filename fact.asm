START:
	ADDI r1, zero, 5  # load 5 into t1 -> r1 is return and params, caluclate 5!
	JAL FACT
	# ADDI r30, r30, -2 # decrement stack pointer 
	lw r1, 1(r30) # pop r1 from stack 
	lw r31, 0(r30) # pop ret addr from stack 
	BEQ zero, zero, END # go to end of program 
FACT:
	ADDI r2, zero, 1 # r2 = 1
	BEQ r1, r2, RETURN
	sw r30, 0,(r31) # push prev return registers 
	sw r30, 1(r1) # push r1 onto stack 
	ADDI r30, r30, 2 # -2 if stack grows down 
	ADDI r1, r1, -1 # argument to next call is r1 - 1
	JAL FACT # put PC + 1 into register 31, jump to FACT
	ADDI r30, r30, -2 # decrement stack pointer 
	lw r1, 1(r30) # pop r1 from stack 
	lw r31, 0(r30) # pop ret addr from stack 
	MUL r2, r1, r2 # r1 = r1 * r2
RETURN:
	ADD r29, zero, r31


END:				#store final in t1
	NO_OP
