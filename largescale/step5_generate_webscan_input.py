import csv
import argparse
import json

class TLSFinder:
    def __init__(self, res_file) -> None:
        self.__unique_certs = []
        with open(res_file, 'r') as f:
            for line in f:
                self.__unique_certs.append(json.loads(line))

    def generate_webserver_scan_input(self, output_path):
        with open(output_path, "w") as f:
            csvwriter = csv.writer(f, delimiter=',')
            for item in self.__unique_certs:
                names = item["possible_web_names"]
                for name in names:
                    csvwriter.writerow(["", name, ""])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unique-certs-res", type=str)
    parser.add_argument("--webscan-input-output-path", type=str)
    args = parser.parse_args()

    finder = TLSFinder(args.unique_certs_res)
    finder.generate_webserver_scan_input(args.webscan_input_output_path)
