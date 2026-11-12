#!/usr/bin/env python3
"""Run LIB_MAP's tests inside real LiveCode 9.6.3, through LIB_MCP's standalone server.

    python3 tests/run_tests.py

Each test is LiveCode statements run in the server after loading the library; the text
they put into the message box is compared with the expected answer. Needs ~/projects/LIB_MCP.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), 'livecode', 'lib_map.livecodescript')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'LIB_MCP', 'python'))
from lib_mcp.client import Client, local_to_win

SETUP = '''put "1111" & return & "1000" & return & "1010" & return & "1111" into xtS["a"]
put "1111" & return & "0001" & return & "0101" & return & "1111" into xtS["b"]
put "1111" & return & "0001" & return & "1011" & return & "1111" into xtS["c"]
put Map.Stitch(xtS, "a b") into xtW
'''
TESTS = [
    ('stitch two sections', 'put Map.Stitch(xtS, "a b")', '11111111\n10000001\n10100101\n11111111'),
    ('stitch with a solid section', 'put line 2 of Map.Stitch(xtS, "a -")', '10001111'),
    ('stitch two rows', 'put the number of lines of Map.Stitch(xtS, "a b" & return & "b a")', '8'),
    ('stitch unknown name', 'put Map.Stitch(xtS, "a z")', 'ERROR: no section named z'),
    ('seam, 2 doorways', 'put Map.Seams(xtS, "a b")', '1,1,east,2,'),
    ('seam, mismatch at row 3', 'put Map.Seams(xtS, "a c")', '1,1,east,1,3'),
    ('seams in a 2x2 layout', 'put Map.Seams(xtS, "a b" & return & "b a")',
     '1,1,east,2,\n1,1,south,0,\n2,1,south,0,\n1,2,east,0,'),
    ('path, 4 directions', 'put Map.FindPath(xtW, "2,2", "7,3", false)', '2,2\n3,2\n4,2\n5,2\n6,2\n7,2\n7,3'),
    ('path, 8 directions, no corner cutting', 'put Map.FindPath(xtW, "2,2", "7,3", true)', '2,2\n3,2\n4,2\n5,2\n6,2\n7,2\n7,3'),
    ('path, diagonal where allowed', 'put Map.FindPath("000" & return & "000" & return & "000", "1,1", "3,3", true)', '1,1\n2,2\n3,3'),
    ('path into a wall', 'put "[" & Map.FindPath(xtW, "2,2", "1,1", false) & "]"', '[]'),
    ('path, walled off', 'put "[" & Map.FindPath("010", "1,1", "3,1", false) & "]"', '[]'),
    ('path to itself', 'put Map.FindPath(xtW, "2,2", "2,2", false)', '2,2'),
    ('pieces count', 'put the number of lines of Map.Pieces(xtW)', '40'),
    ('pieces of one open cell', 'put Map.Pieces("0")', '1,1,floor\n1,1,roof\n1,1,north\n1,1,south\n1,1,east\n1,1,west'),
    ('regions', 'put Map.Regions(xtW)', '1,2,2,7,2\n2,2,3,2,3\n3,4,3,5,3\n4,7,3,7,3'),
    ('region links', 'put Map.RegionLinks(xtW, Map.Regions(xtW))', '1,2\n1,3\n1,4'),
    ('mesh triangle count', 'put Map.MeshText(xtW, 1, 1) into xtM\nput xtM["triangles"] && the number of lines of xtM["vertices"]', '60 180'),
    ('mesh with roofs', 'put Map.MeshText(xtW, 1, 1, true) into xtM\nput xtM["triangles"]', '80'),
    ('floor faces up', 'put Map.MeshText("0", 2, 3) into xtM\nput line 1 to 3 of xtM["vertices"]', '0,0,0\n2,0,2\n2,0,0'),
]


def main():
    c = Client.standalone()
    path = local_to_win(LIB).replace('\\', '/')
    ok, out = c.run('if there is a stack "LIB_MAP" then delete stack "LIB_MAP"\n'
                    'start using stack "%s"\nput "loaded"' % path, in_server=True)
    if not ok or 'loaded' not in out:
        print('Could not load LIB_MAP:', out)
        return 2
    failed = 0
    for name, code, want in TESTS:
        ok, got = c.run(SETUP + code, in_server=True)
        got = got.replace('\r', '')
        good = got == want   # answers that start with "ERROR:" come back as a failed request on purpose
        failed += not good
        print('%s  %s' % ('PASS' if good else 'FAIL', name if good else '%s\n      want %r\n      got  %r' % (name, want, got)))
    print('\n%d of %d passed' % (len(TESTS) - failed, len(TESTS)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
