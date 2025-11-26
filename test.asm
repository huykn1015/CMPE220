# please ignore this comment
LABEL1:
LABEL2:
lw s0, 8(s1) # test comment
no_op cat dog
            # please ignore this comment
LABEL3:addi s0, zero, 1000#comment
addi s0, zero, -1000
beq zero, zero, LABEL3
jal LABEL1