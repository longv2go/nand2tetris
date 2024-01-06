// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.

    @s          // screen state, 1 : fill, 0: clean
    M=0

(MAIN)          // main loop
    @KBD        // load keyboard register
    D=M
    
    @FILL1      // if (KBD not 0) goto FILL
    D;JGT

    @FILL0
    0;JMP

// ====== FILL 1 ======
(FILL1)          // full screen '1'
    @s
    D=M

    @ENDFILL1    // if s != 0 return
    D;JNE

    @s          // set s to 1
    M=1

    @R0         // call fill(-1, ENDFILL1)
    M=-1
    @ENDFILL1
    D=M
    @R1
    M=D
    @FUNC_FILL
    0;JMP

(ENDFILL1)
    @MAIN
    0;JMP

// ====== FILL 0 ======
(FILL0)         // full screen '0'
    @s
    D=M

    @ENDFILL0    // if s == 0 return
    D;JEQ

    @s          // set s to 0
    M=0

    @R0         // call fill(0, ENDFILL0)
    M=0
    @ENDFILL0
    D=M
    @R1
    M=D
    @FUNC_FILL
    0;JMP

(ENDFILL0)
    @MAIN
    0;JMP

// ====== function fill(what, jmp_addr) ======
(FUNC_FILL)         // screen (32x16=512 words)
    @size
    M=0

(ROWLOOP)
    @size            //  size < 512 goto end loop
    D=M
    @8192
    D=D-A
    @END_ROWLOOP
    D;JGE

    @SCREEN
    D=A
    @size
    D=D+M
    @p              // current write addr
    M=D

    @R0             // @p = R0
    D=M
    @p
    A=M
    M=D

    @size
    M=M+1
    @ROWLOOP
    0;JMP

(END_ROWLOOP)
    @R1         // return to R1
    0;JMP



