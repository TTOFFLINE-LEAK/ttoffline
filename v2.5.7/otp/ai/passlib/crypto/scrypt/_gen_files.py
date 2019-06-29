import os
_SALSA_OPS = [
 (4, 0, 12, 7),
 (8, 4, 0, 9),
 (12, 8, 4, 13),
 (0, 12, 8, 18),
 (9, 5, 1, 7),
 (13, 9, 5, 9),
 (1, 13, 9, 13),
 (5, 1, 13, 18),
 (14, 10, 6, 7),
 (2, 14, 10, 9),
 (6, 2, 14, 13),
 (10, 6, 2, 18),
 (3, 15, 11, 7),
 (7, 3, 15, 9),
 (11, 7, 3, 13),
 (15, 11, 7, 18),
 (1, 0, 3, 7),
 (2, 1, 0, 9),
 (3, 2, 1, 13),
 (0, 3, 2, 18),
 (6, 5, 4, 7),
 (7, 6, 5, 9),
 (4, 7, 6, 13),
 (5, 4, 7, 18),
 (11, 10, 9, 7),
 (8, 11, 10, 9),
 (9, 8, 11, 13),
 (10, 9, 8, 18),
 (12, 15, 14, 7),
 (13, 12, 15, 9),
 (14, 13, 12, 13),
 (15, 14, 13, 18)]

def main():
    target = os.path.join(os.path.dirname(__file__), '_salsa.py')
    fh = file(target, 'w')
    write = fh.write
    VNAMES = [ 'v%d' % i for i in range(16) ]
    PAD = '    '
    PAD2 = '        '
    PAD3 = '            '
    TLIST = (', ').join('b%d' % i for i in range(16))
    VLIST = (', ').join(VNAMES)
    kwds = dict(VLIST=VLIST, TLIST=TLIST)
    write('"""passlib.utils.scrypt._salsa - salsa 20/8 core, autogenerated by _gen_salsa.py"""\n#=================================================================\n# salsa function\n#=================================================================\n\ndef salsa20(input):\n    """apply the salsa20/8 core to the provided input\n\n    :args input: input list containing 16 32-bit integers\n    :returns: result list containing 16 32-bit integers\n    """\n\n    %(TLIST)s = input\n    %(VLIST)s = \\\n        %(TLIST)s\n\n    i = 0\n    while i < 4:\n' % kwds)
    for idx, (target, source1, source2, rotate) in enumerate(_SALSA_OPS):
        write('        # salsa op %(idx)d: [%(it)d] ^= ([%(is1)d]+[%(is2)d])<<<%(rot1)d\n        t = (%(src1)s + %(src2)s) & 0xffffffff\n        %(dst)s ^= ((t & 0x%(rmask)08x) << %(rot1)d) | (t >> %(rot2)d)\n\n' % dict(idx=idx, is1=source1, is2=source2, it=target, src1=VNAMES[source1], src2=VNAMES[source2], dst=VNAMES[target], rmask=(1 << 32 - rotate) - 1, rot1=rotate, rot2=32 - rotate))

    write('        i += 1\n\n')
    for idx in range(16):
        write(PAD + 'b%d = (b%d + v%d) & 0xffffffff\n' % (idx, idx, idx))

    write('\n    return %(TLIST)s\n\n#=================================================================\n# eof\n#=================================================================\n' % kwds)


if __name__ == '__main__':
    main()