#!/bin/bash

/usr/lib/courier/courier-authlib/authdaemond &
/sbin/rpcbind -w &
/usr/sbin/famd -T 0
service rsyslog start
service courier-pop start
service courier-pop-ssl start
service courier-imap start
service courier-imap-ssl start

while true; do sleep 1000; done
