from PIL import Image, ImageDraw

image = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

mem = {}
mcu = {}

for rline in iter(raw_input, '====='):
    line = rline.split(';')

    pin, t, xy = (int(line[0]), int(line[1]),
                  map(lambda a: float(a.replace(',', '.')) * 40, line[2:]))

    if t == 2:
        mem[pin] = tuple(xy)
    else:
        mcu[pin] = tuple(xy)

    x, y = xy
    draw.ellipse(((x - 5, y - 5), (x + 5, y + 5)), fill='red', outline='red')

i = 0
for rline in iter(raw_input, '#####'):
    i += 1
    line = rline.split(';')
    n1, n2 = map(int, line)

    n1x, n1y = mcu[n1]
    n2x, n2y = mem[n2]

    draw.line(((n1x, n1y), (n1x, n2y)), fill='green', width=1)
    draw.line(((n1x, n2y), (n2x, n2y)), fill='green', width=1)
    if i > 100:
        break

del draw
image.show()
image.save('test.png')

# from pprint import pprint as p
# p(mem)
# p(mcu)
