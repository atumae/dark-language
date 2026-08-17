    .intel_syntax noprefix
    .globl spit
    .globl exists
    .globl random
    .globl sleep

spit:
    push rbp
    mov rbp, rsp
    push rbx
    mov rax, [rbp + 16]
    sub rax, 1
    lea rdi, [rax + 16]
    mov rsi, 577
    mov rdx, 420
    mov rax, 2
    syscall
    test rax, rax
    js 1f
    mov rbx, rax
    mov rax, [rbp + 24]
    sub rax, 1
    lea rsi, [rax + 16]
    mov rdx, [rax + 8]
    mov rdi, rbx
    mov rax, 1
    syscall
    mov rdi, rbx
    mov rax, 3
    syscall
    mov rax, 2
    pop rbx
    pop rbp
    ret
1:
    mov rax, 0
    pop rbx
    pop rbp
    ret

exists:
    push rbp
    mov rbp, rsp
    mov rax, [rbp + 16]
    sub rax, 1
    lea rdi, [rax + 16]
    mov rax, 2
    xor rsi, rsi
    xor rdx, rdx
    syscall
    test rax, rax
    js 1f
    mov rdi, rax
    mov rax, 3
    syscall
    mov rax, 2
    leave
    ret
1:
    mov rax, 0
    leave
    ret

random:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rdi, rsp
    mov rsi, 8
    xor rdx, rdx
    mov rax, 318
    syscall
    mov rax, [rsp]
    shr rax, 2
    shl rax, 1
    leave
    ret

sleep:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rax, [rbp + 16]
    sar rax, 1
    mov rcx, 1000
    cqo
    idiv rcx
    mov [rsp], rax
    imul rdx, rdx, 1000000
    mov [rsp + 8], rdx
    mov rdi, rsp
    xor rsi, rsi
    mov rax, 35
    syscall
    xor eax, eax
    leave
    ret
