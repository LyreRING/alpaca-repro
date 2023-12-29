#!/bin/sh

TEMP=$(getopt --longoptions zmap-scan-range:,zmap-sender-thread:,zmap-bitwidth:,\
  start-step:,single-test: \
  -n $0 -- $@)

eval set -- "$TEMP"

ZMAP_SCAN_RANGE="0.0.0.0/0"
ZMAP_SENDER_THREAD=16
ZMAP_BITWIDTH="1000M"
START_STEP=
SINGLE_TEST=

while true; do
  case "$1" in
    --zmap-scan-range) ZMAP_SCAN_RANGE="$2"; shift 2;;
    --zmap-sender-thread) ZMAP_SENDER_THREAD="$2"; shift 2;;
    --zmap-bitwidth) ZMAP_BITWIDTH="$2"; shift 2;;
    --start-step) START_STEP="$2"; shift 2;;
    --single-test) SINGLE_TEST="$2"; shift 2;;
    --) shift; break;;
    *) break;;
  esac
done

if [ ! -z $START_STEP ] && [ ! -z $SINGLE_TEST ]; then
  echo "[-] cannot set --start-step and --single-test at the same time"
  exit 2
fi

ZMAP_DIR=$PWD/build/zmap
ZGRAB2_DIR=$PWD/build/zgrab2
RESULT_DIR=$PWD/results

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
  mkdir -p build/go
  GOPATH=$(realpath build/go)
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

test_and_run_step() {
  cmd=$1
  step_no=$2

  if test ! -z START_STEP; then
    if [ $step_no -lt $START_STEP ]; then
      reutrn;
    fi
  fi

  if test ! -z $SINGLE_STEP; then
    if test $step_no != $SINGLE_STEP; then
      return
    fi
  fi

  $cmd
}

start_zmap_scanning() {
  echo "[*] step 1: start zmap scanning"

  port_list="25,587,465,26,2525,143,993,110,995,21,990"
  result_filename=zmap_result.csv
  if test -e $RESULT_DIR/$result_filename; then
    echo "[!] There exist a zmap result file, do you want to continure?"
    echo "[!] Would you like to continue y/n? "
    read reply
    if ! [ "$reply" = y -o "$reply" = Y ]; then
      echo "[-] cancelled"
      return
    fi
  fi
  touch $RESULT_DIR/$result_filename
  $ZMAP_BIN -B $ZMAP_BITWIDTH -p $port_list \
    --sender-threads=$ZMAP_SENDER_THREAD \
    -b /blacklist.conf \
    -o /result/$result_filename $ZMAP_SCAN_RANGE
}

start_zgrab2_scanning() {
  mkdir -p $RESULT_DIR
  $ZGRAB2_BIN -f input.txt \
    -l $RESULT_DIR/log.txt \
    -o $RESULT_DIR/output.txt \
    ftp
}

mkdir -p build

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

test_and_run_step start_zmap_scanning 1
# test_and_run_step start_zgrab2_scanning 2
