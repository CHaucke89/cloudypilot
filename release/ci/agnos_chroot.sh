#!/usr/bin/env bash
# Mounts the AGNOS system image pinned in agnos.json as a writable chroot at $1, so the prebuilt
# can be built on any arm64 Linux host instead of a comma device. Further arguments are host
# directories bound at the same path inside it. Needs root, curl, jq, xz and simg2img.
set -euo pipefail

ROOT="$1"
shift
WORK="${AGNOS_WORK_DIR:-/tmp/agnos}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

read -r URL HASH < <(jq -r '.[] | select(.name == "system") | "\(.url) \(.hash_raw)"' "$REPO/openpilot/system/hardware/tici/agnos.json")
IMG="$WORK/system-$HASH.img"
mkdir -p "$WORK"
if [ ! -f "$IMG" ]; then
  echo "Downloading $URL"
  curl -fsSL --retry 3 "$URL" | xz -T0 -dc > "$IMG.sparse"
  simg2img "$IMG.sparse" "$IMG.tmp"
  rm "$IMG.sparse"
  echo "$HASH  $IMG.tmp" | sha256sum -c -
  mv "$IMG.tmp" "$IMG"
fi

# the image has only a few hundred MB free, so writes go to an overlay and the image stays pristine
mkdir -p "$WORK/lower" "$WORK/upper" "$WORK/overlay-work" "$ROOT"
mount -o loop,ro,noload "$IMG" "$WORK/lower"
mount -t overlay overlay -o "lowerdir=$WORK/lower,upperdir=$WORK/upper,workdir=$WORK/overlay-work" "$ROOT"

mount -t proc proc "$ROOT/proc"
mount --rbind /sys "$ROOT/sys"
mount -t tmpfs tmpfs "$ROOT/tmp"

# a private /dev, so the fake /dev/ion below doesn't land on the host
mount -t tmpfs -o mode=755 tmpfs "$ROOT/dev"
for n in null zero full random urandom tty; do
  touch "$ROOT/dev/$n"
  mount --bind "/dev/$n" "$ROOT/dev/$n"
done
mkdir -p "$ROOT/dev/pts" "$ROOT/dev/shm"
mount --bind /dev/pts "$ROOT/dev/pts"
mount -t tmpfs tmpfs "$ROOT/dev/shm"
ln -s /proc/self/fd "$ROOT/dev/fd"
# msgq only builds the ion VisionBuf, which camerad and modeld need on device, when /dev/ion exists
touch "$ROOT/dev/ion"

rm -f "$ROOT/etc/resolv.conf"
cp -L /etc/resolv.conf "$ROOT/etc/resolv.conf"

for d in "$@"; do
  mkdir -p "$d" "$ROOT$d"
  mount --bind "$d" "$ROOT$d"
done
