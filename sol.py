from PIL import Image, ImageDraw
from collections import OrderedDict
from itertools import islice
from functools import partial
import operator as op
import random

XS, Y0 = 1000, 800

image = Image.new('RGBA', (XS, Y0), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

mem = {}
mcu = {}


def overlap(conn1, conn2):
    deltas = [op.sub(*p) for p in zip(conn1, conn2)]
    xs, ys = deltas[::2], deltas[1::2]
    return not (all(t >= 0 for t in xs) and all(t <= 0 for t in ys)
                or all(t <= 0 for t in xs) and all(t >= 0 for t in ys))


def boards(draw):
    for pin, xy in mcu.items():
        x, y = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='red', outline='red')

    for pin, xy in mem.items():
        x, y = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='blue', outline='blue')


for rline in iter(raw_input, '====='):
    line = rline.split(';')

    pin, t, xy = (int(line[0]), int(line[1]),
                  tuple([200 + float(a.replace(',', '.')) * 30 for a in line[2:]]))

    x, y = xy

    if t == 1:
        mcu[pin] = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='red', outline='red')
    else:
        mem[pin] = xy
        draw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='blue', outline='blue')

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

    c1 = n1x - n2x
    c2 = n1y - n2y

    '''
    c1 = n2x
    c2 = n1y
    '''

    conns[c1 * c2] = (n1x, n1y, n2x, n2y)

    if i > 100:
        break


groups = [[]]

for xconn in conns.values():
    added = False
    o = partial(overlap, xconn)

    for group in groups:
        if any(map(o, group)):
            continue
        else:
            group.append(xconn)
            added = True
            break

    if not added:
        groups.append([xconn])


for n, group in enumerate(groups):
    image = Image.new('RGBA', (XS, Y0), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)

    for conn in group:
        n1x, n1y, n2x, n2y = conn
        color = '#%06x' % random.randint(0, 0xFFFFFF)

        draw.line(((n1x, n1y), (n1x, n2y)), fill=color, width=1)
        draw.line(((n1x, n2y), (n2x, n2y)), fill=color, width=1)
        draw.line(((n1x, n1y), (n2x, n2y)), fill='white', width=1)

    boards(draw)
    del draw
    image.save('%s.png' % n)

'''
sconns = OrderedDict(sorted(conns.items()))

for i in islice(sconns, 24, 26):
    n1x, n1y, n2x, n2y = conns[i]
    print conns[i]

    color = '#%06x' % random.randint(0, 0xFFFFFF)

    draw.line(((n1x, n1y), (n1x, n2y)), fill=color, width=1)
    draw.line(((n1x, n2y), (n2x, n2y)), fill=color, width=1)
    draw.line(((n1x, n1y), (n2x, n2y)), fill='white', width=1)

    del draw
    image.show()
    image.save('test.png')
'''



# from pprint import pprint as p
# p(mem)
# p(mcu)
