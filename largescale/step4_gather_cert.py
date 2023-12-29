import argparse
import json

class TLSFinder:
    def __init__(self, res_file) -> None:
        self.__app_list = []
        self.__unique_certs = dict()

        with open(res_file, 'r') as f:
            for app_line in f:
                self.__app_list.append(json.loads(app_line))

    def get_unique_certs_result(self):
        count = 0
        for cert_item in self.__app_list:
            count = count + 1
            if count % 500 == 0:
                print(f"\r[*] processing server info: {count}", end='')

            if not cert_item["cert_valid"]:
                continue

            names = cert_item["cn"] + cert_item["san"]

            if not cert_item["fingerprint_sha256"] in self.__unique_certs:
                self.__unique_certs[cert_item["fingerprint_sha256"]] = {
                    "names": [],
                    "servers": []
                }

            self.__unique_certs[cert_item["fingerprint_sha256"]]["names"] = \
                self.__unique_certs[cert_item["fingerprint_sha256"]]["names"] + names

            self.__unique_certs[cert_item["fingerprint_sha256"]]["servers"].append({
                "host": cert_item["host"],
                "port": cert_item["port"],
            })

        print("")
        for cert_item in self.__unique_certs:
            self.__unique_certs[cert_item]["names"] = list(set(self.__unique_certs[cert_item]["names"]))
            possible_web_names = []
            for name in self.__unique_certs[cert_item]["names"]:
                if "*" == name[0]:
                    possible_web_names.append(name.replace("*", "www"))
                else:
                    possible_web_names.append(name)
            possible_web_names = list(set(possible_web_names))
            self.__unique_certs[cert_item]["possible_web_names"] = possible_web_names

    def write_unique_certs_to_file(self, filename):
        with open(filename, "w") as f:
            for item in self.__unique_certs:
                file_item = {
                    "cert_fingerprint": item,
                    "names": self.__unique_certs[item]["names"],
                    "servers": self.__unique_certs[item]["servers"],
                    "possible_web_names": self.__unique_certs[item]["possible_web_names"]
                }
                f.writelines(json.dumps(file_item) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-appscan-res", type=str)
    parser.add_argument("--unique-certs-output", type=str)
    args = parser.parse_args()

    finder = TLSFinder(args.processed_appscan_res)
    finder.get_unique_certs_result()
    finder.write_unique_certs_to_file(args.unique_certs_output)
