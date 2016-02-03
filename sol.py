from PIL import Image, ImageDraw

image = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

mem = {}
mcu = {}

for rline in iter(raw_input, '====='):
    line = rline.split(';')

    pin, t, xy = (int(line[0]), int(line[1]),
                  tuple([150 + float(a.replace(',', '.')) * 30 for a in line[2:]]))

    x, y = xy

    if t == 1:
        mcu[pin] = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='red', outline='red')
    else:
        mem[pin] = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='blue', outline='blue')


for i, rline in enumerate(iter(raw_input, '#####')):
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
