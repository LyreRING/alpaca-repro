import os
import json
import argparse

from tlsevalcommon import TLSValidator
from tlsevalcommon import Zgrab2Item
from tlsevalcommon import Zgrab2ErrorChecker
from tlsevalcommon import get_port_list

class TLSFinder:
    def __init__(self, webscan_res, appscan_res, unique_certs_list, warn) -> None:
        self.__weblist = dict()
        self.__applist = []
        self.__certlist = []
        self.__merged_list = []

        self.read_webscan_res(webscan_res, warn)
        self.read_processed_appscan_res(appscan_res)
        self.read_cert_list(unique_certs_list)

    def read_webscan_res(self, res_file, warn):
        validator = TLSValidator()
        count = 0

        with open(res_file) as f:
            for line in f:
                zitem = Zgrab2Item(line)
                count = count + 1
                if count % 500 == 0:
                    print(f"\r[*] processing server info: {count}", end='')

                status = zitem.status()

                if status != "success":
                    if warn:
                        checker = Zgrab2ErrorChecker(zitem)
                        checker.warn_on_unknown()
                    continue

                fingerprint = zitem.server_fingerprint_sha256()
                if fingerprint is None:
                    continue

                cert_x509 = zitem.server_raw_cert()
                chain_x509 = zitem.chain_raw()
                cert_valid = validator.validate(cert_x509, chain_x509)

                if not cert_valid:
                    continue

                self.__weblist[zitem.domain()] = fingerprint
            print("")

    def read_processed_appscan_res(self, res_file):
        with open(res_file, 'r') as f:
            for line in f:
                self.__applist.append(json.loads(line))

    def read_cert_list(self, app_server_list_path):
        with open(app_server_list_path, 'r') as f:
            for line in f:
                self.__certlist.append(json.loads(line))

    def merge_weblist_to_certlist(self):
        for item in self.__certlist:
            extend_item = item
            extend_item["valid_web_domains"] = []
            for possible_web_name in item["possible_web_names"]:
                if possible_web_name in self.__weblist:
                    extend_item["valid_web_domains"].append(possible_web_name)
            self.__merged_list.append(extend_item)

    def write_certs_with_webserver(self, output_path):
        with open(output_path, 'w') as f:
            for item in self.__merged_list:
                f.write(json.dumps(item) + "\n")

    def write_server_statistics(self, output_path):
        ports = get_port_list()
        tables = dict()
        for port in ports:
            tables[f"port-{port}"] = {
                "appserver_num": 0,
                "with_valid_cert": 0,
                "unique_cert_num": 0,
                "web_num": 0
            }

        for app_item in self.__applist:
            port = app_item["port"]
            cert_valid = app_item["cert_valid"]
            tables[f"port-{port}"]["appserver_num"] = tables[f"port-{port}"]["appserver_num"] + 1
            if cert_valid:
                tables[f"port-{port}"]["with_valid_cert"] = tables[f"port-{port}"]["with_valid_cert"] + 1

        for item in self.__merged_list:
            ports = []
            for app in item["servers"]:
                port = app["port"]
                ports.append(port)
            ports = list(set(ports))
            for port in ports:
                tables[f"port-{port}"]["unique_cert_num"] = tables[f"port-{port}"]["unique_cert_num"] + 1
                if len(item["valid_web_domains"]) > 0:
                    tables[f"port-{port}"]["web_num"] = tables[f"port-{port}"]["web_num"] + 1

        table_to_write = []
        for port in tables:
            appserver_num = tables[port]["appserver_num"]
            with_valid_cert = tables[port]["with_valid_cert"]
            if appserver_num == 0:
                valid_cert_portion = 0
            else:
                valid_cert_portion = with_valid_cert / appserver_num

            unique_cert_num = tables[port]["unique_cert_num"]
            web_num = tables[port]["web_num"]
            if unique_cert_num == 0:
                web_portion = 0
            else:
                web_portion = web_num / unique_cert_num
            table_to_write.append({
                "port": port[5:],
                "appserver_num": appserver_num,
                "with_valid_cert": with_valid_cert,
                "valid_cert_portion": f"{valid_cert_portion * 100:.2f}%",
                "unique_cert_num": unique_cert_num,
                "web_num": web_num,
                "web_portion":  f"{web_portion * 100:.2f}%"
            })

        with open(output_path, 'w') as f:
            json.dump(table_to_write, fp=f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-unknown-error", default=False, action='store_true')
    parser.add_argument("--webscan-res", type=str)
    parser.add_argument("--processed-appscan-res", type=str)
    parser.add_argument("--unique-certs-list", type=str)
    parser.add_argument("--unique-certs-with-webserver-output", type=str)
    parser.add_argument("--server-statistics-output", type=str)
    args = parser.parse_args()

    finder = TLSFinder(args.webscan_res, args.processed_appscan_res, args.unique_certs_list, args.warn_unknown_error)
    finder.merge_weblist_to_certlist()
    finder.write_certs_with_webserver(args.unique_certs_with_webserver_output)
    finder.write_server_statistics(args.server_statistics_output)
