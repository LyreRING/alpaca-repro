import os
import json
import argparse
import re

from tlsevalcommon import TLSValidator
from tlsevalcommon import Zgrab2Item
from tlsevalcommon import Zgrab2ErrorChecker
from tlsevalcommon import get_port_list

BANNER_MAP = [
    {
        "banner-fragment": "Dovecot",
        "server": "dovecot"
    },
    {
        "banner-fragment": "SmartGateway",
        "server": "inetutils"
    },
    {
        "banner-fragment": "Idea",
        "server": "idea"
    },
    {
        "banner-fragment": "Training System",
        "server": "idea"
    },
    {
        "banner-fragment": "Mailenable",
        "server": "mailenable"
    },
    {
        "banner-fragment": "OpenSMTPD",
        "server": "opensmtpd"
    },
    {
        "banner-fragment": "SurgeSMTP",
        "server": "surge"
    },
    {
        "banner-fragment": "Wing FTP Server",
        "server": "wingftp"
    },
    {
        "banner-fragment": "vsFTPd",
        "server": "vsftpd"
    },
    {
        "banner-fragment": "Synology",
        "server": "synology"
    },
    {
        "banner-fragment": "FileZilla",
        "server": "filezilla"
    },
    {
        "banner-fragment": "Bigfoot",
        "server": "bigfoot"
    },
    {
        "banner-fragment": "Exim",
        "server": "exim"
    },
    {
        "banner-fragment": "Postfix",
        "server": "postfix"
    },
    {
        "banner-fragment": "Zimbra",
        "server": "zimbra"
    },
    {
        "banner-fragment": "ProFTPD",
        "server": "proftpd"
    },
    {
        "banner-fragment": "Sendinblue",
        "server": "sendinblue"
    },
    {
        "banner-fragment": "Sophos",
        "server": "sophos"
    },
    {
        "banner-fragment": "MDaemon",
        "server": "mdaemon"
    },
    {
        "banner-fragment": "Sendmail",
        "server": "sendmail"
    },
    {
        "banner-fragment": "Postcow",
        "server": "postcow"
    },
    {
        "banner-fragment": "Mailsystemx",
        "server": "mailsystemx"
    },
    {
        "banner-fragment": "totah server ready",
        "server": "totah"
    },
    {
        "banner-fragment": "FTP Server ready",
        "server": "unknwon"
    },
    {
        "banner-fragment": "220 ESMTP MAIL Server",
        "server": "unknwon"
    },
    {
        "banner-fragment": "Europe Mail Service",
        "server": "europe-mail"
    },
    {
        "banner-fragment": "Courier",
        "server": "courier"
    },
    {
        "banner-fragment": "Cyrus",
        "server": "cyrus"
    },
    {
        "banner-fragment": "Kerio Connect",
        "server": "kerio-connect"
    },
    {
        "banner-fragment": "Pure-FTPd",
        "server": "pureftpd"
    },
    {
        "banner-fragment": "IceWarp Epos",
        "server": "icewarp"
    },
    {
        "banner-fragment": "Office-Logic InterChange Lite",
        "server": "office-logic-interchange"
    },
    {
        "banner-fragment": "Axigen",
        "server": "axigen"
    },
    {
        "banner-fragment": "Microsoft Exchange",
        "server": "microsoft"
    },
    {
        "banner-fragment": "Serv-U",
        "server": "servu"
    },
    {
        "banner-fragment": "kasserver",
        "server": "kasserver"
    },
    {
        "banner-fragment": "Multicraft",
        "server": "multicraft"
    },
]

class TLSFinder:
    def __init__(self, appscan_res, unique_certs_list, warn) -> None:
        self._appdict = dict()
        self._server_type_list = dict()
        self._banner_map = []

        for port in get_port_list():
            self._server_type_list[port] = dict()

        self.read_processed_appscan_res(appscan_res, warn)
        self.process_cert_list(unique_certs_list)

    def read_processed_appscan_res(self, res_file, warn):
        with open(res_file, 'r') as f:
            for line in f:
                app = json.loads(line)
                if not app["cert_valid"]:
                    continue
                this_serve = ""
                for banner_test in BANNER_MAP:
                    if banner_test["banner-fragment"] in app["banner"]:
                        this_serve = banner_test["server"]
                if this_serve == "":
                    if warn:
                        print(f"Unknown banner string on {app['port']}: {app['banner']}")
                    continue
                self._appdict[f"{app['host']}:{app['port']}"] = this_serve

    def process_cert_list(self, cert_list_file):
        with open(cert_list_file, 'r') as f:
            for line in f:
                cert = json.loads(line)
                if len(cert["valid_web_domains"]) == 0:
                    continue
                for server in cert["servers"]:
                    server_type = ""
                    try:
                        server_type = self._appdict[f"{server['host']}:{server['port']}"]
                    except:
                        server_type = "unknown"
                    self._server_type_add_count(server['port'], server['host'], server_type)

    def _server_type_add_count(self, port, host, server_type):
        this_list = self._server_type_list[port]
        try:
            _ = this_list[server_type]
        except:
            this_list[server_type] = {
                "count": 0,
                "host-list": []
            }
        this_list[server_type]["count"] = this_list[server_type]["count"] + 1
        this_list[server_type]["host-list"].append(host)
        self._server_type_list[port] = this_list

    def write_output(self, output_path):
        with open(output_path, 'w') as f:
            json.dump({ "res": self._server_type_list }, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-unknown-error", default=False, action='store_true')
    parser.add_argument("--processed-appscan-res", type=str)
    parser.add_argument("--unique-certs-with-webserver", type=str)
    parser.add_argument("--server-statistics-output", type=str)
    args = parser.parse_args()

    finder = TLSFinder(args.processed_appscan_res, args.unique_certs_with_webserver, args.warn_unknown_error)
    finder.write_output(args.server_statistics_output)

