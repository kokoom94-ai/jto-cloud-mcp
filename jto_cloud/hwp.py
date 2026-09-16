"""Narrow HWP5 template editor. Keeps original OLE directory and style records."""
from io import BytesIO
from pathlib import Path
import struct
import zlib
import olefile

FREE, END, FAT = 0xffffffff, 0xfffffffe, 0xfffffffd


def records(data):
    out, pos = [], 0
    while pos < len(data):
        header, = struct.unpack_from('<I', data, pos)
        pos += 4
        tag, level, size = header & 1023, (header >> 10) & 1023, header >> 20
        if size == 4095:
            size, = struct.unpack_from('<I', data, pos)
            pos += 4
        if pos + size > len(data):
            raise ValueError('HWP record is truncated')
        out.append((tag, level, data[pos:pos+size]))
        pos += size
    return out


def encode_records(items):
    out = bytearray()
    for tag, level, data in items:
        size = len(data)
        out.extend(struct.pack('<I', tag | level << 10 | min(size, 4095) << 20))
        if size >= 4095:
            out.extend(struct.pack('<I', size))
        out.extend(data)
    return bytes(out)


def rewrite_ole(source, changes):
    """Repack unchanged directory tree and all streams, including growing mini streams."""
    with olefile.OleFileIO(source) as ole:
        if ole.sectorsize != 512:
            raise ValueError('Only supplied version-3 CFB template is supported')
        directory = bytearray(ole.directory_fp.getvalue())
        streams = []
        for path in ole.listdir():
            sid = ole._find(path)
            streams.append((sid, changes.get('/'.join(path), ole.openstream(path).read())))
        header = bytearray(Path(source).read_bytes()[:512])
    sectors, fat, mini, minifat = [], [], bytearray(), []

    def allocate(data):
        if not data:
            return END
        start = len(sectors)
        for offset in range(0, len(data), 512):
            sectors.append(data[offset:offset+512].ljust(512, b'\0'))
            fat.append(len(sectors))
        fat[-1] = END
        return start

    for sid, data in streams:
        if 0 < len(data) < 4096:
            start = len(minifat)
            for offset in range(0, len(data), 64):
                mini.extend(data[offset:offset+64].ljust(64, b'\0'))
                minifat.append(len(minifat)+1)
            minifat[-1] = END
        else:
            start = allocate(data)
        struct.pack_into('<IQ', directory, sid*128+116, start, len(data))
    root_start = allocate(mini)
    struct.pack_into('<IQ', directory, 116, root_start, len(mini))
    mini_bytes = b''.join(struct.pack('<I', n) for n in minifat)
    mini_bytes = mini_bytes.ljust((len(mini_bytes)+511)//512*512, b'\xff')
    mini_start = allocate(mini_bytes)
    dir_start = allocate(directory)
    count = 1
    while count*128 < len(sectors)+count:
        count += 1
    if count > 109:
        raise ValueError('Template output exceeds CFB allocation limit')
    fat_ids = list(range(len(sectors), len(sectors)+count))
    fat.extend([FAT]*count)
    fat_data = b''.join(struct.pack('<I', n) for n in fat).ljust(count*512, b'\xff')
    sectors.extend(fat_data[i:i+512] for i in range(0, len(fat_data), 512))
    struct.pack_into('<II', header, 40, 0, count)
    struct.pack_into('<I', header, 48, dir_start)
    struct.pack_into('<IIII', header, 60, mini_start, len(mini_bytes)//512, END, 0)
    header[76:512] = b''.join(struct.pack('<I', n) for n in fat_ids).ljust(436, b'\xff')
    return bytes(header) + b''.join(sectors)


def paragraph(prototype, text, last=False):
    text_bytes = (text+'\r').encode('utf-16le')
    out = []
    for tag, level, raw in prototype:
        data = bytearray(raw)
        if tag == 66:
            struct.pack_into('<I', data, 0, len(text_bytes)//2 | (0x80000000 if last else 0))
            struct.pack_into('<H', data, 12, 1)  # one character style run
            struct.pack_into('<H', data, 14, 0)  # no range tags
            struct.pack_into('<H', data, 16, 0)  # discard stale layout cache
        elif tag == 67:
            data = text_bytes
        elif tag == 68:
            data = struct.pack('<II', 0, struct.unpack_from('<I', raw, len(raw)-4)[0])
        elif tag in (69, 70):
            continue
        out.append((tag, level, bytes(data)))
    return out


def generate_onepage(template, target, content):
    with olefile.OleFileIO(template) as ole:
        flags, = struct.unpack_from('<I', ole.openstream('FileHeader').read(), 36)
        if flags & 2 or not flags & 1:
            raise ValueError('Unexpected HWP compression/encryption flags')
        items = records(zlib.decompress(ole.openstream('BodyText/Section0').read(), -15))
    # Known, hash-checked original: preserve header/title/summary boxes and page setup.
    replacements = {
        15: (19, content['metadata']),
        22: (26, content['title']),
        26: (30, content.get('subtitle') or '업무 보고'),
        40: (44, content['summary'][0]),
        44: (48, content['summary'][1]),
    }
    out, i = [], 0
    while i < 51:
        if i in replacements:
            end, text = replacements[i]
            out.extend(paragraph(items[i:end], text, i in (15, 26, 44)))
            i = end
        else:
            out.append(items[i]); i += 1
    for n, section in enumerate(content['sections'], 1):
        out.extend(paragraph(items[51:55], f" {n}. {section['heading']}"))
        for bullet in section['bullets']:
            out.extend(paragraph(items[58:62], ' □ '+bullet))
    out.extend(paragraph(items[87:91], ' ※ '+content['note'], True))
    # All cached paragraph positions refer to the blank form.
    cleaned = []
    for tag, level, raw in out:
        if tag == 69:
            continue
        if tag == 66:
            raw = bytearray(raw)
            struct.pack_into('<H', raw, 16, 0)
            raw = bytes(raw)
        cleaned.append((tag, level, raw))
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    body = compressor.compress(encode_records(cleaned)) + compressor.flush()
    preview = '\r\n'.join([content['title'], *content['summary']] +
                          [s['heading']+': '+' / '.join(s['bullets']) for s in content['sections']])
    # A valid blank PNG replaces the misleading original-form thumbnail.
    import base64
    blank = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
    result = rewrite_ole(template, {'BodyText/Section0':body, 'PrvText':preview.encode('utf-16le'), 'PrvImage':blank})
    Path(target).write_bytes(result)
    with olefile.OleFileIO(BytesIO(result)) as ole:
        check = records(zlib.decompress(ole.openstream('BodyText/Section0').read(), -15))
        if not any(content['title'].encode('utf-16le') in d for t,l,d in check if t == 67):
            raise ValueError('HWP roundtrip validation failed')
    return {'valid':True, 'visual_verified':False, 'page_count_verified':False,
            'warnings':['원본 서식 보존·내용량 제한 적용. 한글에서 실제 1쪽 여부와 줄바꿈 확인 필요.']}
