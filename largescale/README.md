# LARGE SCALE TLS STUDY

## Pre-requirement

Test environment: Ubuntu 22.04 LTS

1. Install go-lang

```
apt install golang-go
```

## Run the Test

```
./run
```

## Strategies

1. `zmap` to scan the whole internet to get alive ip with port:

- SMTP: 25, 587, 465, 26, 2525
- IMAP: 143, 993
- POP3: 110, 995
- FTP: 21, 990
