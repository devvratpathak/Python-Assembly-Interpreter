; =============================================
; Simple Assembly Program for Demonstration
; =============================================

; Initialize registers
mov a, 10
mov b, 20
mov c, 0
mov d, 100
mov counter, 5

; Basic arithmetic operations
add a, 5
sub b, 3
mul c, 4
div d, 2
inc a
dec b

; Compare values
cmp a, 16
je equal_section
jmp not_equal_section

equal_section:
    msg 'Values are equal (16 and 16)'
    jmp end_comparison

not_equal_section:
    msg 'Values are not equal'

end_comparison:
    msg 'Comparison complete'

; Loop demonstration
msg 'Starting loop demonstration'
loop_start:
    msg 'Counter: ', counter
    dec counter
    cmp counter, 0
    jg loop_start
    msg 'Loop finished'

; Function call
mov x, 2
mov y, 3
call multiply_function
msg 'Result of 2 * 3: ', z

; Memory operations
stw a, 1000
mvw temp, 1000
msg 'Memory value: ', temp

; Final output
msg '=== Program Results ==='
msg 'Register a: ', a
msg 'Register b: ', b
msg 'Register d: ', d
msg 'Memory temp: ', temp
msg 'Final counter: ', counter
msg '========================'

jmp end_of_program

; Multiply function
multiply_function:
    mov z, x
    mul z, y
    ret

end_of_program:
end