START:
	ADDI r1, zero, 5  # load 5 into t1 -> r1 is return and params
	BEQ zero, zero, END
	ADDI r30, zero, 0 # replace 0 with stack start address 
	JAL FACT
	BEQ zero, zero, END
	# r29 is where stack starts 
FACT:
	ADDI r2, zero, 1 # r2 = 1
	# if r1 == 1: jump return 
	BEQ r1, r2, RETURN
	sw r30, 0,(r29) # push prev return registers 
	sw r30, 1(r1) # push r1 onto stack 
	ADDI r30, r30, 2 # -2 if stack grows down 
	ADDI r1, r1, -1 # argument to next call is r1 - 1
	JAL FACT # put PC + 1 into register 31, jump to FACT
	# result is in r2
	# 
	MUL r2, r1, r2 # r1 = r1 * r2

RETURN:
	# restore registers 
	lw r30, 0(r1) # load prev r1 back into r1 
	ADDI r1, r1, -2 # argument to next call is r1 - 1
	lw r29, 0(r30) # read address into r29, which overrides pc 


END:				#store final in t1
	NO_OP
