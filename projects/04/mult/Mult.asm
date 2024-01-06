//  n = 0; R2 = 0;
//  for (n=0; n<R0; n++) R2 = R2 + R1
//      
(START)
    @n              // n = 0
    M=0

    @R2            // R2 = 0
    M=0

(LOOP)
    @R0
    D=M             // load D = R0

    @n              // D = n - R0
    D=M-D

    @END            // if (n < R0) goto end;
    D;JGE

    @n              // n = n + 1
    D=M
    D=D + 1         
    M=D

    @R1             // R2 = R2 + R1
    D=M
    @R2
    M=M+D

    @LOOP           // goto LOOP
    0;JMP
(END)
    @END
    0;JMP