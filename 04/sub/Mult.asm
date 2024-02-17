// instantiate variables
// sum = 0
@sum
M=0

// i = 1
@i
M=1

(LOOP)
// check exit condition
// exits loop if (i - R1) > 0
@i
D=M

@R1
D=D-M
@STOP
D;JGT

// perform addition towards end result
// increment i
@i
M=M+1

// get value of R0
@R0
D=M

// add value of R0 to sum
@sum
M=M+D

@LOOP
0;JMP

// assign end result
(STOP)
@sum
D=M

@R2
M=D


// finish with infinite loop
(END)
@END
0;JEQ