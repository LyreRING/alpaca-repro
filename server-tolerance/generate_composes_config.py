import argparse
import json
import os
from pathlib import Path

def read_config(config_path):
    with open(config_path, 'r') as f:
        configs = json.load(f)
        return configs

def generate_composes(configs, server_path, output_path):
    for server_config in configs["servers"]:
        name = server_config["name"]
        host = server_config["host"]
        this_server_path = os.path.join(os.path.realpath(server_path), host)
        if Path(this_server_path).is_dir():
            file_content = \
f'''version: "3.9"
networks:
  default:
    name: tls-network
services:
  {host}:
    build: {this_server_path}
  tolerance_tester:
    build: {os.getcwd()}
    volumes:
      - {os.path.realpath("results")}:/results
      - {os.path.realpath("server-config.json")}:/tester/server-config.json
    depends_on:
      - {host}
    ports:
      - "9999:9999"
    command: [
      "--name",
      "{name}"
    ]
'''
        else:
            file_content = \
f'''version: "3.9"
services:
  tolerance_tester:
    build: {os.getcwd()}
    volumes:
      - {os.path.realpath("results")}:/results
      - {os.path.realpath("server-config.json")}:/tester/server-config.json
    ports:
      - "9999:9999"
    command: [
      "--name",
      "{name}"
    ]
'''
        with open(os.path.join(output_path, f"docker-compose-{name}.yaml"), 'w') as f:
            f.write(file_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str)
    parser.add_argument("--server-dir", type=str)
    parser.add_argument("--output-dir", type=str)
    args = parser.parse_args()

    try:
        os.mkdir(args.output_dir)
    except:
        pass

    configs = read_config(args.config)
    generate_composes(configs, args.server_dir, args.output_dir)
