    .intel_syntax noprefix
    .globl spit
    .globl exists
    .globl random
    .globl sleep

spit:
    push rbp
    mov rbp, rsp
    sub rsp, 96
    push rbx
    mov rax, [rbp + 16]
    sub rax, 1
    mov [rbp - 8], rax
    mov rax, [rbp + 24]
    sub rax, 1
    mov [rbp - 16], rax
    mov rax, [rbp - 8]
    lea rcx, [rax + 16]
    mov rdx, 0x40000000
    xor r8, r8
    xor r9, r9
    mov qword ptr [rsp + 32], 2
    mov qword ptr [rsp + 40], 0x80
    mov qword ptr [rsp + 48], 0
    call QWORD PTR [rip + CreateFileA]
    cmp rax, -1
    je 1f
    mov rbx, rax
    mov rax, [rbp - 16]
    lea rdx, [rax + 16]
    mov r8, [rax + 8]
    mov rcx, rbx
    lea r9, [rsp + 56]
    mov qword ptr [rsp + 32], 0
    call QWORD PTR [rip + WriteFile]
    mov rcx, rbx
    call QWORD PTR [rip + CloseHandle]
    mov rax, 2
    pop rbx
    leave
    ret
1:
    mov rax, 0
    pop rbx
    leave
    ret

exists:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov rax, [rbp + 16]
    sub rax, 1
    lea rcx, [rax + 16]
    mov rdx, 0x80000000
    xor r8, r8
    xor r9, r9
    mov qword ptr [rsp + 32], 3
    mov qword ptr [rsp + 40], 0x80
    mov qword ptr [rsp + 48], 0
    call QWORD PTR [rip + CreateFileA]
    cmp rax, -1
    je 1f
    mov rcx, rax
    call QWORD PTR [rip + CloseHandle]
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
    rdtsc
    shl rdx, 32
    or rax, rdx
    shr rax, 2
    shl rax, 1
    leave
    ret

sleep:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp + 16]
    sar rax, 1
    mov rcx, rax
    mov qword ptr [rsp + 32], 0
    call QWORD PTR [rip + Sleep]
    xor eax, eax
    leave
    ret
