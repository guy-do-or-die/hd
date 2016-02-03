from PIL import Image, ImageDraw
from collections import OrderedDict
from itertools import islice
import random

XS, Y0 = 1000, 800

image = Image.new('RGBA', (XS, Y0), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

mem = {}
mcu = {}

for rline in iter(raw_input, '====='):
    line = rline.split(';')

    pin, t, xy = (int(line[0]), int(line[1]),
                  tuple([200 + float(a.replace(',', '.')) * 30 for a in line[2:]]))

    x, y = xy

    if t == 1:
        mcu[pin] = xy
        draw.ellipse(((x - 2, Y0 - y - 2), (x + 2, Y0 - y + 2)), fill='red', outline='red')
    else:
        mem[pin] = xy
        draw.ellipse(((x - 2, Y0 - y - 2), (x + 2, Y0 - y + 2)), fill='blue', outline='blue')

conns = {}

for i, rline in enumerate(iter(raw_input, '#####')):
    line = rline.split(';')
    n1, n2 = map(int, line)

    n1x, n1y = mcu[n1]
    n2x, n2y = mem[n2]

    '''
    c1 = n1x * n1y
    c2 = (n1x + n2x) * (n1y + n2y)
    '''

    '''
    c1 = n1x - n2x
    c2 = n1y - n2y
    '''

    c1 = n2x
    c2 = n1y

    conns[abs(c1 * c2)] = (n1x, n1y, n2x, n2y)

    if i > 100:
        break

sconns = OrderedDict(sorted(conns.items()))

for i in islice(sconns, 10):
    n1x, n1y, n2x, n2y = conns[i]

    color = '#%06x' % random.randint(0, 0xFFFFFF)

    draw.line(((n1x, Y0 - n1y), (n1x, Y0 - n2y)), fill=color, width=1)
    draw.line(((n1x, Y0 - n2y), (n2x, Y0 - n2y)), fill=color, width=1)
    draw.line(((n1x, Y0 - n1y), (n2x, Y0 - n2y)), fill='white', width=1)


del draw
image.show()
image.save('test.png')

# from pprint import pprint as p
# p(mem)
# p(mcu)
