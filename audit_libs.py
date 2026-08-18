import re, os, sys

std = "/home/dark/projects/dark-language/std"
codegen = os.path.join(std, "codegen.dark")

lib_fns = {}
for f in sorted(os.listdir(std)):
    if not f.endswith(".dark"):
        continue
    path = os.path.join(std, f)
    src = open(path).read()
    defs = re.findall(r"fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", src)
    lib_fns[f] = sorted(set(defs))
    if f != "codegen.dark" and f != "parser.dark" and f != "native.dark":
        print("%-22s %d fns: %s" % (f, len(defs), ", ".join(sorted(set(defs)))))

src = open(codegen).read()
rt = sorted(set(re.findall(r'gen_rt_fn\s*\(ctx,\s*"([A-Za-z_][A-Za-z0-9_]*)"', src)))
crypto = sorted(set(re.findall(r'ctx\["fns"\]\["([A-Za-z_][A-Za-z0-9_]*)"\]\s*=\s*l', src)))
print("\nRUNTIME fns in codegen.dark:")
print("  gen_rt_fn:", ", ".join(rt))
print("  crypto/fns:", ", ".join(crypto))
