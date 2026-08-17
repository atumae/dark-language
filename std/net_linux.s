    .intel_syntax noprefix
    .globl dns
    .globl tcp_connect
    .globl tcp_send
    .globl tcp_recv
    .globl tcp_close

skip_name:
    movzx eax, byte ptr [rdi]
    test eax, eax
    jz 2f
    cmp al, 0xC0
    jae 3f
    inc rdi
    add rdi, rax
    jmp skip_name
3:
    add rdi, 2
    ret
2:
    inc rdi
    ret

dns:
    push rbp
    mov rbp, rsp
    push rbx
    sub rsp, 1024
    mov rax, [rbp+16]
    sub rax, 1
    mov rcx, [rax+8]
    mov word ptr [rsp], 0x1234
    mov word ptr [rsp+2], 0x0001
    mov word ptr [rsp+4], 0x0100
    mov word ptr [rsp+6], 0
    mov word ptr [rsp+8], 0
    mov word ptr [rsp+10], 0
    lea rsi, [rax+16]
    lea rdi, [rsp+12]
    mov r8, rdi
    inc rdi
    xor rdx, rdx
    xor r9, r9
1:
    cmp r9, rcx
    jge 3f
    mov al, [rsi+r9]
    cmp al, 0x2e
    je 2f
    mov [rdi], al
    inc rdi
    inc rdx
    inc r9
    jmp 1b
2:
    mov [r8], dl
    mov r8, rdi
    inc rdi
    xor rdx, rdx
    inc r9
    jmp 1b
3:
    mov [r8], dl
    mov byte ptr [rdi], 0
    inc rdi
    mov word ptr [rdi], 0x0100
    mov word ptr [rdi+2], 0x0100
    add rdi, 4
    mov r10, rdi
    sub r10, rsp
    mov rax, 41
    mov rdi, 2
    mov rsi, 2
    xor rdx, rdx
    syscall
    test rax, rax
    js 9f
    mov rbx, rax
    lea r11, [rsp+800]
    mov word ptr [r11], 2
    mov word ptr [r11+2], 0x3500
    mov byte ptr [r11+4], 8
    mov byte ptr [r11+5], 8
    mov byte ptr [r11+6], 8
    mov byte ptr [r11+7], 8
    mov qword ptr [r11+8], 0
    mov rax, 44
    mov rdi, rbx
    mov rsi, rsp
    mov rdx, r10
    xor r10, r10
    mov r8, r11
    mov r9, 16
    syscall
    test rax, rax
    js 8f
    mov rax, 45
    mov rdi, rbx
    lea rsi, [rsp+128]
    mov rdx, 512
    xor r10, r10
    lea r8, [rsp+900]
    lea r9, [rsp+916]
    mov qword ptr [r9], 16
    syscall
    test rax, rax
    js 8f
    mov rax, 3
    mov rdi, rbx
    syscall
    lea rdi, [rsp+128+12]
    call skip_name
    add rdi, 4
    call skip_name
    add rdi, 10
    movzx eax, byte ptr [rdi]
    movzx ecx, byte ptr [rdi+1]
    movzx edx, byte ptr [rdi+2]
    movzx esi, byte ptr [rdi+3]
    shl eax, 24
    shl ecx, 16
    shl edx, 8
    or eax, ecx
    or eax, edx
    or eax, esi
    shl rax, 1
    add rsp, 1024
    pop rbx
    pop rbp
    ret
8:
    mov rax, 3
    mov rdi, rbx
    syscall
9:
    xor eax, eax
    add rsp, 1024
    pop rbx
    pop rbp
    ret

tcp_connect:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    sub rsp, 32
    mov rax, [rbp+16]
    sar rax, 1
    mov r12d, eax
    bswap r12d
    mov rax, [rbp+24]
    sar rax, 1
    mov r13d, eax
    mov rax, 41
    mov rdi, 2
    mov rsi, 1
    xor rdx, rdx
    syscall
    test rax, rax
    js 1f
    mov r14, rax
    
    # Set SO_RCVTIMEO (20 seconds)
    mov rax, 54
    mov rdi, r14
    mov rsi, 1
    mov rdx, 20
    mov r10, 20
    mov r8, 0
    mov qword ptr [rsp+16], 20
    mov qword ptr [rsp+24], 0
    lea r9, [rsp]
    mov rdx, 1
    syscall
    
    # Set SO_SNDTIMEO (20 seconds)
    mov rax, 54
    mov rdi, r14
    mov rsi, 1
    mov rdx, 21
    mov r10, 20
    mov r8, 0
    mov qword ptr [rsp+16], 20
    mov qword ptr [rsp+24], 0
    lea r9, [rsp]
    mov rdx, 1
    syscall
    
    mov word ptr [rsp], 2
    mov ax, r13w
    xchg al, ah
    mov word ptr [rsp+2], ax
    mov dword ptr [rsp+4], r12d
    mov qword ptr [rsp+8], 0
    mov rax, 42
    mov rdi, r14
    mov rsi, rsp
    mov rdx, 16
    syscall
    test rax, rax
    js 2f
    mov rax, r14
    shl rax, 1
    add rsp, 32
    pop r14
    pop r13
    pop r12
    pop rbp
    ret
2:
    mov rax, 3
    mov rdi, r14
    syscall
1:
    mov rax, -2
    add rsp, 32
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

tcp_send:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    sar rax, 1
    mov rdi, rax
    mov rax, [rbp+24]
    sub rax, 1
    lea rsi, [rax+16]
    mov rdx, [rax+8]
    mov rax, 1
    syscall
    shl rax, 1
    leave
    ret

tcp_recv:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push rbx
    sub rsp, 32
    mov rax, [rbp+16]
    sar rax, 1
    mov r12, rax
    mov rax, [rbp+24]
    sar rax, 1
    mov r13, rax
    lea rax, [r13+17]
    push rax
    call alloc_placeholder
    add rsp, 8
    mov r14, rax
    mov rax, 0
    mov rdi, r12
    lea rsi, [r14+16]
    mov rdx, r13
    syscall
    test rax, rax
    js 1f
    mov qword ptr [r14], 0
    mov [r14+8], rax
    mov rbx, rax
    mov byte ptr [r14+rbx+16], 0
    mov rax, r14
    or rax, 1
    add rsp, 32
    pop rbx
    pop r14
    pop r13
    pop r12
    pop rbp
    ret
1:
    mov qword ptr [r14], 0
    mov qword ptr [r14+8], 0
    mov byte ptr [r14+16], 0
    mov rax, r14
    or rax, 1
    add rsp, 32
    pop rbx
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

tcp_close:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    sar rax, 1
    mov rdi, rax
    mov rax, 3
    syscall
    xor eax, eax
    leave
    ret
