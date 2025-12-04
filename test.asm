.data   # useless comment
    cat:1 2 3 4 5 6    7 8 9 10 #asdfsf
    crow:bird:1000 2000 3000
    dog:
.text  # another useless comment
    # please ignore this comment
    LABEL0:     LABEL1:
    LABEL2:
    lw s0, 8(s1) # test comment
    sw s0, 8(s1) # test comment
    no_op cat dog
                # please ignore this comment
    LABEL5:LABEL4:LABEL3:addi s0, zero, 1000#comment
    addi s0, zero, -1000
    add s1, s2, s3
    beq zero, zero, LABEL3
    jal LABEL1
    jal LABEL4