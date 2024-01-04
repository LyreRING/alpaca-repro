# Server Tolerance Testsuite

## Prerequirement

Environment: Ubuntu 22.04 LTS

Install dependencies:

```
apt update
apt instal docker.io docker-compose
```

## Run the test

```
./run.sh
```

This will create a suites of docker-compose config files in `build`. 
To test a single server, run `docker-compose -f build/docker-compose-<servername>.yaml up`

## Configuration

Configuration of `tolerance_test.py` is `server-config.json`. There is a demo file `server-config-demo.json` 
that is used by `run.sh` by default. To use a user-specified `server-config.json`, run

```
python3 --config ./server-config.json --name <servername>
```

## Details of `run.sh`

`run.sh` includes 3 strategies. First build the baseimage of servers container, 
then generate docker-compose config files by `server-config.json`. At last, it runs 
docker-compose on each of the config files.

You can use `--start-step` or `--single-test` to skip strategies:

```
./run.sh --start-step 2
```

```
./run.sh --single-test 3
```
