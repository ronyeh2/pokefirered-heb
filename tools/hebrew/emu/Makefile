# Headless mGBA runner used to check Hebrew layout on screen.
#
# Point it at an mGBA checkout you have built (the reliable option):
#
#   git clone --depth 1 -b 0.10.5 https://github.com/mgba-emu/mgba
#   cmake -S mgba -B mgba/build -DBUILD_QT=OFF -DBUILD_SDL=OFF && make -C mgba/build -j
#   make -C tools/hebrew/emu MGBA=/path/to/mgba
#
# Or against a packaged libmgba:
#
#   make -C tools/hebrew/emu MGBA_PREFIX=/opt/homebrew
#
# Homebrew's libmgba records an ABSOLUTE path to ffmpeg's libavcodec, so it
# stops loading the moment Homebrew bumps ffmpeg to a new soname -- you get
# "Library not loaded: .../libavcodec.62.dylib" and no rpath can override it.
# If that happens, build mGBA from source as above; the source build needs no
# ffmpeg at all with BUILD_QT and BUILD_SDL off.

ifdef MGBA
CFLAGS  ?= -O2 -I$(MGBA)/include -I$(MGBA)/build/include
LDFLAGS ?= -L$(MGBA)/build -Wl,-rpath,$(MGBA)/build
else
MGBA_PREFIX ?= /opt/homebrew
CFLAGS  ?= -O2 -I$(MGBA_PREFIX)/include
LDFLAGS ?= -L$(MGBA_PREFIX)/lib
endif
LDLIBS ?= -lmgba

all: runner crosscore

runner: runner.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

# Self-contained: declares the libretro structs it needs and dlopen()s the core,
# so it builds with no headers and no libmgba.
crosscore: crosscore.c
	$(CC) -O2 -o $@ $<

clean:
	rm -f runner crosscore

.PHONY: all clean
