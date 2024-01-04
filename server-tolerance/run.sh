#!/bin/bash

TEMP=$(getopt -l start-step:,single-test: -n "$0" -- $0 "$@")

if [ $? != 0 ]
then
  exit 1
fi

eval set -- "$TEMP"

START_STEP=
SINGLE_TEST=

while true; do
  case "$1" in
    --start-step) START_STEP="$2"; shift 2;;
    --single-test) SINGLE_TEST="$2"; shift 2;;
    --) shift; break;;
    *) break;;
  esac
done

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

ALPACA_CODE_PATH=$PWD/../alpaca-code

build_base_images() {
  echo "[*] step 1: build servers' base image"

  store_dir=$PWD
  cd ../servers/baseimage
  ./build.sh
  cd $store_dir
}

generate_docker_compose_configs() {
  echo "[*] step 2: generage docker compose config files"

  cp server-config-demo.json server-config.json

  python3 ./generate_composes_config.py \
    --config ./server-config.json \
    --output-dir build \
    --server-dir ../servers
}

test_tolerance() {
  echo "[*] step 3: run test"
  touch results/00_tolerance.txt

  for item in build/*; do
    docker-compose -f $item build
    timeout -s SIGINT 20 docker-compose -f $item up
    docker-compose -f $item down
  done
}

test_and_run_step build_base_images 1
test_and_run_step generate_docker_compose_configs 2
test_and_run_step test_tolerance 3
