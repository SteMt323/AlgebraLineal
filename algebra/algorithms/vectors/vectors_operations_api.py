from __future__ import annotations
from typing import Any, Dict, List, Optional

from ...utils.algebraic_support import format_number

Number = float
Vec = List[Number]

def vec_pretty(v: Vec) -> str:
    return "[" + ", ".join(format_number(x) for x in v) + "]"

def add(u: Vec, v: Vec) -> Vec:
    return [a + b for a, b in zip(u, v)]

def sub(u: Vec, v: Vec) -> Vec:
    return [a - b for a, b in zip(u, v)]

def scale(c: Number, u: Vec) -> Vec:
    return [c * x for x in u]

def dot(u: Vec, v: Vec) -> Number:
    return sum(a * b for a, b in zip(u, v))

def same_dim(*vectors: Vec) -> None:
    n = len(vectors[0])
    if any(len(v) != n for v in vectors):
        raise ValueError("Dimensiones incompatibles entre vectores.")
    

# -------------------------------------------
# A) Operaciones con vectores (API)
# -------------------------------------------

def vector_ops_api(
        *,
        operation: str,
        vectors: Dict[str, Any],
        scalars: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    scalars = scalars or {}
    steps: List[str] = []
    diagram: Optional[Dict[str, Any]] = None

    if operation == "add":
        u, v = vectors["u"], vectors["v"]
        same_dim(u, v)
        r = add(u, v)
        steps.append(f"u + v = {vec_pretty(u)} + {vec_pretty(v)} = {vec_pretty(r)}")
        diagram = _diagram_for(u=u, v=v, res=r, mode="add")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors), "scalars": _pretty_scalars(scalars)},
                "steps": steps, "result": {"vector": r, "vector_pretty": vec_pretty(r)}, "diagram": diagram}

    if operation == "sub":
        u, v = vectors["u"], vectors["v"]
        same_dim(u, v)
        r = sub(u, v)
        steps.append(f"u - v = {vec_pretty(u)} - {vec_pretty(v)} = {vec_pretty(r)}")
        diagram = _diagram_for(u=u, v=v, res=r, mode="sub")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors), "scalars": _pretty_scalars(scalars)},
                "steps": steps, "result": {"vector": r, "vector_pretty": vec_pretty(r)}, "diagram": diagram}

    if operation == "escalar":
        u = vectors["u"]; c = scalars["c"]
        r = scale(c, u)
        steps.append(f"c·u = {format_number(c)} · {vec_pretty(u)} = {vec_pretty(r)}")
        diagram = _diagram_for(u=u, res=r, c=c, mode="scale")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors), "scalars": _pretty_scalars(scalars)},
                "steps": steps, "result": {"vector": r, "vector_pretty": vec_pretty(r)}, "diagram": diagram}

    if operation == "comb2":
        u, v = vectors["u"], vectors["v"]
        c, d = scalars["c"], scalars["d"]
        same_dim(u, v)
        cu = scale(c, u); dv = scale(d, v)
        r = add(cu, dv)
        steps.extend([
            f"c·u = {format_number(c)} · {vec_pretty(u)} = {vec_pretty(cu)}",
            f"d·v = {format_number(d)} · {vec_pretty(v)} = {vec_pretty(dv)}",
            f"c·u + d·v = {vec_pretty(cu)} + {vec_pretty(dv)} = {vec_pretty(r)}",
        ])
        diagram = _diagram_for(u=u, v=v, res=r, c=c, d=d, mode="comb2")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors), "scalars": _pretty_scalars(scalars)},
                "steps": steps, "result": {"vector": r, "vector_pretty": vec_pretty(r)}, "diagram": diagram}

    if operation == "comb3":
        u, v, w = vectors["u"], vectors["v"], vectors["w"]
        c, d = scalars["c"], scalars["d"]
        same_dim(u, v, w)
        cv, dw = scale(c, v), scale(d, w)
        r = add(add(u, cv), dw)
        steps.extend([
            f"c·v = {format_number(c)} · {vec_pretty(v)} = {vec_pretty(cv)}",
            f"d·w = {format_number(d)} · {vec_pretty(w)} = {vec_pretty(dw)}",
            f"u + c·v + d·w = {vec_pretty(u)} + {vec_pretty(cv)} + {vec_pretty(dw)} = {vec_pretty(r)}",
        ])
        diagram = _diagram_for(u=u, v=v, w=w, res=r, c=c, d=d, mode="comb3")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors), "scalars": _pretty_scalars(scalars)},
                "steps": steps, "result": {"vector": r, "vector_pretty": vec_pretty(r)}, "diagram": diagram}

    if operation == "dot":
        v, w = vectors["v"], vectors["w"]
        same_dim(v, w)
        s = dot(v, w)
        term_strs = [f"{format_number(a)}·{format_number(b)}" for a, b in zip(v, w)]
        steps.append(" + ".join(term_strs) + f" = {format_number(s)}")
        return {"input": {"operation": operation, "vectors": _pretty_map(vectors)},
                "steps": steps, "result": {"scalar": s, "scalar_pretty": format_number(s)}}

    raise ValueError("operation inválida.")



def _pretty_map(vectors: Dict[str, Vec]) -> Dict[str, Any]:
    return {k: {"raw": vectors[k], "pretty": vec_pretty(vectors[k])} for k in vectors}

def _pretty_scalars(sc: Dict[str, Number]) -> Dict[str, Any]:
    return {k: {"raw": sc[k], "pretty": format_number(sc[k])} for k in sc}

def _diagram_for(*, u=None, v=None, w=None, res=None, c=None, d=None, mode="add") -> Optional[Dict[str, Any]]:
    """
    Estructura simple para que el frontend dibuje (2D/3D):
      { "vectors": [ {label, to, from=[0,0,(0)], emphasis?}, ... ] }
    """
    def vec(vv): return vv if vv is None else list(vv)
    out = {"vectors": []}
    if u is not None: out["vectors"].append({"label": "u", "from": [0]*len(u), "to": vec(u)})
    if v is not None: out["vectors"].append({"label": "v", "from": [0]*len(v), "to": vec(v)})
    if w is not None: out["vectors"].append({"label": "w", "from": [0]*len(w), "to": vec(w)})
    if c is not None and u is not None: out["vectors"].append({"label": f"{format_number(c)}·u", "from": [0]*len(u), "to": vec(scale(c, u))})
    if d is not None and v is not None: out["vectors"].append({"label": f"{format_number(d)}·v", "from": [0]*len(v), "to": vec(scale(d, v))})
    if res is not None: out["vectors"].append({"label": "resultado", "from": [0]*len(res), "to": vec(res), "emphasis": True})
    return out