// Headless GBA runner: boots a ROM with a battery save, steps frames with a
// key mask, dumps the framebuffer, and peeks/pokes RAM. Drives the layout
// checks described in tools/hebrew/emu/README.md.
// argv: runner <rom> <outdir> [save.sav]
// stdin script:
//   <frames> <keys>      e.g. "60 A", "300 -"
//   shot <name>          dump framebuffer
//   read <hexaddr> <len> hex-dump RAM to stderr
//   w8|w16|w32 <hexaddr> <hexval>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/serialize.h>
#include <mgba/core/interface.h>
#include <mgba/internal/gba/input.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t parseKeys(const char* s) {
    uint32_t k = 0;
    if (strchr(s, 'A') && !strstr(s, "START") && !strstr(s, "SELECT")) k |= 1 << GBA_KEY_A;
    if (strstr(s, "START"))  k |= 1 << GBA_KEY_START;
    if (strstr(s, "SELECT")) k |= 1 << GBA_KEY_SELECT;
    if (strstr(s, "UP"))     k |= 1 << GBA_KEY_UP;
    if (strstr(s, "DOWN"))   k |= 1 << GBA_KEY_DOWN;
    if (strstr(s, "LEFT"))   k |= 1 << GBA_KEY_LEFT;
    if (strstr(s, "RIGHT"))  k |= 1 << GBA_KEY_RIGHT;
    if (strstr(s, "Lb"))     k |= 1 << GBA_KEY_L;
    if (strstr(s, "Rb"))     k |= 1 << GBA_KEY_R;
    if (strstr(s, "B") && !strstr(s, "Lb") && !strstr(s, "Rb")) k |= 1 << GBA_KEY_B;
    return k;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: runner2 <rom> <outdir> [save.sav]\n"); return 2; }
    const char* rom = argv[1];
    const char* outdir = argv[2];
    const char* savePath = argc > 3 ? argv[3] : NULL;

    struct mCore* core = mCoreFind(rom);
    if (!core) { fprintf(stderr, "FAIL: mCoreFind\n"); return 1; }
    if (!core->init(core)) { fprintf(stderr, "FAIL: core init\n"); return 1; }
    mCoreInitConfig(core, NULL);

    unsigned w, h;
    core->desiredVideoDimensions(core, &w, &h);
    color_t* fb = calloc(w * h, BYTES_PER_PIXEL);
    core->setVideoBuffer(core, fb, w);

    if (!mCoreLoadFile(core, rom)) { fprintf(stderr, "FAIL: load ROM\n"); return 1; }

    if (savePath) {
        struct VFile* sv = VFileOpen(savePath, O_RDWR);
        if (!sv) { fprintf(stderr, "FAIL: open save %s\n", savePath); return 1; }
        if (!core->loadSave(core, sv)) { fprintf(stderr, "FAIL: loadSave\n"); return 1; }
        fprintf(stderr, "OK: save loaded (%s)\n", savePath);
    }

    core->reset(core);
    fprintf(stderr, "OK: booted %ux%u\n", w, h);

    char line[512];
    long total = 0;
    while (fgets(line, sizeof line, stdin)) {
        char a[64] = {0}, b[128] = {0}, c[64] = {0};
        int n = sscanf(line, "%63s %127s %63s", a, b, c);
        if (n < 1) continue;
        if (!strcmp(a, "shot")) {
            char path[512];
            snprintf(path, sizeof path, "%s/%s.raw", outdir, b[0] ? b : "shot");
            FILE* f = fopen(path, "wb");
            if (!f) { fprintf(stderr, "FAIL: open %s\n", path); return 1; }
            fwrite(&w, 4, 1, f); fwrite(&h, 4, 1, f);
            fwrite(fb, BYTES_PER_PIXEL, (size_t)w * h, f);
            fclose(f);
            fprintf(stderr, "shot %s @%ld\n", b, total);
            continue;
        }
        if (!strcmp(a, "ss") || !strcmp(a, "sl")) {
            struct VFile* st = VFileOpen(b, !strcmp(a, "ss") ? (O_RDWR|O_CREAT|O_TRUNC) : O_RDONLY);
            if (!st) { fprintf(stderr, "FAIL: state %s %s\n", a, b); return 1; }
            bool ok = !strcmp(a, "ss") ? mCoreSaveStateNamed(core, st, 0)
                                       : mCoreLoadStateNamed(core, st, 0);
            st->close(st);
            fprintf(stderr, "STATE %s %s %s\n", a, b, ok ? "ok" : "FAIL");
            continue;
        }
        if (!strcmp(a, "read")) {
            uint32_t addr = (uint32_t)strtoul(b, NULL, 16);
            int len = c[0] ? atoi(c) : 16;
            fprintf(stderr, "MEM %08X:", addr);
            for (int i = 0; i < len; i++) fprintf(stderr, " %02X", core->busRead8(core, addr + i));
            fprintf(stderr, "\n");
            continue;
        }
        if (!strcmp(a, "w8") || !strcmp(a, "w16") || !strcmp(a, "w32")) {
            uint32_t addr = (uint32_t)strtoul(b, NULL, 16);
            uint32_t val  = (uint32_t)strtoul(c, NULL, 16);
            if (!strcmp(a, "w8"))  core->busWrite8(core, addr, val & 0xFF);
            if (!strcmp(a, "w16")) core->busWrite16(core, addr, val & 0xFFFF);
            if (!strcmp(a, "w32")) core->busWrite32(core, addr, val);
            fprintf(stderr, "POKE %s %08X = %X\n", a, addr, val);
            continue;
        }
        long frames = atol(a);
        uint32_t keys = b[0] ? parseKeys(b) : 0;
        if (b[0] == '-') keys = 0;
        for (long i = 0; i < frames; i++) {
            core->setKeys(core, keys);
            core->runFrame(core);
            total++;
        }
    }
    fprintf(stderr, "OK: %ld frames\n", total);
    core->deinit(core);
    return 0;
}
