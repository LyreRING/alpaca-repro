#!/bin/bash

TEMP=$(getopt -l name: -n "$0" -- $0 "$@")

if [ $? != 0 ]
then
  exit 1
fi

eval set -- "$TEMP"

while true; do
  case "$1" in
    --name) name="$2"; shift 2;;
    --) shift; break;;
    *) break;;
  esac
done

tester_config_path=/tester/server-config.json
host=`jq ".servers | map(select(.name == \"$name\").host)[0]" $tester_config_path`
port=`jq ".servers | map(select(.name == \"$name\").port)[0]" $tester_config_path`
protocol=`jq ".servers | map(select(.name == \"$name\").protocol)[0]" $tester_config_path`
starttls=`jq ".servers | map(select(.name == \"$name\").starttls)[0]" $tester_config_path`

if test $starttls = "true"; then
  starttls_cmd="-starttls $protocol"
fi

echo "openssl s_client -connect $host:$port $starttls_cmd" > /tester/run-openssl
chmod +x /tester/run-openssl

service xinetd start

python3 /tester/tolerance_test.py --config $tester_config_path --name $name

while true; do sleep 1000; done
