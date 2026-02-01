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
font5x5 = {
"A":[" X ","X X","XXX","X X","X X"],
"B":["XX ","X X","XX ","X X","XX "],
"C":[" XX","X  ","X  ","X  "," XX"],
"D":["XX ","X X","X X","X X","XX "],
"E":["XXX","X  ","XX ","X  ","XXX"],
"F":["XXX","X  ","XX ","X  ","X  "],
"G":[" XX","X  ","X X","X X"," XX"],
"H":["X X","X X","XXX","X X","X X"],
"I":["XXX"," X "," X "," X ","XXX"],
"J":["  X","  X","  X","X X"," X "],
"K":["X X","X X","XX ","X X","X X"],
"L":["X  ","X  ","X  ","X  ","XXX"],
"M":["X X","XXX","XXX","X X","X X"],
"N":["X X","XXX","XXX","XXX","X X"],
"O":["XXX","X X","X X","X X","XXX"],
"P":["XX ","X X","XX ","X  ","X  "],
"Q":["XXX","X X","X X","XX "," XX"],
"R":["XX ","X X","XX ","X X","X X"],
"S":[" XX","X  "," X ","  X","XX "],
"T":["XXX"," X "," X "," X "," X "],
"U":["X X","X X","X X","X X","XXX"],
"V":["X X","X X","X X","X X"," X "],
"W":["X X","X X","XXX","XXX","X X"],
"X":["X X","X X"," X ","X X","X X"],
"Y":["X X","X X"," X "," X "," X "],
"Z":["XXX","  X"," X ","X  ","XXX"],

"0":["XXX","X X","X X","X X","XXX"],
"1":[" X ","XX "," X "," X ","XXX"],
"2":["XX ","  X"," X ","X  ","XXX"],
"3":["XX ","  X"," X ","  X","XX "],
"4":["X X","X X","XXX","  X","  X"],
"5":["XXX","X  ","XX ","  X","XX "],
"6":[" XX","X  ","XX ","X X"," XX"],
"7":["XXX","  X"," X "," X "," X "],
"8":[" XX","X X"," XX","X X"," XX"],
"9":[" XX","X X"," XX","  X","XX "],

" ":["   ","   ","   ","   ","   "],
"!":[" X "," X "," X ","   "," X "],
"?":["XX ","  X"," X ","   "," X "],
".":["   ","   ","   ","   "," X "],
",":["   ","   ","   "," X ","X  "],
"-":["   ","XXX","   ","   ","   "],
":":["   "," X ","   "," X ","   "],
";":["   "," X ","   "," X ","X  "],
"'":[" X "," X ","   ","   ","   "],
"\"":["X X","X X","   ","   ","   "],
"/":["  X","  X"," X ","X  ","X  "],
"\\":["X  ","X  "," X ","  X","  X"],
"+":["   "," X ","XXX"," X ","   "],
"=":["   ","XXX","   ","XXX","   "],
"*":[" X ","X X"," X ","X X"," X "],
"#":[" X ","XXX"," X ","XXX"," X "],
"&":[" X ","X X"," X ","X X"," XX"],
"%":["XX ","  X"," X ","X  ","XX"],
"@":[" XX","X X","X X","X  "," XX"],
"$":[" X ","XXX"," X ","XX "," X "],
"^":[" X ","X X","   ","   ","   "],
"_":["   ","   ","   ","   ","XXX"],
"`":[" X ","  X","   ","   ","   "],
"~":["   "," XX","X X","   ","   "],
"|":[" X "," X "," X "," X "," X "]
}


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
                canvas.create_rectangle(
                    x0+x*4, y0+y*4,
                    x0+x*4+4, y0+y*4+4,
                    fill=color, outline=color
                )

def wait_ms(ms, callback):
    root.after(ms, callback)

# ===== PARSER =====
FUNCTIONS = {}
LABELS = {}

def parse_blocks(lines):
    stack = [(-1, [])]
    for idx,line in enumerate(lines):
        line = line.split(";")[0].rstrip()
        if not line: continue
        indent = len(line)-len(line.lstrip())
        while indent <= stack[-1][0]:
            stack.pop()
        entry = {"line":line, "children":[]}
        stack[-1][1].append(entry)
        stack.append((indent, entry["children"]))
        if line.upper().startswith("FUNC"):
            parts = line.split()
            FUNCTIONS[parts[1]] = {
                "lines": entry["children"],
                "args": parts[2:]
            }
        elif line.startswith(":"):
            LABELS[line[1:].strip()] = len(stack[0][1])-1
    return stack[0][1]

# ===== EXEC =====
def exec_block_step(block, canvas, debug_box, locals=None, i=0):
    global cmp
    if locals is None:
        locals = {}

    if i >= len(block):
        update_keys()
        return

    entry = block[i]
    line = entry["line"]
    debug_box.insert(tk.END, line + "\n")
    debug_box.see(tk.END)

    parts = line.split(None, 1)
    op = parts[0].upper()
    args = [a.strip() for a in parts[1].split(",")] if len(parts) > 1 else []

    try:
        if op == "CALL":
            name = args[0]
            values = [val(a, locals) for a in args[1:]]
            if name in FUNCTIONS:
                fn = FUNCTIONS[name]
                new_locals = locals.copy()
                for i2, arg in enumerate(fn["args"]):
                    if i2 < len(values):
                        new_locals[arg] = values[i2]
                CALL_STACK.append((block, i))
                exec_block_step(fn["lines"], canvas, debug_box, new_locals, 0)
                block, i = CALL_STACK.pop()

        elif op == "MOVE":
            regs[args[1]] = val(args[0], locals)
        elif op == "ADD":
            regs[args[1]] += val(args[0], locals)
        elif op == "SUB":
            regs[args[1]] -= val(args[0], locals)
        elif op == "MUL":
            regs[args[1]] *= val(args[0], locals)
        elif op == "DIV":
            regs[args[1]] //= val(args[0], locals)
        elif op == "MOD":
            regs[args[1]] %= val(args[0], locals)
        elif op == "NEG":
            regs[args[0]] = -regs[args[0]]
        elif op == "CMP":
            cmp = val(args[1], locals) - val(args[0], locals)

        elif op == "WAIT":
            delay = val(args[0], locals) if args else 0
            wait_ms(delay, lambda: exec_block_step(block, canvas, debug_box, locals, i+1))
            return

        elif op == "CLS":
            r = val(args[0], locals) if len(args)>0 else 0
            g = val(args[1], locals) if len(args)>1 else 0
            b = val(args[2], locals) if len(args)>2 else 0
            canvas.delete("all")
            canvas.create_rectangle(
                0,0,320,180,
                fill=f"#{r:02x}{g:02x}{b:02x}",
                outline=""
            )

        elif op == "PIX":
            x = val(args[0], locals)
            y = val(args[1], locals)
            r = val(args[2], locals)
            g = val(args[3], locals)
            b = val(args[4], locals)
            canvas.create_rectangle(
                x,y,x+4,y+4,
                fill=f"#{r:02x}{g:02x}{b:02x}",
                outline=""
            )

        elif op == "PRINT":
            x = val(args[0], locals)
            y = val(args[1], locals)
            text = args[2].strip('"')
            color = f"#{val(args[3]):02x}{val(args[4]):02x}{val(args[5]):02x}"
            for i2,ch in enumerate(text):
                draw_char(canvas, ch, x+i2*24, y, color)

        elif op == "SOUND":
            play_sound(val(args[0]), val(args[1]), val(args[2]))

        elif op == "BRA":
            label = args[0]
            if label in LABELS:
                root.after(1, lambda: exec_block_step(block, canvas, debug_box, locals, LABELS[label]))
                return

    except Exception as e:
        debug_box.insert(tk.END, f"ERROR: {e}\n")

    canvas.update()

    if entry["children"]:
        exec_block_step(entry["children"], canvas, debug_box, locals.copy(), 0)

    root.after(1, lambda: exec_block_step(block, canvas, debug_box, locals, i+1))

# ===== GUI =====
root = tk.Tk()
root.title("HASM IDE")

left = tk.Frame(root)
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right = tk.Frame(root)
right.pack(side=tk.RIGHT, fill=tk.BOTH)

code_box = scrolledtext.ScrolledText(
    left,
    bg="black",
    fg="lime",
    insertbackground="lime",   
    insertwidth=2,             
    insertontime=600,         
    insertofftime=400          
)

code_box.pack(fill=tk.BOTH, expand=True)

code_box.focus_set()  
code_box.insert(tk.END, """
CLS #0,#0,#0
PRINT #10,#10,"WAIT TEST",#255,#255,#255
WAIT #1000
CLS #0,#0,#0
PRINT #10,#10,"DONE",#0,#255,#0
""")

debug_box = scrolledtext.ScrolledText(right, height=10, bg="black", fg="lime")
debug_box.pack(fill=tk.BOTH)

canvas = tk.Canvas(right, width=320, height=180, bg="black")
canvas.pack()
canvas.bind("<KeyPress>", on_key)
canvas.bind("<KeyRelease>", on_key_release)
canvas.focus_set()

def run():
    block = parse_blocks(code_box.get("1.0", tk.END).splitlines())
    debug_box.delete("1.0", tk.END)
    canvas.delete("all")
    exec_block_step(block, canvas, debug_box)

tk.Button(left, text="Run", command=run).pack(fill=tk.X)

root.mainloop()
