# RetroArch state -> the raw libretro blob the core serialized.
# Outer container is RZIP (zlib chunks); inside it is RASTATE, a tagged
# container whose "MEM " block is what retro_unserialize wants.
import sys, struct, zlib
d = open(sys.argv[1], 'rb').read()
if d[:6] == b'#RZIPv':
    total, out, off = struct.unpack_from('<Q', d, 12)[0], bytearray(), 20
    while off < len(d) and len(out) < total:
        n = struct.unpack_from('<I', d, off)[0]; off += 4
        if n == 0: break
        out += zlib.decompress(bytes(d[off:off+n])); off += n
    d = bytes(out)
if d[:7] == b'RASTATE':
    off = 8
    while off + 8 <= len(d):
        tag, size = d[off:off+4], struct.unpack_from('<i', d, off+4)[0]
        if tag == b'MEM ':
            d = d[off+8:off+8+size]; break
        if tag == b'END ' or size <= 0: break
        off += 8 + size
open(sys.argv[2], 'wb').write(d)
print("%s -> %d bytes" % (sys.argv[1].split('/')[-1], len(d)))
