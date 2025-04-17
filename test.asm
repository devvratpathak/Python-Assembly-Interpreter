; =============================================
; Assembly Program with Clean Output Formatting
; =============================================

; Initialize registers
mov a, 10
mov b, 20
mov c, 0
mov d, 100
mov counter, 5

; Basic arithmetic operations
add_ops:
    add a, 5
    sub b, 3
    mul c, 4
    div d, 2
    inc a
    dec b

; Comparison section
compare_section:
    cmp a, b
    je equal
    msg 'This should not print'
    jmp end_comparison

equal:
    msg 'Values are equal (16 and 16)', '\n'

end_comparison:
    cmp counter, 0
    jg loop_section

; Loop demonstration with clean output
loop_section:
    msg 'Counter: ', counter
    dec counter
    cmp counter, 0
    jg loop_section

msg ''  ; Add extra line break

; Function call
main:
    mov x, 2
    mov y, 3
    call multiply
    msg 'Result of 2 * 3: ', z, '\n'
    jmp memory_ops

; Multiply function
multiply:
    mov z, x
    mul z, y
    ret

; Memory operations
memory_ops:
    stw a, 1000
    mvw temp, 1000
    msg 'Memory value: ', temp, '\n'

; Conditional jumps section
conditional_demo:
    mov p, 15
    mov q, 20
    
    cmp p, q
    jl less
    jg greater
    je equal_msg
    
less:
    msg '15 is less than 20'
    jmp next_condition
    
greater:
    msg 'This should not print'
    jmp next_condition
    
equal_msg:
    msg 'This should not print'

next_condition:
    cmp p, q
    jle less_or_equal
    jge greater_or_equal
    
less_or_equal:
    msg '15 is less than or equal to 20', '\n'
    jmp final_output
    
greater_or_equal:
    msg 'This should not print'

; Final output section
final_output:
    msg '=== Program Results ==='
    msg 'Register a: ', a
    msg 'Register b: ', b
    msg 'Register d: ', d
    msg 'Memory temp: ', temp
    msg 'Final counter: ', counter
    msg '========================'

end