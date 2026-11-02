import ast
import collections
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
bodies = collections.defaultdict(list)
for p in root.rglob("*.py"):
    if "__pycache__" in p.parts: continue
    t = ast.parse(p.read_text(encoding="utf-8"))
    for f in ast.walk(t):
        if isinstance(f, ast.FunctionDef) and len(f.body) >= 3:
            body = f.body
            if isinstance(body[0], ast.Expr) and isinstance(getattr(body[0],'value',None), ast.Constant): body = body[1:]
            if len(body) < 2: continue
            dump = "\n".join(ast.dump(s) for s in body)
            bodies[hashlib.md5(dump.encode()).hexdigest()].append((f.name, str(p.relative_to(root)), f.lineno))
clones = [v for v in bodies.values() if len(v) > 1]
print("grupos de funciones con cuerpo identico (>=2 stmts):", len(clones))
for g in clones[:20]: print(g)
