#!/bin/bash

TEMP=$(getopt -l zmap-scan-range:,zmap-sender-thread:,zmap-bandwidth:,zgrab2-sender:,start-step:,single-test:,warn-unknown-error -n "$0" -- $0 "$@")

if [ $? != 0 ]
then
  exit 1
fi

eval set -- "$TEMP"

ZMAP_SCAN_RANGE=
ZMAP_SENDER_THREAD=8
ZMAP_BANDWIDTH="10000M"
ZGRAB2_SENDER=10000
START_STEP=
SINGLE_TEST=
WARN_UNKNOWN_ERROR=

while true; do
  case "$1" in
    --zmap-scan-range) ZMAP_SCAN_RANGE="$2"; shift 2;;
    --zmap-sender-thread) ZMAP_SENDER_THREAD="$2"; shift 2;;
    --zmap-bandwidth) ZMAP_BANDWIDTH="$2"; shift 2;;
    --zgrab2-sender) ZGRAB2_SENDER="$2"; shift 2;;
    --start-step) START_STEP="$2"; shift 2;;
    --single-test) SINGLE_TEST="$2"; shift 2;;
    --warn-unknown-error) WARN_UNKNOWN_ERROR="--warn-unknown-error"; shift 1;;
    --) shift; break;;
    *) break;;
  esac
done

if [ ! -z $START_STEP ] && [ ! -z $SINGLE_TEST ]; then
  echo "[-] cannot set --start-step and --single-test at the same time"
  exit 2
fi

RESULT_DIR=$PWD/results
BUILD_DIR=$PWD/build
ZMAP_DIR=$BUILD_DIR/zmap
ZGRAB2_DIR=$BUILD_DIR/zgrab2

test_and_run_step() {
  cmd=$1
  step_no=$2

  if test ! -z $START_STEP; then
    if [ $step_no -lt $START_STEP ]; then
      return
    fi
  fi

  if test ! -z $SINGLE_TEST; then
    if test $step_no != $SINGLE_TEST; then
      return
    fi
  fi

  $cmd || exit $?
}

test_file_exist() {
  if test -e $1; then
    echo "[!] There exist file $1, be careful that it will be ERASED"
    echo "[!] Would you like to continue y/n? "
    read reply
    if ! [ "$reply" = y -o "$reply" = Y ]; then
      echo "[-] cancelled"
      exit 3
    fi
  fi
}

start_zmap_scanning() {
  echo "[*] step 1: start zmap scanning"

  port_list=$(cat port_list)

  result_filename=00_zmap_result.csv
  test_file_exist $RESULT_DIR/$result_filename

  touch $RESULT_DIR/$result_filename
  $ZMAP_BIN -B $ZMAP_BANDWIDTH -p $port_list \
    --sender-threads=$ZMAP_SENDER_THREAD \
    -b /blacklist.conf \
    -o /results/$result_filename $ZMAP_SCAN_RANGE
}

start_zgrab2_app_scanning() {
  echo "[*] step 2: start tls handshake test"
  ulimit -n 1048576
  python3 step2_generate_input.py \
    --zmq-res $RESULT_DIR/00_zmap_result.csv \
    --appscan-input-output $RESULT_DIR/01_appscan_input.txt

  zgrab_outfile_path=$RESULT_DIR/02_appscan_output.txt
  test_file_exist $zgrab_outfile_path

  $ZGRAB2_BIN \
    --input-file=$RESULT_DIR/01_appscan_input.txt \
    --output-file=$zgrab_outfile_path \
    --senders=$ZGRAB2_SENDER \
    --gomaxprocs=16 \
    multiple \
    --config-file=$PWD/appscan_multiple.ini
}

process_result_appscan() {
  echo "[*] step 3: strip unneeded content and check certificate"
  python3 step3_process_tls_res.py \
    --appscan-res $RESULT_DIR/02_appscan_output.txt \
    --processed-appscan-res-output $RESULT_DIR/03_appscan_output_processed.txt \
    $WARN_UNKNOWN_ERROR
}

gather_cert() {
  echo "[*] step 4: gether cert"
  python3 step4_gather_cert.py \
    --processed-appscan-res $RESULT_DIR/03_appscan_output_processed.txt \
    --unique-certs-output $RESULT_DIR/04_unique_certs.txt
}

start_scan_webserver() {
  echo "[*] step 5: test the gathered web server"

  python3 step5_generate_webscan_input.py \
    --unique-certs-res $RESULT_DIR/04_unique_certs.txt \
    --webscan-input-output-path $RESULT_DIR/05_webscan_input.txt

  ulimit -n 1048576
  $ZGRAB2_BIN \
    --input-file=$RESULT_DIR/05_webscan_input.txt \
    --output-file=$RESULT_DIR/06_webscan_output.txt \
    --senders=$ZGRAB2_SENDER \
    --gomaxprocs=16 \
    tls \
    --port=443 \
    --timeout=20
}

process_webserver_res() {
  echo "[*] step 6: process the result scanning webserver"
  python3 step6_process_webserver.py \
    --webscan-res $RESULT_DIR/06_webscan_output.txt \
    --processed-appscan-res $RESULT_DIR/03_appscan_output_processed.txt \
    --unique-certs-list $RESULT_DIR/04_unique_certs.txt \
    --unique-certs-with-webserver-output $RESULT_DIR/07_unique_certs_with_webserver.txt \
    --server-statistics-output $RESULT_DIR/08_server_statistics.txt \
    $WARN_UNKNOWN_ERROR
}

mkdir -p $BUILD_DIR
mkdir -p $RESULT_DIR
ZMAP_BIN="docker run --rm --network=host \
  -v $RESULT_DIR:/results -v $PWD/blacklist.conf:/blacklist.conf \
  zmap"
ZGRAB2_BIN=$(realpath $ZGRAB2_DIR/zgrab2)

test_and_run_step start_zmap_scanning 1
test_and_run_step start_zgrab2_app_scanning 2
test_and_run_step process_result_appscan 3
test_and_run_step gather_cert 4
test_and_run_step start_scan_webserver 5
test_and_run_step process_webserver_res 6
