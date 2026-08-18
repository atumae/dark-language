#!/usr/bin/env python3
import subprocess, tempfile, os, re, sys

ASM = {}

# ============================= LINUX =============================

ASM["linux"] = {
"trim": """
trim:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    mov r12, [rbp+16]
    sub r12, 1
    mov r13, [r12+8]
    xor r14, r14
.start_loop:
    cmp r14, r13
    jge .start_done
    movzx eax, byte [r12+r14+16]
    cmp al, 32
    je .skip_start
    cmp al, 9
    je .skip_start
    cmp al, 10
    je .skip_start
    cmp al, 13
    je .skip_start
    jmp .start_done
.skip_start:
    inc r14
    jmp .start_loop
.start_done:
    mov r15, r13
.end_loop:
    cmp r15, r14
    jle .end_done
    movzx eax, byte [r12+r15+15]
    cmp al, 32
    je .skip_end
    cmp al, 9
    je .skip_end
    cmp al, 10
    je .skip_end
    cmp al, 13
    je .skip_end
    jmp .end_done
.skip_end:
    dec r15
    jmp .end_loop
.end_done:
    sub r15, r14
    mov rax, r15
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r15
    lea rdi, [rax+16]
    lea rsi, [r12+r14+16]
    mov rcx, r15
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    pop r15
    pop r14
    pop r13
    pop r12
    leave
    ret
""",
"stop": """
stop:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    shr rax, 1
    mov rdi, rax
    mov rax, 60
    syscall
""",
"syscall": """
syscall:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    shr rax, 1
    mov rdi, [rbp+24]
    shr rdi, 1
    mov rsi, [rbp+32]
    shr rsi, 1
    mov rdx, [rbp+40]
    shr rdx, 1
    mov r10, [rbp+48]
    shr r10, 1
    mov r8, [rbp+56]
    shr r8, 1
    mov r9, [rbp+64]
    shr r9, 1
    syscall
    shl rax, 1
    leave
    ret
""",
"time_now": """
time_now:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rdi, rsp
    xor esi, esi
    mov rax, 96
    syscall
    mov rax, [rsp]
    imul rax, rax, 1000
    mov rdx, [rsp+8]
    add rax, rdx
    add rax, 500
    mov rcx, 1000
    xor edx, edx
    div rcx
    shl rax, 1
    leave
    ret
""",
"mkdir": """
mkdir:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    sub rax, 1
    lea rdi, [rax+16]
    mov rsi, 493
    mov rax, 83
    syscall
    test rax, rax
    sete al
    movzx eax, al
    shl rax, 1
    leave
    ret
""",
"remove": """
remove:
    push rbp
    mov rbp, rsp
    mov rax, [rbp+16]
    sub rax, 1
    lea rdi, [rax+16]
    mov rax, 87
    syscall
    test rax, rax
    sete al
    movzx eax, al
    shl rax, 1
    leave
    ret
""",
"file_size": """
file_size:
    push rbp
    mov rbp, rsp
    push rbx
    sub rsp, 200
    mov rax, [rbp+16]
    sub rax, 1
    lea rdi, [rax+16]
    xor esi, esi
    xor edx, edx
    mov rax, 2
    syscall
    test rax, rax
    js .fail
    mov rbx, rax
    mov rdi, rbx
    mov rsi, rsp
    mov rax, 5
    syscall
    mov rdi, rbx
    mov rax, 3
    syscall
    mov rax, [rsp+48]
    shl rax, 1
    add rsp, 200
    pop rbx
    leave
    ret
.fail:
    mov rax, -2
    add rsp, 200
    pop rbx
    leave
    ret
""",
"listdir": """
listdir:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 24
    mov rax, [rbp+16]
    sub rax, 1
    lea rdi, [rax+16]
    mov rsi, 65536
    xor edx, edx
    mov rax, 2
    syscall
    test rax, rax
    js .fail
    mov r15, rax
    push 65536
    call __alloc
    add rsp, 8
    mov r14, rax
    push 8192
    call __make_array
    add rsp, 8
    sub rax, 1
    mov r13, rax
    xor r12, r12
.read:
    mov rdi, r15
    mov rsi, r14
    mov rdx, 65536
    mov rax, 217
    syscall
    test rax, rax
    jle .done
    mov r9, rax
    mov rbx, r14
.loop:
    mov r10, rbx
    add r10, 19
    xor r8, r8
.nlen:
    cmp byte [r10+r8], 0
    je .nlen_done
    inc r8
    jmp .nlen
.nlen_done:
    mov al, [r10]
    cmp al, 46
    jne .add
    cmp r8, 1
    je .next
    cmp r8, 2
    jne .add
    cmp byte [r10+1], 46
    je .next
.add:
    mov rax, r8
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r8
    lea rdi, [rax+16]
    mov rsi, r10
    mov rcx, r8
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    mov [r13 + r12*8 + 24], rax
    inc r12
.next:
    movzx eax, word [rbx+16]
    add rbx, rax
    lea rax, [r14+r9]
    cmp rbx, rax
    jl .loop
    jmp .read
.done:
    mov rdi, r15
    mov rax, 3
    syscall
    mov [r13+8], r12
    mov rax, r13
    or rax, 1
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    leave
    ret
.fail:
    push 0
    call __make_array
    add rsp, 8
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    leave
    ret
""",
"system": """
system:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r14
    sub rsp, 128
    lea rdi, [rsp+8]
    xor esi, esi
    mov rax, 22
    syscall
    test rax, rax
    js .fail
    mov rax, 57
    syscall
    test rax, rax
    jz .child
    mov r14, rax
    mov edi, [rsp+12]
    mov rax, 3
    syscall
    push 65536
    call __alloc
    add rsp, 8
    mov rbx, rax
    xor r12, r12
.read_loop:
    lea rsi, [rbx+r12]
    mov rdx, 65536
    sub rdx, r12
    test rdx, rdx
    jz .read_done
    mov edi, [rsp+8]
    mov rax, 0
    syscall
    test rax, rax
    jle .read_done
    add r12, rax
    cmp r12, 65536
    jl .read_loop
.read_done:
    mov edi, [rsp+8]
    mov rax, 3
    syscall
    mov rdi, r14
    xor esi, esi
    xor edx, edx
    xor r10d, r10d
    mov rax, 61
    syscall
    mov rax, r12
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r12
    lea rdi, [rax+16]
    mov rsi, rbx
    mov rcx, r12
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    add rsp, 128
    pop r14
    pop r12
    pop rbx
    leave
    ret
.child:
    mov edi, [rsp+8]
    mov rax, 3
    syscall
    mov edi, [rsp+12]
    mov esi, 1
    mov rax, 33
    syscall
    mov edi, [rsp+12]
    mov esi, 2
    mov rax, 33
    syscall
    mov edi, [rsp+12]
    mov rax, 3
    syscall
    movabs rax, 0x0068732f6e69622f
    mov [rsp+32], rax
    movabs rax, 0x00632d
    mov [rsp+40], rax
    lea rax, [rsp+32]
    mov [rsp+72], rax
    lea rax, [rsp+40]
    mov [rsp+80], rax
    mov rax, [rbp+16]
    sub rax, 1
    lea rax, [rax+16]
    mov [rsp+88], rax
    mov qword [rsp+96], 0
    mov rdi, [rsp+72]
    lea rsi, [rsp+72]
    xor rdx, rdx
    mov rax, 59
    syscall
    mov rdi, 127
    mov rax, 60
    syscall
.fail:
    push 17
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], 0
    lea rdi, [rax+16]
    mov byte [rdi], 0
    or rax, 1
    add rsp, 128
    pop r14
    pop r12
    pop rbx
    leave
    ret
""",
"env": """
env:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    mov r14, [rbp+16]
    sub r14, 1
    mov r13, [r14+8]
    movabs rbx, 0x0011223344556699
    xor rdi, rdi
.bufcmp:
    cmp rdi, r13
    jge .bufend
    mov al, [rbx+rdi]
    mov r9b, [r14+rdi+16]
    cmp al, r9b
    jne .envscan
    inc rdi
    jmp .bufcmp
.bufend:
    mov al, [rbx+rdi]
    cmp al, 61
    jne .envscan
    lea rsi, [rbx+rdi+1]
    xor r12, r12
.bufvlen:
    cmp byte [rsi+r12], 0
    je .build
    inc r12
    jmp .bufvlen
.envscan:
    movabs rbx, 0x0011223344556677
    mov rbx, [rbx]
    movabs rcx, 0x0011223344556688
    mov rcx, [rcx]
    lea rbx, [rcx + rbx*8 + 8]
.entry_loop:
    mov rdx, [rbx]
    test rdx, rdx
    jz .notfound
    add rbx, 8
    xor rdi, rdi
.compare:
    cmp rdi, r13
    jge .check_end
    mov al, [rdx+rdi]
    cmp al, 61
    je .next_entry
    mov r9b, [r14+rdi+16]
    cmp al, r9b
    jne .next_entry
    inc rdi
    jmp .compare
.check_end:
    mov al, [rdx+rdi]
    cmp al, 61
    jne .next_entry
    lea rsi, [rdx+rdi+1]
    xor r12, r12
.vlen:
    cmp byte [rsi+r12], 0
    je .build
    inc r12
    jmp .vlen
.notfound:
    xor r12, r12
    xor rsi, rsi
.build:
    mov rax, r12
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r12
    lea rdi, [rax+16]
    test rsi, rsi
    jz .nul
    mov rcx, r12
    rep movsb
.nul:
    mov byte [rdi], 0
    or rax, 1
    pop r14
    pop r13
    pop r12
    pop rbx
    leave
    ret
.next_entry:
    jmp .entry_loop
""",
"setenv": """
setenv:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    mov r12, [rbp+16]
    sub r12, 1
    mov r13, [r12+8]
    mov r14, [rbp+24]
    sub r14, 1
    mov rbx, [r14+8]
    movabs rdi, 0x0011223344556699
    lea rsi, [r12+16]
    mov rcx, r13
    rep movsb
    mov byte [rdi], 61
    inc rdi
    lea rsi, [r14+16]
    mov rcx, rbx
    rep movsb
    mov byte [rdi], 0
    mov rax, 2
    pop r14
    pop r13
    pop r12
    pop rbx
    leave
    ret
""",
}

# ============================= WINDOWS =============================

ASM["win"] = {
"trim": """
trim:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    mov r12, [rbp+16]
    sub r12, 1
    mov r13, [r12+8]
    xor r14, r14
.start_loop:
    cmp r14, r13
    jge .start_done
    movzx eax, byte [r12+r14+16]
    cmp al, 32
    je .skip_start
    cmp al, 9
    je .skip_start
    cmp al, 10
    je .skip_start
    cmp al, 13
    je .skip_start
    jmp .start_done
.skip_start:
    inc r14
    jmp .start_loop
.start_done:
    mov r15, r13
.end_loop:
    cmp r15, r14
    jle .end_done
    movzx eax, byte [r12+r15+15]
    cmp al, 32
    je .skip_end
    cmp al, 9
    je .skip_end
    cmp al, 10
    je .skip_end
    cmp al, 13
    je .skip_end
    jmp .end_done
.skip_end:
    dec r15
    jmp .end_loop
.end_done:
    sub r15, r14
    mov rax, r15
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r15
    lea rdi, [rax+16]
    lea rsi, [r12+r14+16]
    mov rcx, r15
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    pop r15
    pop r14
    pop r13
    pop r12
    leave
    ret
""",
"stop": """
stop:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rcx, [rbp+16]
    shr rcx, 1
    @win ExitProcess
""",
"syscall": """
syscall:
    xor eax, eax
    ret
""",
"time_now": """
time_now:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    lea rcx, [rsp+32]
    @win GetSystemTimeAsFileTime
    mov rax, [rsp+32]
    mov rcx, 10000
    xor edx, edx
    div rcx
    mov rcx, 11644473600000
    sub rax, rcx
    shl rax, 1
    leave
    ret
""",
"mkdir": """
mkdir:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp+16]
    sub rax, 1
    lea rcx, [rax+16]
    xor rdx, rdx
    @win CreateDirectoryA
    test rax, rax
    sete al
    movzx eax, al
    shl rax, 1
    leave
    ret
""",
"remove": """
remove:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp+16]
    sub rax, 1
    lea rcx, [rax+16]
    @win DeleteFileA
    test rax, rax
    sete al
    movzx eax, al
    shl rax, 1
    leave
    ret
""",
"file_size": """
file_size:
    push rbp
    mov rbp, rsp
    sub rsp, 96
    mov rax, [rbp+16]
    sub rax, 1
    lea rcx, [rax+16]
    xor edx, edx
    lea r8, [rsp+32]
    @win GetFileAttributesExA
    test rax, rax
    jz .fail
    mov eax, [rsp+64]
    mov edx, [rsp+60]
    shl rdx, 32
    or rax, rdx
    shl rax, 1
    leave
    ret
.fail:
    mov rax, -2
    leave
    ret
""",
"listdir": """
listdir:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 656
    and rsp, -16
    mov r14, [rbp+16]
    sub r14, 1
    mov r15, [r14+8]
    mov rax, r15
    add rax, 19
    push rax
    call __alloc
    add rsp, 8
    mov r13, rax
    lea rdi, [r13+16]
    lea rsi, [r14+16]
    mov rcx, r15
    rep movsb
    lea rdi, [r13+16]
    add rdi, r15
    movabs rax, 0x0000000000002a5c
    mov [rdi], rax
    lea rcx, [r13+16]
    lea rdx, [rsp+32]
    @win FindFirstFileA
    cmp rax, -1
    je .empty
    mov r14, rax
    push 8192
    call __make_array
    add rsp, 8
    sub rax, 1
    mov r12, rax
    xor r15, r15
.collect:
    lea rbx, [rsp+76]
    mov al, [rbx]
    cmp al, 46
    jne .addname
    cmp byte [rbx+1], 0
    je .nextfile
    cmp byte [rbx+1], 46
    jne .addname
    cmp byte [rbx+2], 0
    je .nextfile
.addname:
    xor r8, r8
.strlen:
    cmp byte [rbx+r8], 0
    je .strlen_done
    inc r8
    jmp .strlen
.strlen_done:
    mov rax, r8
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r8
    lea rdi, [rax+16]
    mov rsi, rbx
    mov rcx, r8
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    mov [r12 + r15*8 + 24], rax
    inc r15
.nextfile:
    mov rcx, r14
    lea rdx, [rsp+32]
    @win FindNextFileA
    test rax, rax
    jnz .collect
.done:
    mov rcx, r14
    @win FindClose
    mov [r12+8], r15
    mov rax, r12
    or rax, 1
    lea rsp, [rbp-40]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
.empty:
    push 0
    call __make_array
    add rsp, 8
    lea rsp, [rbp-40]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
""",
"system": """
system:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 248
    and rsp, -16
    mov r12, [rbp+16]
    sub r12, 1
    mov rbx, [r12+8]
    lea r13, [r12+16]
    mov rax, rbx
    add rax, 7
    add rax, 23
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov r14, rax
    lea rdi, [r14+16]
    lea rsi, [rel .prefix]
    mov rcx, 7
    rep movsb
    mov rsi, r13
    mov rcx, rbx
    rep movsb
    lea rsi, [rel .suffix]
    mov rcx, 23
    rep movsb
    mov byte [rdi], 0
    lea rdi, [rsp+96]
    xor eax, eax
    mov ecx, 13
    rep stosq
    mov dword [rsp+96], 104
    xor ecx, ecx
    mov rdx, r14
    add rdx, 16
    xor r8d, r8d
    xor r9d, r9d
    mov qword [rsp+32], 0
    mov qword [rsp+40], 0
    mov qword [rsp+48], 0
    mov qword [rsp+56], 0
    lea rax, [rsp+96]
    mov qword [rsp+64], rax
    lea rax, [rsp+200]
    mov qword [rsp+72], rax
    @win CreateProcessA
    test rax, rax
    jz .fail
    mov rcx, [rsp+208]
    @win CloseHandle
    mov rcx, [rsp+200]
    mov rdx, -1
    @win WaitForSingleObject
    mov rcx, [rsp+200]
    @win CloseHandle
    push 32
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], 15
    lea rdi, [rax+16]
    lea rsi, [rel .tmpfile]
    mov rcx, 15
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    push rax
    call slurp
    add rsp, 8
    mov r15, rax
    push 32
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], 15
    lea rdi, [rax+16]
    lea rsi, [rel .tmpfile]
    mov rcx, 15
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    push rax
    call remove
    add rsp, 8
    mov rax, r15
    lea rsp, [rbp-40]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
.fail:
    push 17
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], 0
    lea rdi, [rax+16]
    mov byte [rdi], 0
    or rax, 1
    lea rsp, [rbp-40]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
.prefix:
    db "cmd /c "
.suffix:
    db " > .__dark_tmp.txt 2>&1"
.tmpfile:
    db ".__dark_tmp.txt"
""",
"env": """
env:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    sub rsp, 40
    mov r12, [rbp+16]
    sub r12, 1
    lea rcx, [r12+16]
    xor edx, edx
    xor r8d, r8d
    @win GetEnvironmentVariableA
    test eax, eax
    jz .notfound
    mov r13d, eax
    mov rax, r13
    add rax, 2
    push rax
    call __alloc
    add rsp, 8
    mov r14, rax
    lea rcx, [r12+16]
    mov rdx, r14
    mov r8d, r13d
    add r8d, 1
    @win GetEnvironmentVariableA
    mov r13d, eax
    mov rax, r13
    add rax, 17
    push rax
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], r13
    lea rdi, [rax+16]
    mov rsi, r14
    mov rcx, r13
    rep movsb
    mov byte [rdi], 0
    or rax, 1
    pop r14
    pop r13
    pop r12
    add rsp, 40
    leave
    ret
.notfound:
    push 17
    call __alloc
    add rsp, 8
    mov qword [rax], 0
    mov [rax+8], 0
    lea rdi, [rax+16]
    mov byte [rdi], 0
    or rax, 1
    pop r14
    pop r13
    pop r12
    add rsp, 40
    leave
    ret
""",
"setenv": """
setenv:
    push rbp
    mov rbp, rsp
    sub rsp, 40
    mov rax, [rbp+16]
    sub rax, 1
    lea rcx, [rax+16]
    mov rax, [rbp+24]
    sub rax, 1
    lea rdx, [rax+16]
    @win SetEnvironmentVariableA
    test rax, rax
    sete al
    movzx eax, al
    shl rax, 1
    leave
    ret
""",
}

FIX_IMM = {
    "argc": 0x0011223344556677,
    "argv": 0x0011223344556688,
    "setenv": 0x0011223344556699,
}
FIX_REG = {
    "argc": "rbx",
    "argv": "rcx",
    "setenv": "rdi",
}

WINFN = {
    "SetEnvironmentVariableA": 30,
    "ExitProcess": 2,
    "GetSystemTimeAsFileTime": 28,
    "GetEnvironmentVariableA": 27,
    "CreateDirectoryA": 21,
    "DeleteFileA": 22,
    "GetFileAttributesExA": 23,
    "FindFirstFileA": 24,
    "FindNextFileA": 25,
    "FindClose": 26,
    "CreateProcessA": 20,
    "CloseHandle": 7,
    "WaitForSingleObject": 29,
    "GetStdHandle": 0,
    "WriteConsoleA": 1,
    "VirtualAlloc": 3,
    "CreateFileA": 4,
    "ReadFile": 5,
    "WriteFile": 6,
    "GetCommandLineA": 8,
    "Sleep": 17,
    "WinExec": 18,
    "WSAStartup": 9,
    "socket": 10,
    "connect": 11,
    "send": 12,
    "recv": 13,
    "closesocket": 14,
    "sendto": 15,
    "recvfrom": 16,
}

def stub_labels(text):
    own = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*):", text, re.M))
    out = []
    for lab in ["__alloc", "__make_array", "slurp", "remove"]:
        if lab in own:
            continue
        out.append(f"{lab}:\n    ret\n")
    return "".join(out)

def win_preprocess(text):
    lines = []
    wins = []
    for line in text.split("\n"):
        t = line.strip()
        if t.startswith("@win"):
            wins.append(t.split()[1])
            lines.append("    call qword [rel .win_%d]" % (len(wins) - 1))
        else:
            lines.append(line)
    for i in range(len(wins)):
        lines.append(".win_%d: dq 0" % i)
    return "\n".join(lines) + "\n", wins

def assemble_src(text):
    text, wins = win_preprocess(text)
    src = "BITS 64\n" + text + stub_labels(text)
    return src, wins

def asm_bin(src):
    with open("/tmp/rtg.s", "w") as f:
        f.write(src)
    subprocess.run(["nasm", "-f", "bin", "-o", "/tmp/rtg.bin", "/tmp/rtg.s"], check=True)
    with open("/tmp/rtg.bin", "rb") as f:
        return f.read()

def asm_listing(src):
    with open("/tmp/rtg.s", "w") as f:
        f.write(src)
    subprocess.run(["nasm", "-f", "elf64", "-l", "/tmp/rtg.lst", "-o", "/tmp/rtg.o", "/tmp/rtg.s"], check=True)
    with open("/tmp/rtg.lst") as f:
        return f.read()

def parse_listing(listing, limit):
    insns = []
    for ln in listing.split("\n"):
        m = re.match(r"^\s*\d+\s+([0-9A-Fa-f]{8})\s+[0-9A-Fa-f-]*\s*(.*)$", ln)
        if not m:
            continue
        if not m.group(2).strip():
            continue
        off = int(m.group(1), 16)
        if off >= limit:
            continue
        insns.append([off, m.group(2)])
    return insns

def build(name, src, win):
    src2, winlist = win_preprocess(src)
    stubs = stub_labels(src2)
    full = "BITS 64\n" + src2 + stubs
    b = asm_bin(full)
    stubs_kept = len(re.findall(r"^(__alloc|__make_array|slurp|remove):", stubs, re.M))
    total = len(b) - 8 * len(winlist) - stubs_kept
    insns = parse_listing(asm_listing(full), total)
    win_ids = [WINFN[t] for t in winlist]
    items = []
    i = 0
    while i < len(insns):
        off, source = insns[i]
        s = source.strip()
        end = insns[i + 1][0] if i + 1 < len(insns) else total
        bts = list(b[off:end])
        fixname = None
        m = re.search(r"movabs\s+\w+,\s*0x([0-9a-fA-F]+)", s)
        if m:
            imm = int(m.group(1), 16)
            for fname, fimm in FIX_IMM.items():
                if imm == fimm:
                    fixname = fname
                    break
        if fixname is not None:
            items.append(["fix_" + fixname, bts[1]])
            i += 1
        elif s.startswith("call qword [rel .win"):
            items.append(["win", win_ids.pop(0)])
            i += 1
        elif s.startswith("call") and len(s.split()) >= 2 and s.split()[1] in ("__alloc", "__make_array", "slurp", "remove"):
            target = s.split()[1]
            items.append(["call_" + target, None])
            i += 1
            if i < len(insns) and "add rsp" in insns[i][1]:
                i += 1
        else:
            items.append(["bytes", bts])
            i += 1
    merged = []
    for kind, data in items:
        if kind == "bytes" and merged and merged[-1][0] == "bytes":
            merged[-1][1].extend(data)
        else:
            merged.append([kind, data])
    return total, merged

def fmt(bs):
    return "[" + ", ".join(str(x) for x in bs) + "]"

def emit_dark(name, items):
    out = []
    first = True
    for kind, data in items:
        if kind == "bytes":
            if first:
                out.append("    gen_rt_fn(ctx, \"%s\", %s)" % (name, fmt(data)))
                first = False
            else:
                out.append("    emitc(ctx, %s)" % fmt(data))
        elif kind == "win":
            out.append("    gen_win_call(ctx, %d)" % data)
        elif kind.startswith("call_"):
            fname = kind[5:]
            out.append("    gen_call_runtime(ctx, \"%s\", 1)" % fname)
        elif kind.startswith("fix_"):
            fname = kind[4:]
            out.append("    emitc(ctx, [72, %d])" % data)
            out.append("    emitc(ctx, zeros(8))")
            out.append("    p = size(ctx[\"code\"]) - 8")
            out.append("    ctx[\"fix\"] = push(ctx[\"fix\"], [p, \"%s\", 0])" % fname)
        else:
            out.append("    // ?? " + kind)
    return "\n".join(out)

if __name__ == "__main__":
    import json
    results = {}
    for name in ["stop", "syscall", "time_now", "mkdir", "remove", "file_size", "listdir", "system", "env", "setenv"]:
        total, items = build(name, ASM["linux"][name], False)
        results[name] = {"total": total, "items": [[k, d] for k, d in items]}
        total, items = build(name, ASM["win"][name], True)
        results["win_" + name] = {"total": total, "items": [[k, d] for k, d in items]}
    with open("/tmp/rtgen_out.json", "w") as f:
        json.dump(results, f)
    for name in ["stop", "syscall", "time_now", "mkdir", "remove", "file_size", "listdir", "system", "env", "setenv"]:
        for tag, key in [("LINUX", name), ("WINDOWS", "win_" + name)]:
            v = results[key]
            print("// ===== %s %s (total=%d) =====" % (name, tag, v["total"]))
            print(emit_dark(name, v["items"]))
            print()
