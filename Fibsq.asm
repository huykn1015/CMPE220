START:
	ADD  t0, zero, zero
	ADDI t1, zero, 1         

	ADDI t2, zero, 9

LOOP:

	ADD  t3, t0, t1 

	ADD  t0, t1, zero
	ADD  t1, t3, zero

	ADDI t2, t2, -1
	BNE  t2, zero, LOOP


END:				#store final in t1
	NO_OP