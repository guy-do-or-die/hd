from PIL import Image, ImageDraw, ImageOps

from collections import OrderedDict
from itertools import islice
from functools import partial

import operator as op
import random

XS, Y0 = 800, 800


def read_boards():
    mcu, mem = {}, {}

    for rline in iter(raw_input, '====='):
        line = rline.split(';')

        pin, t, xy = (int(line[0]), int(line[1]),
                      tuple([180 + float(a.replace(',', '.')) * 30 for a in line[2:]]))

        if t == 1:
            mcu[pin] = xy
        else:
            mem[pin] = xy

    return mcu, mem


def read_conns(mcu, mem):
    conns = {}

    for i, rline in enumerate(iter(raw_input, '#####')):
        line = rline.split(';')
        n1, n2 = map(int, line)

        n1x, n1y = mcu[n1]
        n2x, n2y = mem[n2]

        c1 = n1x - n2x
        c2 = n1y - n2y

        conns[c1 * c2] = (n1x, n1y, n2x, n2y)

        if i > 100:
            break

    return conns


def overlap(conn1, conn2):
    deltas = [op.sub(*p) for p in zip(conn1, conn2)]
    xs, ys = deltas[::2], deltas[1::2]
    return not (all(t >= 0 for t in xs) and all(t <= 0 for t in ys)
                or all(t <= 0 for t in xs) and all(t >= 0 for t in ys))


def group_conns(conns):
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

    return groups


def draw_boards(drw, mcu, mem):
    for xy in mcu.values():
        x, y = xy
        drw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='red', outline='red')

    for xy in mem.values():
        x, y = xy
        drw.ellipse(((x - 2, y - 2), (x + 2, y + 2)), fill='blue', outline='blue')


def draw_conn(drw, conn):
    n1x, n1y, n2x, n2y = conn
    color = '#%06x' % random.randint(0, 0xFFFFFF)

    drw.line(((n1x, n1y), (n1x, n2y)), fill=color, width=1)
    drw.line(((n1x, n2y), (n2x, n2y)), fill=color, width=1)
    drw.line(((n1x, n1y), (n2x, n2y)), fill='white', width=1)


def draw_groups(groups, mcu, mem):
    for n, group in enumerate(groups):
        img = Image.new('RGBA', (XS, Y0), (0, 0, 0, 255))
        drw = ImageDraw.Draw(img)

        draw_boards(drw, mcu, mem)
        for conn in group:
            draw_conn(drw, conn)

        img = ImageOps.flip(img)
        img.save('%s.png' % n)
        del drw


def main():
    mcu, mem = read_boards()
    conns = read_conns(mcu, mem)
    groups = group_conns(conns)
    draw_groups(groups, mcu, mem)

    sconns = OrderedDict(sorted(conns.items()))

    img = Image.new('RGBA', (XS, Y0), (0, 0, 0, 255))
    drw = ImageDraw.Draw(img)

    draw_boards(drw, mcu, mem)
    for f in islice(sconns, 100):
        draw_conn(drw, conns[f])

    img = ImageOps.flip(img)
    img.show()
    img.save('test.png')
    del drw


if __name__ == '__main__':
    main()
