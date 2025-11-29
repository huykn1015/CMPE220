START:
    ADDI a1, zero, 256      # a1 = base MMIO address (RAM end)

    # H
    ADDI t0, zero, 72       # 'H'
    SW   a1, 0(t0)
    # e
    ADDI t0, zero, 101      # 'e'
    SW   a1, 0(t0)
    # l
    ADDI t0, zero, 108      # 'l'
    SW   a1, 0(t0)
    # l
    ADDI t0, zero, 108      # 'l'
    SW   a1, 0(t0)
    # o
    ADDI t0, zero, 111      # 'o'
    SW   a1, 0(t0)
    # ,
    ADDI t0, zero, 44       # ','
    SW   a1, 0(t0)
    # space
    ADDI t0, zero, 32       # ' '
    SW   a1, 0(t0)
    # W
    ADDI t0, zero, 87       # 'W'
    SW   a1, 0(t0)
    # o
    ADDI t0, zero, 111      # 'o'
    SW   a1, 0(t0)
    # r
    ADDI t0, zero, 114      # 'r'
    SW   a1, 0(t0)
    # l
    ADDI t0, zero, 108      # 'l'
    SW   a1, 0(t0)
    # d
    ADDI t0, zero, 100      # 'd'
    SW   a1, 0(t0)
    # !
    ADDI t0, zero, 33       # '!'
    SW   a1, 0(t0)
    # newline
    ADDI t0, zero, 10       # '\n'
    SW   a1, 0(t0)

    ADDI t0, zero, 0
    SW   a1, 1(t0)

END:
    NO_OP