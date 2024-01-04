# LARGE SCALE TLS STUDY

## Pre-requirement

Test environment: Ubuntu 22.04 LTS

1. Install go-lang (need version >= 1.18)

```
apt install golang-go
```

For manual installation, refer to [https://go.dev/doc/install](https://go.dev/doc/install).

2. Install docker

```
apt install docker.io
```

3. Install python dependencies

```
apt install python3 python3-pip python3-venv
python3 -m venv .venv
. ./.venv/bin/activate
pip3 install -r ./requirements.txt
```

## Run the Test

```
./run
```
