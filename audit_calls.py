import re, os

std = "/home/dark/projects/dark-language/std"
keywords = set("""if else while for give emit exit_code skip break continue return fn extract
and or not null true false stop do in""".split())

rt = set("""__add __alloc __cmp __emit_str __get __make_array __obj_new __set __str_concat
args char_at chr dns env exec exists keys kind make_exe ord os push random size sleep slurp
spit stop substring syscall system tcp_close tcp_connect tcp_recv tcp_send to_int to_string trim values
gcm_open_d gcm_seal_d hkdf_d hmac_d sha256_d x25519_d""".split())

defs = {}   # name -> file
for f in sorted(os.listdir(std)):
    if not f.endswith(".dark"):
        continue
    src = open(os.path.join(std, f)).read()
    for m in re.finditer(r"fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", src):
        defs[m.group(1)] = f

for f in sorted(os.listdir(std)):
    if not f.endswith(".dark") or f in ("parser.dark", "codegen.dark", "native.dark"):
        continue
    src = open(os.path.join(std, f)).read()
    src = re.sub(r'"(\\.|[^"\\])*"', '""', src)      # strip strings
    calls = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", src))
    unknown = sorted(c for c in calls
                     if c not in keywords
                     and c not in rt
                     and c not in defs)
    if unknown:
        print("%-18s UNDEFINED CALLS: %s" % (f, ", ".join(unknown)))
    else:
        print("%-18s ok" % f)
