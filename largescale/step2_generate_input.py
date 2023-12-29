import argparse
import csv

def generate_appscan_input(res_path, output_path):
    resf = open(res_path, 'r')
    outf = open(output_path, 'w')

    reader = csv.reader(resf, delimiter=',')
    writer = csv.writer(outf, delimiter=',')
    for item in reader:
        output_item = [
            item[0],
            " ",
            f"tag{item[1]}"
        ]
        writer.writerow(output_item)

    outf.close()
    resf.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zmq-res", type=str)
    parser.add_argument("--appscan-input-output", type=str)
    args = parser.parse_args()

    generate_appscan_input(args.zmq_res, args.appscan_input_output)
