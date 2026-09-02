#!/usr/bin/env python3
"""Validate a Turbine theme JSON against the Zed schema and WCAG AA.
Usage: python3 validate_turbine.py turbine.json schema_keys.txt"""
import json, sys

def lin(c):
    c /= 255
    return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
def L(h):
    h = h.lstrip('#')[:6]
    r,g,b = [int(h[i:i+2],16) for i in (0,2,4)]
    return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
def cr(a,b):
    la,lb = L(a),L(b); hi,lo = max(la,lb),min(la,lb)
    return (hi+0.05)/(lo+0.05)

theme = json.load(open(sys.argv[1]))
schema = set(open(sys.argv[2]).read().split())
fail = 0
for t in theme['themes']:
    style = t['style']
    unknown = sorted(set(style) - schema)
    missing = sorted(schema - set(style) - {'players','accents','syntax','background.appearance'})
    print(f"\n=== {t['name']} ({t['appearance']}) ===")
    if unknown:
        print(f"  INVENTED KEYS ({len(unknown)}) — Zed will ignore these:"); fail += len(unknown)
        for k in unknown: print(f"    {k}")
    if missing:
        print(f"  UNSET KEYS ({len(missing)}) — will fall back to defaults:"); fail += len(missing)
        for k in missing: print(f"    {k}")
    bg = style.get('editor.background')
    if bg:
        for k in ('editor.foreground','text','text.muted','editor.line_number'):
            if k in style:
                r = cr(style[k], bg)
                v = 'AAA' if r >= 7 else ('AA' if r >= 4.5 else 'FAIL')
                if v == 'FAIL': fail += 1
                print(f"  {k:<22} {r:>6.2f}:1  {v}")
        for cap, st in style.get('syntax', {}).items():
            c = st.get('color')
            if c:
                r = cr(c, bg)
                if r < 4.5:
                    print(f"  syntax.{cap:<15} {r:>6.2f}:1  FAIL"); fail += 1
print(f"\n{'PASS — ready to ship' if fail == 0 else f'{fail} issue(s) found'}")
sys.exit(1 if fail else 0)
