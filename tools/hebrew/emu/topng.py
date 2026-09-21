import sys,struct,zlib,os
def conv(raw,png,scale=2):
    d=open(raw,'rb').read()
    w,h=struct.unpack('<II',d[:8]); px=d[8:]
    rows=[]
    for y in range(h):
        for _ in range(scale):
            row=bytearray([0])
            for x in range(w):
                o=(y*w+x)*4
                b,g,r,a=px[o],px[o+1],px[o+2],px[o+3]
                row+= bytes([r,g,b])*scale
            rows.append(bytes(row))
    raw_img=b''.join(rows)
    def chunk(t,data):
        c=t+data
        return struct.pack('>I',len(data))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
    out=b'\x89PNG\r\n\x1a\n'
    out+=chunk(b'IHDR',struct.pack('>IIBBBBB',w*scale,h*scale,8,2,0,0,0))
    out+=chunk(b'IDAT',zlib.compress(raw_img,9))
    out+=chunk(b'IEND',b'')
    open(png,'wb').write(out)
    return w,h
for f in sys.argv[1:]:
    o=f[:-4]+'.png'
    print(conv(f,o), o)
