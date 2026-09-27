import re, json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
F = "C:/Users/EM360BP1/Downloads/GUIONES_GRABACION_2026-09-27 (1).md"
t = open(F, encoding="utf-8").read()
out = []
secs = re.split(r"^## ", t, flags=re.M)
def clean(s): return re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()
for sec in secs[1:]:
    head, _, body = sec.partition("\n")
    m = re.match(r"([GJ]\d+) · (.+)", head.strip())
    if not m: continue
    sid, title = m.group(1), m.group(2).strip()
    body = body.split("\n---")[0]
    meta = re.search(r"^\*\*(Publicación|Duración).*$", body, re.M)
    meta = [clean(meta.group(0)).rstrip(".")] if meta else []
    alt = re.search(r"^\*\*Gancho alternativo:\*\*\s*(.+)$", body, re.M)
    rod = re.search(r"^\*\*Rodaje:\*\*\s*(.+)$", body, re.M)
    txt = body.split("**Texto a cámara**", 1)[1]
    txt = re.split(r"^\*\*(Gancho alternativo|Rodaje):\*\*", txt, flags=re.M)[0]
    paras = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
    gancho = clean(paras[0]) if paras and paras[0].startswith("**") else ""
    if gancho: paras = paras[1:]
    blocks = [{"t": "", "b": "Texto a cámara", "x": "\n\n".join(clean(p) for p in paras)}]
    if alt: blocks.append({"t": "", "b": "Gancho alternativo · segunda entrada, no se lee seguido", "x": alt.group(1).strip().strip("«»")})
    grupo = "Plan 100K · 12 guiones" if sid.startswith("G") else "Julio · 21 guiones actualizados"
    out.append({"grupo": grupo, "id": sid, "title": title, "meta": meta, "cifras": [], "gancho": gancho,
                "nota": (rod.group(1).strip() if rod else ""), "blocks": blocks})
json.dump(out, open(os.path.join(S, "guiones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "guiones;", sum(len(o["blocks"][0]["x"].split()) for o in out), "palabras de texto a cámara")
for o in out[:2] + out[-1:]: print(o["id"], "|", o["title"], "|", o["gancho"][:60], "| alt:", len(o["blocks"]) > 1, "| nota:", bool(o["nota"]))
