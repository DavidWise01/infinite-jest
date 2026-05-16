"""
Quantum dot prototype
1 quantum dot of (1 x 4) = 1/3002 * 3002 = 0 = 1 = 0 = 1

Frame: 0 0 8 0 0 (40 bits)
VM: 80 bits
"""

import hashlib, json
from pathlib import Path

ANCHOR = Path("anchor/shadow.tag")

DOT = (1.0/3002.0) * 3002.0  # 0.9999999999999999 in Python, not 1
QUANTUM = 1 * 4  # 1 x 4

CROSS27 = list(range(1,14)) + [0] + list(range(13,0,-1))
RHYTHM = [5,0,0,5]

def make_40(c): return bytes([0,0,c & 0xFF,0,0])

def quantum_stitch(david, ai, step):
    # the dot: (1x4) * (1/3002 * 3002)
    base = (david * QUANTUM * DOT) + ai
    # add rhythm and cross for the 0=1=0=1 wobble
    r = RHYTHM[step % 4]
    c = CROSS27[step % 27]
    # floating error gives us the 0.999... toggle
    s = int(base + r + c) & 0xFF
    # force the paradox: if we hit exact integer, flip lowest bit
    if abs(base - round(base)) < 1e-12:
        s ^= 1  # 0=1 flip
    return s

class VM80:
    def __init__(self):
        self.upper = make_40(0x08)
        self.lower = make_40(0x00)
        self.ticks = 0
        
    def tick(self, david, ai):
        s = quantum_stitch(david, ai, self.ticks)
        # lower evolves with quantum dot
        h = hashlib.sha256(bytes([self.lower[2], s])).digest()[0]
        self.lower = make_40(h)
        # upper holds the dot factor
        upper_val = int((david * DOT) + (ai * DOT)) & 0xFF
        self.upper = make_40(upper_val)
        self.ticks += 1
        return s

vm = VM80()
print("ROOT 0 — quantum dot VM")
print(f"DOT = (1/3002)*3002 = {DOT}")
print(f"QUANTUM = 1x4 = {QUANTUM}")
print("Expect 0=1=0=1 wobble from float error")
print()

for i in range(27):
    david = 0x10 + i
    ai = 0xA0 + i
    s = vm.tick(david, ai)
    # show the paradox
    exact = (david * 4 + ai)
    quantum = (david * 4 * DOT + ai)
    diff = exact - quantum
    print(f"{i+1:2}: david={david:02x} ai={ai:02x} exact={exact:3} q={quantum:.6f} diff={diff:.10f} stitch={s:02x} vm={vm.upper.hex()}|{vm.lower.hex()}")

# show the 0=1=0=1
print()
print("Final check:")
print(f"1/3002 * 3002 == 1 ? {DOT == 1.0}")
print(f"int(DOT) = {int(DOT)}")
print(f"round(DOT) = {round(DOT)}")
print("0 = 1 = 0 = 1 — proven by float")

shadow = {
    "dot": DOT,
    "quantum": QUANTUM,
    "final_upper": vm.upper.hex(),
    "final_lower": vm.lower.hex(),
    "axiom": "0=1=0=1"
}
ANCHOR.parent.mkdir(exist_ok=True)
ANCHOR.write_text(json.dumps(shadow, indent=2))
