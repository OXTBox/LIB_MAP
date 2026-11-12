# LIB_MAP

Levels from 1-bit grids, for xt3d and Vibecode3D alike: lace 16x16 (or any size) sprites
into a world, check that neighbouring sections join up, list floors and walls, find
paths for AI, merge open space into navigation regions, and build 3D mesh data.
Pure LiveCode handlers: data in, data out; each engine draws the result its own way.

Grids are LIB_BIT's format: one line per row, **`1` = wall, `0` = open floor**
(`Bit.Invert` flips a sprite drawn the other way). Cells are `col,row`, 1-based; rows
grow southward, columns eastward.

```
start using stack "<path>/LIB_MAP/livecode/lib_map.livecodescript"
put tGrid1 into tSections["hall"]
put tGrid2 into tSections["room"]
put Map.Stitch(tSections, "hall room hall" & return & "room - room") into tWorld
put Map.FindPath(tWorld, "2,2", "40,20", true) into tPath      -- one col,row per line
put Map.MeshText(tWorld, 1, 1) into tMesh                     -- for xt3d
put xt3d_MeshFromText(tMesh["vertices"], "", "") into tMeshHandle
```

| Handler | Gives |
|---|---|
| `Map.Stitch(sections, layout)` | the world grid; layout = lines of section names, `-` = solid |
| `Map.Seams(sections, layout)` | per seam: `col,row,east/south,doorways,mismatches` (doorways 0 = not connected) |
| `Map.Pieces(world)` | `col,row,floor/roof/north/south/east/west` per open cell |
| `Map.IsOpen(world, col, row)` | true for open cells inside the world |
| `Map.Blocks(grid)` | the other way round: raised blocks for filled cells, `col,row,top/north/south/east/west` (sprites made solid, relief pictures) |
| `Map.IsFilled(grid, col, row)` | true for filled cells inside the grid |
| `Map.FindPath(world, from, to [, diagonal])` | A* path, one `col,row` per line; empty if none. Diagonals never cut wall corners. |
| `Map.Regions(world)` | open space as rectangles `id,left,top,right,bottom` |
| `Map.RegionLinks(world, regions)` | touching region pairs `a,b` (a navigation graph) |
| `Map.MeshText(world, cell, height [, roof])` | array: `["vertices"]` triangles as `x,y,z` lines (y up, z south), `["triangles"]` count. Walls face into open space, so back-face culling shows the inside. |

## Tests

`python3 tests/run_tests.py`: 20 checks in real LiveCode 9.6.3 through LIB_MCP. All pass.

## Next

Section-level path caching for big worlds (plan section to section, then inside one),
doorway-aware seams, texture coordinates for the mesh, and the two showcases: an xt3d
level with an AI walking it, and the same level in Vibecode3D.

`Map.Pieces` replaces the tracer's `textToMap` (formerly `Trace.GridToMap`).
Part of the family of separate libraries listed in `~/projects/LIB_MCP/README.md`.
