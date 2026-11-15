# Hexes_but_bad_Offsets: what is wrong, and the fix

Sunday, November 15, 2026. Claude (Opus 5.5), from the harvest
`XTJSON/batch/Hexes_but_bad_Offsets/scripts/` (404 lines; the hex code is in button 1006).
Checked in Python: `python3 -I python/hexgrid.py` (no LiveCode needed).

The hexes are flat-top, side `s`: 2s wide, sqrt(3)·s tall (drawHex's corners are right).
The spacing is what goes wrong, in three places.

## 1. The background tile is the wrong size (generateHexTile)
The tile is `1.5 s` wide and `sqrt(3) s` tall, with one hex in it. A hex is `2 s` wide, so its
left and right corners are cut off, and repeating one hex in a rectangle only ever makes a
square grid: hexes never fit into each other's notches.

**Fix:** the smallest picture that repeats into a hex grid is **3 s wide and sqrt(3) s tall**
and holds one whole hex in the middle (centre 1.5 s, sqrt(3)/2 s) plus a quarter hex at each
corner (centres at the tile's four corners). Draw those five hexes, clipped to the tile, then
export the snapshot. `hexgrid.tile_hexes(s)` gives the numbers.

## 2. The row offset is half what it must be (paintTarget)
The loop puts rows `sqrt(3)/2 s` apart (half a hex: right for this loop shape), columns
`1.5 s` apart and shifts odd rows by `0.75 s`. With rows that close, hexes in the same column
of neighbouring rows overlap (centres 0.87 s apart where 1.73 s is the least). The check
reports exactly that.

**Fix (keep the loop, change two numbers):**
```
put (3 * s) into dx                       -- was 3/2 * s
put (sqrt(3)/2 * s) into dy               -- unchanged
...
if (row mod 2) = 1 then add (1.5 * s) to x   -- was s * 0.75
```
Or the usual form: columns `1.5 s` apart, rows `sqrt(3) s` apart, odd **columns** pushed down
`sqrt(3)/2 s` (`hexgrid.centre`).

## 3. A typo moves the group only sideways (generateHexTile)
```
add tOffset to item 2 of tHextRect     -- tHextRect, not tHexRect
add tOffset to item 4 of tHextRect
```
`tHextRect` is a new, empty variable, so only left and right get the -3: the snapshot is
shifted 3 pixels left but not up, and the 1-pixel outline is clipped on one side. Use
`tHexRect` for all four, or better, drop the offset and make the tile from the corner hexes
as in 1 (the edges then meet across tiles by construction).

## Smaller things
- The angle scrollbar (1115) rotates the hex, then uses half its width for both directions;
  a rotated hex no longer tiles in this rectangle anyway, so rotating should rotate the whole
  grid (or the tile) instead.
- resizeStack sets a widget "hexCanvas" while paintTarget measures widget "Browser".

## For LIB_MAP
`python/hexgrid.py`: the layout (`centre`, `neighbours`, `corners`, `tile_hexes`) and the
check (`check_layout`: no overlaps, every inner hex meets 6 hexes edge to edge, two shared
corners each). The old paintTarget numbers are kept in it as a case that must fail. A LiveCode
`Map.Hex*` set can follow the same formulas when a game needs one (not written yet: the
LiveCode tests run through LIB_MCP, which is off limits today).
