# LIB_MAP: notes for Claude Code

Read `README.md`. Keep handlers pure. Grids: "1" wall, "0" open.
Compile-check (`~/projects/LIB_MCP/tools/lcmcp compile livecode/lib_map.livecodescript`),
lint (`lcmcp lint ...`) and run `python3 tests/run_tests.py` after every change. Add a
test with every new handler; take expected answers from LiveCode when unsure.
Every loop that searches (pathfinding, flood fills) needs a step limit: a hang freezes the
LIB_MCP standalone (recover: `taskkill.exe /IM xt3d_MCP.exe /F`, delete
`C:\LIB_MCP\devtoken_8767.txt`).
Used by xt3d (3D, y up) and Vibecode3D (+Y down): keep output engine-neutral.
