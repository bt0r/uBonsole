#!/bin/bash
# Installs the SDR tools used by the radio launcher (Debian trixie, arm64).
#   Debian packages: direwolf, satdump, qsstv, fldigi, js8call, welle.io, gpredict, gpsd-clients
#   Official packages: SDR++ (nightly .deb), WSJT-X and AIS-catcher (GitHub release .deb)
#   Built from source in ~/src: libacars, dumpvdl2, acarsdec, RTLSDR-Airband, radiosonde_auto_rx
# Log it with:  bash tools/install-sdr-tools.sh 2>&1 | tee ~/sdr-install.log
set -e
SRC=$HOME/src; mkdir -p "$SRC"

echo "=== Debian packages"
sudo apt-get update
sudo apt-get install -y direwolf satdump satdump-data rtl-sdr rtl-433 gqrx-sdr qsstv fldigi pipewire-bin \
  js8call welle.io gpredict gpsd-clients feh python3-pil \
  build-essential cmake git pkg-config libglib2.0-dev zlib1g-dev libxml2-dev libjansson-dev \
  libsqlite3-dev libzmq3-dev libconfig++-dev libsoapysdr-dev libsndfile1-dev libcjson-dev \
  libpaho-mqtt-dev librtlsdr-dev python3-venv python3-dev libusb-1.0-0-dev \
  libmp3lame-dev libshout3-dev libpulse-dev libfftw3-dev

echo "=== SDR++ (official trixie arm64 package)"
curl -fsSL -o /tmp/sdrpp.deb https://github.com/AlexandreRouma/SDRPlusPlus/releases/download/nightly/sdrpp_debian_trixie_aarch64.deb
sudo apt-get install -y /tmp/sdrpp.deb

echo "=== WSJT-X (official release, FT8 / FT4)"
WSJTX_VERSION=3.0.2
case $(dpkg --print-architecture) in arm64) WSJTX_ARCH=aarch64 ;; amd64) WSJTX_ARCH=x86_64 ;; *) WSJTX_ARCH=$(dpkg --print-architecture) ;; esac
curl -fsSL -o /tmp/wsjtx.deb "https://github.com/WSJTX/wsjtx/releases/download/v$WSJTX_VERSION/wsjtx-$WSJTX_VERSION-linux-$WSJTX_ARCH.deb"
sudo apt-get install -y /tmp/wsjtx.deb

echo "=== AIS-catcher (official release, ships)"
AISCATCHER_VERSION=0.70
case $(dpkg --print-architecture) in arm64) AIS_ARCH=arm64 ;; amd64) AIS_ARCH=amd64 ;; *) AIS_ARCH=$(dpkg --print-architecture) ;; esac
curl -fsSL -o /tmp/ais-catcher.deb "https://github.com/jvde-github/AIS-catcher/releases/download/v$AISCATCHER_VERSION/ais-catcher_debian_trixie_$AIS_ARCH.deb"
sudo apt-get install -y /tmp/ais-catcher.deb

echo "=== libacars"
cd "$SRC"; [ -d libacars ] || git clone --depth 1 https://github.com/szpajder/libacars.git
cd libacars && mkdir -p build && cd build && cmake .. && make -j3 && sudo make install && sudo ldconfig

echo "=== dumpvdl2 (VDL2)"
cd "$SRC"; [ -d dumpvdl2 ] || git clone --depth 1 https://github.com/szpajder/dumpvdl2.git
cd dumpvdl2 && mkdir -p build && cd build && cmake .. && make -j3 && sudo make install

echo "=== acarsdec (ACARS)"
cd "$SRC"; [ -d acarsdec ] || git clone --depth 1 https://github.com/TLeconte/acarsdec.git
cd acarsdec && mkdir -p build && cd build && cmake .. -Drtl=ON && make -j3 && sudo make install

echo "=== RTLSDR-Airband (airband voice, played on the speakers)"
cd "$SRC"; [ -d RTLSDR-Airband ] || git clone --depth 1 --branch v7.0.0 https://github.com/rtl-airband/RTLSDR-Airband.git
cd RTLSDR-Airband && mkdir -p build && cd build && cmake -DNFM=ON -DPLATFORM=native -DRTLSDR=ON -DPULSEAUDIO=ON .. \
  && make -j3 && sudo make install

echo "=== radiosonde_auto_rx (weather balloons, web UI on :5000)"
cd "$SRC"; [ -d radiosonde_auto_rx ] || git clone --depth 1 https://github.com/projecthorus/radiosonde_auto_rx.git
cd radiosonde_auto_rx/auto_rx && ./build.sh
python3 -m venv venv && venv/bin/pip install -r requirements.txt
[ -f station.cfg ] || cp station.cfg.example station.cfg

echo "=== Check"
for b in direwolf satdump-ui sdrpp acarsdec dumpvdl2 wsjtx js8call qsstv fldigi welle-io gpredict AIS-catcher rtl_airband gpspipe; do printf "%-11s %s\n" "$b" "$(command -v "$b" || echo MISSING)"; done
[ -f "$SRC/radiosonde_auto_rx/auto_rx/auto_rx.py" ] && echo "auto_rx     OK"
