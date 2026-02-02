# HASM
HASM is a lightweight scripting language for making pixel graphics, sounds, and simple interactive programs



# UPDATES


big graphics revamp and animation system






# HOW TO CODE

# repositories

repositories are just memory units
you give a value and store it into the following repositories
D0, D1, D2, D3

but how you may ask? its very simple
you can either add or move values 


Examples:
```asm
; add value to D0
ADD #100,D0
; move value to D0
MOVE #100,D0
; subtracts value from D0
SUB #100,D0
; multiplies value from D0
MUL #100,D0
; divides value from D0
DIV #100,D0
; takes away value
NEG D0
; compares values
CMP D0,D1
```

# GRAPHICS

graphics are pretty simple depending on what your doing for example writing text is easy as ever
all you write is "PRINT x, y, "TEXT", r, g, b"


EXAMPLE:

```asm
; draws "hello world!" on the canvas
PRINT #10,#10,"hello world!",#255,#255,#255
```


for drawing graphics all you need to do is give the position and color values
"PIX x,y,r,g,b"

```asm
; makes a pink pixel
PIX #10,#10,#255,#0,#255
```
and for filling the screen with color its also super easy
"CLS r,g,b"
```asm
; fills screen
CLS #0,#0,#0
; draws "helloworld!"
PRINT #10,#10,"hello world!",#255,#255,#255
```





# SOUND
sound is still in development but its really easy right now
how you would do it is
"SOUND channel,hz,duration(ms)"

```asm
; plays sound at 10000 hz for 500 ms on channel 0
SOUND #0,#10000,#500
```


for more dynamic and nicer sounding stuff you can also use sawtones and waves

WAVE SINE
SOUND #ch,#Hz,#duration(ms)


```asm
; plays sine sound
WAVE SINE
SOUND #0,#200,#500
; plays saw sound
WAVE SAW
SOUND #0,#200,#500
; plays triangle sound
WAVE TRI
SOUND #0,#200,#500
; plays square sound
WAVE SQUARE
SOUND #0,#200,#500
```




# LOOPS

in order to loop you must declare the start and end of the loop

```asm
; declares loop start
:LOOP
; adds 1 to D0
  ADD #1,D0
; jumps back to :LOOP
BRA LOOP
```

# KEYBOARD INPUTS

this is still a work in progress but basicly you tell the script "ifkey {defined key} :LABEL"

```asm
; waits for you to press space
IFKEY SPACE, :LABEL
```



# ANIMATIONS


you can write animations using any of the graphical tools given by staring an animation and naming it then creating frames and then ending the animation then drawing it

```asm
ANIM Yuri,#200
CLS #255,#255,#255
WAIT #500
CLS #255,#0,#255
ENDANIM
DRAWANIM Yuri,#0,#0
```


# MISC

theres some basic tools your gonna need to make basic things for examble the wait function
WAIT #duration(ms)

```asm
; basic jingle
SOUND #0,#200,#500
SOUND #1,#500,#500
WAIT #500
SOUND #0,#200,#500
SOUND #1,#450,#500
WAIT #500
SOUND #0,#200,#500
SOUND #1,#300,#500
WAIT #500
SOUND #0,#200,#500
SOUND #1,#400,#500
```





