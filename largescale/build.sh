#!/bin/sh
mkdir -p $BUILD_DIR

RESULT_DIR=$PWD/results
BUILD_DIR=$PWD/build
ZMAP_DIR=$BUILD_DIR/zmap
ZGRAB2_DIR=$BUILD_DIR/zgrab2

build_zmap() {
  ZMAP_URL=https://github.com/zmap/zmap.git
  if ! test -d $ZMAP_DIR; then
    git clone $ZMAP_URL $ZMAP_DIR
  fi
  localdir=$PWD
  cd $ZMAP_DIR
  docker build . -t zmap
  cd $localdir
}

build_zgrab2() {
  mkdir -p $BUILD_DIR/go
  GOPATH=$BUILD_DIR/go
  ZGRAB2_HASH=97ba87c0e706
  ZGRAB2_URL=https://github.com/zmap/zgrab2.git

  if ! test -d $ZGRAB2_DIR; then
    git clone $ZGRAB2_URL $ZGRAB2_DIR
  fi
  localdir=$PWD
  cd $ZGRAB2_DIR
  git checkout $ZGRAB2_HASH
  make
  cd $localdir
}

echo "[*] building zmap"
build_zmap
ZMAP_BIN="docker run --rm --network=host \
  -v $RESULT_DIR:/results -v $PWD/blacklist.conf:/blacklist.conf \
  zmap"

echo "[*] building zgrab"
build_zgrab2
ZGRAB2_BIN=$(realpath $ZGRAB2_DIR/zgrab2)
if ! test -e $ZGRAB2_BIN; then
  echo "[-] build zgrab2 failed"
  exit 1
fi
