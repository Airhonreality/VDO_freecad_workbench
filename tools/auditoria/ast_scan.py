import ast, sys, pathlib
root = pathlib.Path(sys.argv[1])
rows = []
fn_long = []
for p in sorted(root.rglob("*.py")):
    if "__pycache__" in p.parts: continue
    src = p.read_text(encoding="utf-8")
    t = ast.parse(src)
    classes = [n for n in ast.walk(t) if isinstance(n, ast.ClassDef)]
    funcs = [n for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for f in funcs:
        ln = f.end_lineno - f.lineno + 1
        if ln > 120: fn_long.append((ln, str(p.relative_to(root)), f.name))
    rows.append((len(src.splitlines()), len(classes), len(funcs), str(p.relative_to(root))))
print("TOP files by lines (lines, classes, funcs, file)")
for r in sorted(rows, reverse=True)[:12]: print(r)
print("Funciones > 120 lineas:", len(fn_long))
for r in sorted(fn_long, reverse=True)[:15]: print(r)
