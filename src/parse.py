import re, json, glob, os, html
P = "G:/Mi unidad/99_Intercambio_EM360/PLAN_CONTENIDO_INSTAGRAM"
J = "I:/Mi unidad/00_Sistema_IA/Dpto_Marketing/_Produccion/SESION_GRABACION_01_2026-07-27"
def strip_md(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = s.replace("<br>", "\n").replace(" // ", "\n")
    return s.strip()
out = []
for f in sorted(glob.glob(P + "/GUION_*.md")):
    t = open(f, encoding="utf-8").read()
    num = re.search(r"GUION_(\d+)", f).group(1)
    title = re.search(r"^# GUION \d+ - (.+)$", t, re.M).group(1).strip()
    meta = re.findall(r"^\*\*(.+?)\*\*\s*$", t, re.M)[:3]
    cif = re.search(r"## Cifras.*?\n(.*?)\n---", t, re.S)
    cifras = [strip_md(l[2:]) for l in cif.group(1).strip().splitlines() if l.startswith("- ")] if cif else []
    g = re.search(r"> ## (.+)", t).group(1).strip()
    blocks = []
    for row in re.findall(r"^\| \*\*(.+?)\*\* \| \*\*(.+?)\*\* \| (.+?) \|$", t, re.M):
        blocks.append({"t": row[0], "b": row[1], "x": strip_md(row[2])})
    nota = blocks[0]["x"] if blocks else ""
    blocks = blocks[1:]
    out.append({"grupo": "Plan 100K · octubre", "id": "G" + num, "title": title, "meta": [strip_md(m) for m in meta],
                "cifras": cifras, "gancho": g, "nota": nota, "blocks": blocks})
# julio talking heads
for fn in ["GUIONES_SESION_01_prompter.txt", "GUIONES_SESION_02_prompter.txt"]:
    t = open(os.path.join(J, fn), encoding="utf-8").read()
    parts = re.split(r"^### ", t, flags=re.M)
    for p in parts[1:]:
        head, _, body = p.partition("\n")
        m = re.match(r"Guion (\d+) — (.+)", head.strip())
        blocks = []
        cur = None
        for line in body.strip().splitlines():
            line = line.strip()
            if not line: continue
            mm = re.match(r"^\[(.+?)\]$", line)
            if mm:
                cur = {"t": "", "b": mm.group(1), "x": ""}; blocks.append(cur)
            else:
                if cur is None:
                    cur = {"t": "", "b": "", "x": ""}; blocks.append(cur)
                cur["x"] = (cur["x"] + "\n" + line).strip()
        gancho = blocks[0]["x"] if blocks and blocks[0]["b"].upper().startswith("HOOK") else ""
        if gancho: blocks = blocks[1:]
        out.append({"grupo": "Julio · talking heads", "id": "J" + m.group(1), "title": m.group(2).strip(), "meta": ["Sesión de julio, aprobado 27-jul-2026"],
                    "cifras": [], "gancho": gancho, "nota": "", "blocks": blocks})
json.dump(out, open(os.path.join(os.path.dirname(__file__), "guiones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out)); 
for o in out: print(o["id"], "|", o["title"], "|", len(o["blocks"]), "bloques", "| gancho:", bool(o["gancho"]))
