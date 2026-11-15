#!/usr/bin/env python3
"""hexgrid.py - a flat-top hex grid layout with a check that tiles meet edge to edge
(LIB_MAP; written for the owner's Hexes_but_bad_Offsets stack, see docs/HEX_OFFSETS.md).

    python3 -I python/hexgrid.py            run the checks (exit 1 on any fault)
    python3 -I python/hexgrid.py --help     this text

Flat-top hexes of side s (the owner's drawHex: corners at cx +/- s on the centre line):
  width 2s, height sqrt(3) s.
Layout "odd-q": columns are 1.5 s apart; every odd column is pushed down half a hex
(sqrt(3)/2 s); rows are sqrt(3) s apart.
    centre(col, row) = (col * 1.5 s,  row * sqrt(3) s + (col odd ? sqrt(3)/2 s : 0))
A picture that repeats (a card's backgroundPattern) must be 3 s wide and sqrt(3) s tall and
hold one whole hex plus the four quarter hexes at its corners: tile_hexes(s) gives their
centres (the tile's own rectangle clips them).

The check: in a grid of hexes, each hex has 6 neighbours, each neighbour shares exactly one
whole edge with it (two corners in the same place), and no two hexes overlap (centres at least
sqrt(3) s apart). check_layout() runs that on any centre function, so a broken offset is
caught: it is run below on the old stack's paintTarget layout too, which fails.
"""
import math, sys

R3 = math.sqrt(3)


def corners(cx, cy, s):
    """the six corners, in the owner's drawHex order (left, upper left, upper right, right, ...)"""
    h = R3 / 2 * s
    return [(cx - s, cy), (cx - s / 2, cy - h), (cx + s / 2, cy - h),
            (cx + s, cy), (cx + s / 2, cy + h), (cx - s / 2, cy + h)]


def centre(col, row, s):
    """odd-q flat-top layout"""
    return (col * 1.5 * s, row * R3 * s + (R3 / 2 * s if col % 2 else 0))


def neighbours(col, row):
    """the 6 neighbours of a cell in the odd-q layout"""
    if col % 2:
        d = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
    else:
        d = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]
    return [(col + a, row + b) for a, b in d]


def tile_hexes(s):
    """(width, height, centres) of the smallest picture that repeats into the grid"""
    w, h = 3 * s, R3 * s
    return w, h, [(1.5 * s, h / 2), (0, 0), (w, 0), (0, h), (w, h)]


def old_paint_target(col, row, s):
    """the stack's paintTarget loop as written: dx = 1.5 s, dy = sqrt(3)/2 s, odd ROWS shifted 0.75 s"""
    x = col * 1.5 * s + (s * 0.75 if row % 2 else 0)
    return (x, row * R3 / 2 * s)


def fixed_paint_target(col, row, s):
    """the same loop shape (rows sqrt(3)/2 s apart, odd rows shifted), with the right numbers:
    columns 3 s apart and odd rows shifted 1.5 s"""
    x = col * 3 * s + (1.5 * s if row % 2 else 0)
    return (x, row * R3 / 2 * s)


def _key(p, eps=1e-6):
    return (round(p[0] / eps), round(p[1] / eps))


def check_layout(centre_fn, s=40.0, cols=8, rows=8):
    """faults (a list of text lines; empty = the layout tiles edge to edge)"""
    faults = []
    pts = {(c, r): centre_fn(c, r, s) for c in range(cols) for r in range(rows)}
    # 1. no overlaps: centres at least sqrt(3) s apart
    items = list(pts.items())
    for i, (a, pa) in enumerate(items):
        for b, pb in items[i + 1:]:
            d = math.dist(pa, pb)
            if d < R3 * s - 1e-6:
                faults.append('hexes %s and %s overlap (centres %.1f apart, need %.1f)' % (a, b, d, R3 * s))
                if len(faults) > 5:
                    return faults
    # 2. inner hexes: exactly 6 hexes at distance sqrt(3) s, each sharing one whole edge
    for (c, r), p in pts.items():
        if not (1 < c < cols - 2 and 1 < r < rows - 2):
            continue
        mine = {_key(q) for q in corners(p[0], p[1], s)}
        touching = 0
        for other, q in pts.items():
            if other == (c, r) or abs(math.dist(p, q) - R3 * s) > 1e-6:
                continue
            shared = mine & {_key(k) for k in corners(q[0], q[1], s)}
            if len(shared) == 2:
                touching += 1
            else:
                faults.append('hexes %s and %s are neighbours but share %d corners, not an edge' % ((c, r), other, len(shared)))
        if touching != 6:
            faults.append('hex %s meets %d hexes edge to edge, not 6 (gaps around it)' % ((c, r), touching))
        if len(faults) > 5:
            break
    return faults


def check_tile(s=40.0):
    """the repeating picture: every hex of a 6 x 6 grid is a tile hex moved by whole tiles"""
    w, h, cs = tile_hexes(s)
    tiled = {_key((x + i * w, y + j * h)) for x, y in cs for i in range(-1, 8) for j in range(-1, 8)}
    return ['hex %s is not in the repeated tile' % ((c, r),)
            for c in range(6) for r in range(6) if _key(centre(c, r, s)) not in tiled]


def main(argv):
    if any(a in ('-h', '--help') for a in argv):
        print(__doc__)
        return 0
    results = [('odd-q layout (centre)', check_layout(centre), True),
               ('fixed paintTarget (3 s columns, odd rows +1.5 s)', check_layout(fixed_paint_target), True),
               ('repeating tile 3 s x sqrt(3) s', check_tile(), True),
               ('neighbours() matches the layout', [] if all(
                   abs(math.dist(centre(c, r, 1), centre(*n, 1)) - R3) < 1e-9
                   for c in range(2, 6) for r in range(2, 6) for n in neighbours(c, r)) else ['a neighbour is not adjacent'], True),
               ('the old paintTarget (must FAIL)', check_layout(old_paint_target), False)]
    bad = 0
    for name, faults, should_pass in results:
        ok = (not faults) == should_pass
        bad += not ok
        print('%s  %s%s' % ('ok  ' if ok else 'FAIL', name, '' if not faults else ': ' + faults[0]))
    print('\n%d of %d checks as expected' % (len(results) - bad, len(results)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
