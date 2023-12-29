import os
import argparse
import json
import csv

from tlsevalcommon import TLSValidator
from tlsevalcommon import Zgrab2Item
from tlsevalcommon import Zgrab2ErrorChecker

class TLSFinder:
    def __init__(self, res_file, warn) -> None:
        self.__app_list = []

        validator = TLSValidator()
        count = 0

        with open(res_file, 'r') as f:
            for line in f:
                zitem = Zgrab2Item(line)
                count = count + 1
                if count % 500 == 0:
                    print(f"\r[*] processing server info: {count}", end='')
                host = zitem.host()
                port = zitem.port()
                banner = zitem.banner()
                status = zitem.status()

                if zitem.status() == "application-error":
                    self.__app_list.append({
                        "host": host,
                        "port": port,
                        "use_tls": False,
                        "cert_valid": False,
                        "banner": banner
                    })
                    continue

                if status != "success":
                    if warn:
                        checker = Zgrab2ErrorChecker(zitem)
                        checker.warn_on_unknown()
                    continue

                if not "server_certificates" in line:
                    self.__app_list.append({
                        "host": host,
                        "port": port,
                        "use_tls": False,
                        "cert_valid": False,
                        "banner": banner
                    })
                    continue

                cn = zitem.cn()
                san = zitem.san()
                fingerprint_sha256 = zitem.server_fingerprint_sha256()
                cert_x509 = zitem.server_raw_cert()
                chain_x509 = zitem.chain_raw()

                cert_valid = validator.validate(cert_x509, chain_x509)

                self.__app_list.append({
                    "host": host,
                    "port": port,
                    "cn": cn,
                    "san": san,
                    "fingerprint_sha256": fingerprint_sha256,
                    "use_tls": True,
                    "cert_valid": cert_valid,
                    "banner": banner
                })
        print("")

    def write_appscan_processed_data(self, output_path):
        with open(output_path, "w") as f:
            for item in self.__app_list:
                f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-unknown-error", default=False, action='store_true')
    parser.add_argument("--appscan-res", type=str)
    parser.add_argument("--processed-appscan-res-output", type=str)
    args = parser.parse_args()

    finder = TLSFinder(args.appscan_res, args.warn_unknown_error)
    finder.write_appscan_processed_data(args.processed_appscan_res_output)
