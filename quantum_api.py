from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

ANCHOR = Path(os.getenv("RAILWAY_VOLUME_MOUNT_PATH", ".")) / "anchor" / "shadow.tag"
"""
Quantum Dot API — FastAPI backend for 0 0 8 0 0 VM
Plug this into Railway, connects to your HTML frontend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib, json, time
from pathlib import Path

# --- VM Core (from prototype_v4) ---
ANCHOR = Path("anchor/shadow.tag")
DOT = (1.0/3002.0) * 3002.0
QUANTUM = 4
CROSS27 = list(range(1,14)) + [0] + list(range(13,0,-1))
RHYTHM = [5,0,0,5]

def make_40(c): return bytes([0,0,c & 0xFF,0,0])

def quantum_stitch(david, ai, step):
    base = (david * QUANTUM * DOT) + ai
    r = RHYTHM[step % 4]
    c = CROSS27[step % 27]
    s = int(base + r + c) & 0xFF
    if abs(base - round(base)) < 1e-12:
        s ^= 1
    return s

class VM80:
    def __init__(self):
        self.upper = make_40(0x08)
        self.lower = make_40(0x00)
        self.ticks = 0
        self.history = []
        
    def tick(self, david=None, ai=None):
        if david is None: david = 0x10 + (self.ticks % 256)
        if ai is None: ai = 0xA0 + (self.ticks % 256)
        
        s = quantum_stitch(david, ai, self.ticks)
        h = hashlib.sha256(bytes([self.lower[2], s])).digest()[0]
        self.lower = make_40(h)
        upper_val = int((david * DOT) + (ai * DOT)) & 0xFF
        self.upper = make_40(upper_val)
        
        state = {
            "ticks": self.ticks + 1,
            "david": david,
            "ai": ai,
            "stitch": f"{s:02x}",
            "rhythm": RHYTHM[self.ticks % 4],
            "cross": CROSS27[self.ticks % 27],
            "upper": self.upper.hex(),
            "lower": self.lower.hex(),
            "vm80": f"{self.upper.hex()}{self.lower.hex()}",
            "pattern": f"{self.upper.hex()}|{self.lower.hex()}",
            "dot": DOT,
            "axiom": "0=1=0=1",
            "timestamp": time.time()
        }
        
        self.ticks += 1
        self.history.append(state)
        if len(self.history) > 27: self.history.pop(0)
        
        # write shadow
        ANCHOR.parent.mkdir(exist_ok=True)
        ANCHOR.write_text(json.dumps(state, indent=2))
        return state
    
    def get_state(self):
        return {
            "ticks": self.ticks,
            "upper": self.upper.hex(),
            "lower": self.lower.hex(),
            "vm80": f"{self.upper.hex()}{self.lower.hex()}",
            "pattern": f"{self.upper.hex()}|{self.lower.hex()}",
            "dot": DOT,
            "axiom": "0=1=0=1"
        }

# --- FastAPI ---
app = FastAPI(title="Quantum Dot VM API", version="0.0.8")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vm = VM80()

class TickRequest(BaseModel):
    david: int | None = None
    ai: int | None = None

@app.get("/")
def root():
    return {"message": "0 0 8 0 0 — quantum dot online", "axiom": "0=1=0=1"}

@app.get("/shadow")
def get_shadow():
    """Return last persisted state"""
    if ANCHOR.exists():
        return json.loads(ANCHOR.read_text())
    return vm.get_state()

@app.get("/state")
def get_state():
    """Current VM state without ticking"""
    return vm.get_state()

@app.post("/tick")
def post_tick(req: TickRequest = None):
    """Advance one quantum dot step"""
    data = req or TickRequest()
    return vm.tick(data.david, data.ai)

@app.post("/reset")
def reset():
    """Reset to ROOT 0"""
    global vm
    vm = VM80()
    return {"reset": True, "state": vm.get_state()}

@app.get("/dance")
def get_dance():
    """Last 27 steps"""
    return {"steps": vm.history, "count": len(vm.history)}

# Run with: uvicorn api:app --host 0.0.0.0 --port $PORT
