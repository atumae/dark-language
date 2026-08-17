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
    sub rsp, 2048
    push rbx
    push rdi
    push rsi
    push r12

    mov rcx, 0x202
    lea rdx, [rsp + 48]
    call QWORD PTR [rip + WSAStartup]

    mov word ptr [rsp + 512], 0x1234
    mov word ptr [rsp + 514], 0x0001
    mov word ptr [rsp + 516], 0x0100
    mov word ptr [rsp + 518], 0
    mov word ptr [rsp + 520], 0
    mov word ptr [rsp + 522], 0
    mov rax, [rbp + 16]
    sub rax, 1
    mov rcx, [rax + 8]
    lea rsi, [rax + 16]
    lea rdi, [rsp + 524]
    mov r8, rdi
    inc rdi
    xor rdx, rdx
    xor r9, r9
1:
    cmp r9, rcx
    jge 4f
    mov al, [rsi + r9]
    cmp al, 0x2e
    je 5f
    mov [rdi], al
    inc rdi
    inc rdx
    inc r9
    jmp 1b
5:
    mov [r8], dl
    mov r8, rdi
    inc rdi
    xor rdx, rdx
    inc r9
    jmp 1b
4:
    mov [r8], dl
    mov byte ptr [rdi], 0
    inc rdi
    mov word ptr [rdi], 0x0100
    mov word ptr [rdi + 2], 0x0100
    add rdi, 4
    lea r12, [rsp + 512]
    mov rax, rdi
    sub rax, r12
    mov r12, rax

    mov rcx, 2
    mov rdx, 2
    mov r8, 17
    call QWORD PTR [rip + socket]
    mov rbx, rax

    lea r11, [rsp + 1536]
    mov word ptr [r11], 2
    mov word ptr [r11 + 2], 0x3500
    mov dword ptr [r11 + 4], 0x08080808
    mov qword ptr [r11 + 8], 0

    mov rcx, rbx
    lea rdx, [rsp + 512]
    mov r8, r12
    xor r9, r9
    lea rax, [rsp + 1536]
    mov [rsp + 32], rax
    mov qword ptr [rsp + 40], 16
    call QWORD PTR [rip + sendto]

    mov rcx, rbx
    lea rdx, [rsp + 1024]
    mov r8, 512
    xor r9, r9
    mov qword ptr [rsp + 32], 0
    mov qword ptr [rsp + 40], 0
    call QWORD PTR [rip + recvfrom]

    mov rcx, rbx
    call QWORD PTR [rip + closesocket]

    lea rdi, [rsp + 1024 + 12]
    call skip_name
    add rdi, 4
    call skip_name
    add rdi, 10
    movzx eax, byte ptr [rdi]
    movzx ecx, byte ptr [rdi + 1]
    movzx edx, byte ptr [rdi + 2]
    movzx esi, byte ptr [rdi + 3]
    shl eax, 24
    shl ecx, 16
    shl edx, 8
    or eax, ecx
    or eax, edx
    or eax, esi
    shl rax, 1

    add rsp, 2048
    pop r12
    pop rsi
    pop rdi
    pop rbx
    pop rbp
    ret

tcp_connect:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    sub rsp, 440

    mov rcx, 0x202
    lea rdx, [rsp + 32]
    call QWORD PTR [rip + WSAStartup]

    mov rax, [rbp + 16]
    sar rax, 1
    mov r12d, eax
    bswap r12d
    mov rax, [rbp + 24]
    sar rax, 1
    mov r13d, eax

    mov rcx, 2
    mov rdx, 1
    mov r8, 6
    call QWORD PTR [rip + socket]
    mov r14, rax

    mov word ptr [rsp + 32], 2
    mov ax, r13w
    xchg al, ah
    mov word ptr [rsp + 34], ax
    mov dword ptr [rsp + 36], r12d
    mov qword ptr [rsp + 40], 0

    mov rcx, r14
    lea rdx, [rsp + 32]
    mov r8, 16
    call QWORD PTR [rip + connect]

    test eax, eax
    js 6f
    mov rax, r14
    shl rax, 1
    add rsp, 440
    pop r14
    pop r13
    pop r12
    pop rbp
    ret
6:
    mov rcx, r14
    call QWORD PTR [rip + closesocket]
    mov rax, -2
    add rsp, 440
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

tcp_send:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp + 16]
    sar rax, 1
    mov rcx, rax
    mov rax, [rbp + 24]
    sub rax, 1
    lea rdx, [rax + 16]
    mov r8, [rax + 8]
    xor r9, r9
    mov qword ptr [rsp + 32], 0
    call QWORD PTR [rip + send]
    movsxd rax, eax
    shl rax, 1
    leave
    ret

tcp_recv:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    sub rsp, 48

    mov rax, [rbp + 16]
    sar rax, 1
    mov r12, rax
    mov rax, [rbp + 24]
    sar rax, 1
    mov r13, rax

    lea rax, [r13 + 17]
    push rax
    call alloc_placeholder
    add rsp, 8
    mov r14, rax

    mov rcx, r12
    lea rdx, [r14 + 16]
    mov r8, r13
    xor r9, r9
    mov qword ptr [rsp + 32], 0
    call QWORD PTR [rip + recv]

    movsxd rax, eax
    test rax, rax
    js 7f
    mov qword ptr [r14], 0
    mov [r14 + 8], rax
    mov byte ptr [r14 + rax + 16], 0
    mov rax, r14
    or rax, 1
    add rsp, 48
    pop r14
    pop r13
    pop r12
    pop rbp
    ret
7:
    mov qword ptr [r14], 0
    mov qword ptr [r14 + 8], 0
    mov byte ptr [r14 + 16], 0
    mov rax, r14
    or rax, 1
    add rsp, 48
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

tcp_close:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp + 16]
    sar rax, 1
    mov rcx, rax
    mov qword ptr [rsp + 32], 0
    call QWORD PTR [rip + closesocket]
    xor eax, eax
    leave
    ret
