import tkinter as tk
from tkinter import scrolledtext
import numpy
import pygame

# ===== STATE =====
regs = {"D0":0, "D1":0, "D2":0, "D3":0}
cmp = 0
CALL_STACK = []

# ===== KEYBOARD =====
KEYS = {}
KEYS_LAST = {}

def on_key(event):
    KEYS[event.keysym.upper()] = 1

def on_key_release(event):
    KEYS[event.keysym.upper()] = 0

def update_keys():
    for k in KEYS:
        KEYS_LAST[k] = KEYS[k]

# ===== AUDIO =====
pygame.mixer.init(frequency=44100, size=-16, channels=2)
audio_channels = [None]*4

def play_sound(ch, freq, ms):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * ms / 1000)
        t = numpy.linspace(0, ms/1000, n_samples, False)
        wave = 0.1 * numpy.sign(numpy.sin(2 * numpy.pi * freq * t))
        sound = numpy.int16(wave * 32767)
        sound_stereo = numpy.column_stack((sound, sound))
        sound_obj = pygame.sndarray.make_sound(sound_stereo)
        if audio_channels[ch]:
            audio_channels[ch].stop()
        sound_obj.play()
        audio_channels[ch] = sound_obj
    except Exception as e:
        print(f"Sound error: {e}")

# ===== FONT =====
font5x5 = {"A":[" X ","X X","XXX","X X","X X"], "B":["XX ","X X","XX ","X X","XX "], "C":[" XX","X  ","X  ","X  "," XX"], "D":["XX ","X X","X X","X X","XX "], "E":["XXX","X  ","XX ","X  ","XXX"], "F":["XXX","X  ","XX ","X  ","X  "], "G":[" XX","X  ","X X","X X"," XX"], "H":["X X","X X","XXX","X X","X X"], "I":["XXX"," X "," X "," X ","XXX"], "J":["  X","  X","  X","X X"," X "], "K":["X X","X X","XX ","X X","X X"], "L":["X  ","X  ","X  ","X  ","XXX"], "M":["X X","XXX","XXX","X X","X X"], "N":["X X","XXX","XXX","XXX","X X"], "O":["XXX","X X","X X","X X","XXX"], "P":["XX ","X X","XX ","X  ","X  "], "Q":["XXX","X X","X X","XX "," XX"], "R":["XX ","X X","XX ","X X","X X"], "S":[" XX","X  "," X ","  X","XX "], "T":["XXX"," X "," X "," X "," X "], "U":["X X","X X","X X","X X","XXX"], "V":["X X","X X","X X","X X"," X "], "W":["X X","X X","XXX","XXX","X X"], "X":["X X","X X"," X ","X X","X X"], "Y":["X X","X X"," X "," X "," X "], "Z":["XXX","  X"," X ","X  ","XXX"], "0":["XXX","X X","X X","X X","XXX"], "1":[" X ","XX "," X "," X ","XXX"], "2":["XX ","  X"," X ","X  ","XXX"], "3":["XX ","  X"," X ","  X","XX "], "4":["X X","X X","XXX","  X","  X"], "5":["XXX","X  ","XX ","  X","XX "], "6":[" XX","X  ","XX ","X X"," XX"], "7":["XXX","  X"," X "," X "," X "], "8":[" XX","X X"," XX","X X"," XX"], "9":[" XX","X X"," XX","  X","XX "], " ":["   ","   ","   ","   ","   "], "!":[" X "," X "," X ","   "," X "], "?":["XX ","  X"," X ","   "," X "], ".":["   ","   ","   ","   "," X "], ",":["   ","   ","   "," X ","X  "], "-":["   ","XXX","   ","   ","   "], ":":["   "," X ","   "," X ","   "], ";":["   "," X ","   "," X ","X  "], "'":[" X "," X ","   ","   ","   "], "\"":["X X","X X","   ","   ","   "], "/":["  X","  X"," X ","X  ","X  "], "\\":["X  ","X  "," X ","  X","  X"], "+":["   "," X ","XXX"," X ","   "], "=":["   ","XXX","   ","XXX","   "], "*":[" X ","X X"," X ","X X"," X "], "#":[" X ","XXX"," X ","XXX"," X "], "&":[" X ","X X"," X ","X X"," XX"], "%":["XX ","  X"," X ","X  ","XX"], "@":[" XX","X X","X X","X  "," XX"], "$":[" X ","XXX"," X ","XX "," X "], "^":[" X ","X X","   ","   ","   "], "_":["   ","   ","   ","   ","XXX"], "`":[" X ","  X","   ","   ","   "], "~":["   "," XX","X X","   ","   "], "|":[" X "," X "," X "," X "," X "]}

# ===== UTIL =====
def val(x, locals=None):
    x = x.strip()
    context = {}
    if locals: context.update(locals)
    context.update(regs)
    if x.startswith("#"):
        return int(x[1:])
    try:
        return int(eval(x, {}, context))
    except:
        raise ValueError(f"Invalid literal or expression: {x}")

def draw_char(canvas, ch, x0, y0, color="#000000"):
    bitmap = font5x5.get(ch.upper(), font5x5.get(" "))
    for y,row in enumerate(bitmap):
        for x,c in enumerate(row):
            if c=="X":
                canvas.create_rectangle(x0+x*4, y0+y*4, x0+x*4+4, y0+y*4+4, fill=color, outline=color)

# ===== PARSER =====
FUNCTIONS = {}
LABELS = {}
def parse_blocks(lines):
    stack = [(-1, [])]
    for idx,line in enumerate(lines):
        orig = line
        line = line.split(";")[0].rstrip()
        if not line: continue
        indent = len(line)-len(line.lstrip())
        while indent <= stack[-1][0]: stack.pop()
        entry = {"line":line, "children":[]}
        stack[-1][1].append(entry)
        stack.append((indent, entry["children"]))
        if line.upper().startswith("FUNC"):
            parts = line.split()
            name = parts[1]
            args = parts[2:] if len(parts)>2 else []
            FUNCTIONS[name] = {"lines": entry["children"], "args": args}
        elif line.startswith(":"):
            LABELS[line[1:].strip()] = len(stack[0][1])-1
    return stack[0][1]

# ===== EXEC (non-blocking) =====
def exec_block_step(block, canvas, debug_box, locals=None, i=0):
    global cmp
    if locals is None: locals={}
    if i >= len(block):
        update_keys()
        return

    entry = block[i]
    line = entry["line"]
    debug_box.insert(tk.END, line+"\n"); debug_box.see(tk.END)
    parts = line.split(None,1)
    op = parts[0].upper()
    args_raw = parts[1] if len(parts)>1 else ""
    args = [a.strip() for a in args_raw.split(",")] if args_raw else []

    try:
        if op=="CALL":
            func_name = args[0]
            func_args = [val(a, locals) for a in args[1:]]
            if func_name in FUNCTIONS:
                func_data = FUNCTIONS[func_name]
                new_locals = locals.copy()
                for idx,arg_name in enumerate(func_data["args"]):
                    if idx<len(func_args):
                        new_locals[arg_name] = func_args[idx]
                CALL_STACK.append((block,i))
                exec_block_step(func_data["lines"], canvas, debug_box, new_locals, 0)
                block,i = CALL_STACK.pop()
        elif op=="MOVE": regs[args[1]] = val(args[0], locals)
        elif op=="ADD": regs[args[1]] += val(args[0], locals)
        elif op=="SUB": regs[args[1]] -= val(args[0], locals)
        elif op=="MUL": regs[args[1]] *= val(args[0], locals)
        elif op=="DIV": regs[args[1]] //= val(args[0], locals)
        elif op=="MOD": regs[args[1]] %= val(args[0], locals)
        elif op=="NEG": regs[args[0]] = -regs[args[0]]
        elif op=="CMP": cmp = val(args[1], locals)-val(args[0], locals)
        elif op=="CLS":
            cr = val(args[0], locals) if len(args)>0 else 0
            cg = val(args[1], locals) if len(args)>1 else 0
            cb = val(args[2], locals) if len(args)>2 else 0
            canvas.delete("all")
            canvas.create_rectangle(0,0,320,180,fill=f"#{cr:02x}{cg:02x}{cb:02x}", outline=f"#{cr:02x}{cg:02x}{cb:02x}")
        elif op=="PIX":
            x = val(args[0], locals)
            y = val(args[1], locals)
            r = val(args[2], locals) if len(args)>2 else 0
            g = val(args[3], locals) if len(args)>3 else 0
            b = val(args[4], locals) if len(args)>4 else 0
            canvas.create_rectangle(x,y,x+4,y+4,fill=f"#{r:02x}{g:02x}{b:02x}", outline=f"#{r:02x}{g:02x}{b:02x}")
        elif op=="PRINT":
            x = val(args[0], locals)
            y = val(args[1], locals)
            text = args[2].strip('"')
            color = f"#{val(args[3], locals):02x}{val(args[4], locals):02x}{val(args[5], locals):02x}" if len(args)>=6 else "#FFFFFF"
            for idx,ch in enumerate(text):
                draw_char(canvas,ch,x+idx*24,y,color)
        elif op=="SOUND":
            play_sound(val(args[0], locals),val(args[1], locals),val(args[2], locals))
        elif op=="BRA":
            label = args[0]
            if label in LABELS:
                i = LABELS[label]
                root.after(1, lambda: exec_block_step(block, canvas, debug_box, locals, i))
                return
    except Exception as e:
        debug_box.insert(tk.END,f"ERROR: {e}\n"); debug_box.see(tk.END)

    canvas.update()
    if entry["children"]:
        exec_block_step(entry["children"], canvas, debug_box, locals.copy(), 0)

    root.after(1, lambda: exec_block_step(block, canvas, debug_box, locals, i+1))

# ===== GUI =====
root = tk.Tk(); root.title("HASM IDE")

left = tk.Frame(root); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right = tk.Frame(root); right.pack(side=tk.RIGHT, fill=tk.BOTH)

code_box = scrolledtext.ScrolledText(left, width=50, height=25, bg="black", fg="lime", insertbackground="lime")
code_box.pack(fill=tk.BOTH, expand=True)
code_box.insert(tk.END, """
CLS #0,#0,#0
PRINT #10,#10,"HELLO WORLD!",#255,#255,#255
""")

debug_box = scrolledtext.ScrolledText(right, width=50, height=10, bg="black", fg="lime")
debug_box.pack(fill=tk.BOTH)

canvas = tk.Canvas(right, width=320, height=180, bg="black")
canvas.pack(pady=10)
canvas.bind("<KeyPress>", on_key)
canvas.bind("<KeyRelease>", on_key_release)
canvas.focus_set()

def run():
    lines = code_box.get("1.0", tk.END).splitlines()
    block_tree = parse_blocks(lines)
    canvas.delete("all")
    debug_box.delete("1.0", tk.END)
    canvas.focus_set()
    exec_block_step(block_tree, canvas, debug_box)

run_btn = tk.Button(left, text="Run", command=run, bg="black", fg="lime", activebackground="lime", activeforeground="black")
run_btn.pack(fill=tk.X)

root.mainloop()
