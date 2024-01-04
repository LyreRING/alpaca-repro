import socket
import ssl
import argparse
import time
import json
from multiprocessing import Queue, Process

HTTP_REQUEST = "POST / HTTP/1.1\r\n"
HTTP_REQUEST_HEADERS = "Host: localhost\r\n" \
    "Connection: keep-alive\r\n"
HTTP_REQUEST_HEADERS_FULL = "POST / HTTP/1.1" \
    "Host: localhost\r\n" \
    "Connection: keep-alive\r\n" \
    "Cache-Control: max-age=0\r\n" \
    "sec-ch-ua: \"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Microsoft Edge\";v=\"120\"\r\n" \
    "sec-ch-ua-mobile: ?0\r\n" \
    "sec-ch-ua-platform: \"Windows\"\r\n" \
    "Upgrade-Insecure-Requests: 1\r\n" \
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0\r\n" \
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\n" \
    "Sec-Fetch-Site: none\r\n" \
    "Sec-Fetch-Mode: navigate\r\n" \
    "Sec-Fetch-User: ?1\r\n" \
    "Sec-Fetch-Dest: document\r\n" \
    "Accept-Encoding: gzip, deflate, br\r\n" \
    "Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6\r\n\r\n"


BUFFER_SIZE = 1024
def recv_ssl(client, count, queue):
    res = b""
    try:
        for _i in range(count):
            this_res = client.recv(BUFFER_SIZE)
            if len(this_res) == 0:
                break
            res = res + this_res
    except Exception as e:
        print(f"[-] recv exception as {e}")
    queue.put(res)

class ServerToleranceTester:
    def __init__(self, config, name) -> None:
        with open(config, 'r') as f:
            self.configs = json.load(f)

        for item in self.configs["servers"]:
            if item["name"] == name:
                self.test_config = item
                break

        self.result_path = self.configs["output-path"]

        self.name = name
        self.host = self.test_config["host"]
        self.port = self.test_config["port"]
        self.proto = self.test_config["protocol"]
        self.starttls = self.test_config["starttls"]

        self.proto_info = None
        for item in self.configs["protocol-info"]:
            if item["protocol"] == self.proto:
                self.proto_info = item
                break

        server_login_cmds = {
            "imap": [
                "A1 LOGIN <user> <password>"
            ],
            "pop3": [
                "USER <user>",
                "PASS <password>"
            ],
            "ftp": [
                "USER <user>",
                "PASS <password>"
            ]
        }
        self.login_cmds = []
        if "login" in self.test_config:
            user = self.test_config["login"]["user"]
            password = self.test_config["login"]["password"]
            login_cmds = server_login_cmds[self.proto]
            for item in login_cmds:
                self.login_cmds.append(item.replace("<user>", user).replace("<password>", password))
            print(self.login_cmds)

        self.context = ssl.create_default_context()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        for cert in self.configs["certificates"]:
            self.context.load_verify_locations(cert)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.VerifyMode.CERT_NONE

    def connect_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.starttls:
            self.client.connect((self.host, self.port))
            print(self.client.recv(BUFFER_SIZE))
            self.send_starttls_command()
            self.client = self.context.wrap_socket(self.client, server_hostname="tls-server.com")
        else:
            self.client = self.context.wrap_socket(self.client, server_hostname="tls-server.com")
            self.client.connect((self.host, self.port))
            time.sleep(0.1)
            print(self.client.recv(BUFFER_SIZE))

    def server_login(self):
        for item in self.login_cmds:
            print(item)
            self.send(bytes(item + "\r\n", 'ascii'))
            print(self.recv_lines(1))

    def recv_lines(self, line):
        res = b""
        Q = Queue()
        p = Process(target=recv_ssl, args=(self.client, line, Q))
        p.start()
        p.join(timeout=3)
        p.terminate()
        if p.exitcode is None:
            print("[!] recv timeout!")
            return res
        if p.exitcode == 0:
            res = Q.get()

        return res

    def send(self, content):
        return self.client.send(content)

    def check_socket_alive(self) -> bool:
        try:
            time.sleep(0.1)
            self.client.send(b"0\r\n")
            res = self.client.recv(BUFFER_SIZE)
            if len(res) == 0:
                return False
        except (ssl.SSLZeroReturnError, ssl.SSLEOFError, ssl.SSLError) as e:
            print(f"exception while checking alive: {e}")
            return False
        return True

    def send_starttls_command(self):
        # print("[*] sending starttls command")
        if self.proto == "ftp":
            self.client.send(b"AUTH TLS\r\n")
            print(self.client.recv(BUFFER_SIZE))
        elif self.proto == "smtp":
            self.client.send(b"EHLO whatever\r\n")
            print(self.client.recv(BUFFER_SIZE))
            self.client.send(b"STARTTLS\r\n")
            print(self.client.recv(BUFFER_SIZE))
        elif self.proto == "pop3":
            self.client.send(b"STLS\r\n")
            print(self.client.recv(BUFFER_SIZE))
        else:
            print(f"[-] starttls protocol {self.proto}")


    def test_http_request_tolerance(self) -> bool:
        print("[*] start sending http request")
        self.connect_server()
        self.client.send(bytes(HTTP_REQUEST, 'ascii'))
        res = self.client.recv(BUFFER_SIZE)
        print(res.decode('ascii'))
        res = self.check_socket_alive()
        self.client.close()
        return res

    def test_http_header_tolerance(self) -> bool:
        print("[*] start sending http request with headers")
        self.connect_server()
        test_content = HTTP_REQUEST + HTTP_REQUEST_HEADERS
        self.client.send(bytes(test_content, 'ascii'))
        time.sleep(0.1)
        this_res = self.recv_lines(test_content.count("\r\n"))
        return this_res.decode('ascii').count("\r\n") == test_content.count("\r\n")

    def test_max_tolerance(self) -> int:
        print("[*] start testing tolerance")
        self.connect_server()
        for i in range(100):
            try:
                self.client.send(b"asdasdasd\r\n")
                time.sleep(0.01)
                res = self.client.recv(BUFFER_SIZE)
                if len(res) == 0:
                    return i
                print(res)
            except (ssl.SSLEOFError, ssl.SSLZeroReturnError):
                return i - 2
            except Exception as e:
                print(f"[!] unknwon exception {e}!")
                return i
        return 0

    def _test_reflect_ascii_with_login(self, login: bool):
        valid_reflection = []
        if self.proto_info is None:
            return
        test_cmds = self.proto_info["reflection-test-cmds"]

        reflectiontest = "reflectiontest"
        for cmd in test_cmds:
            self.connect_server()
            if login:
                self.server_login()
            bcmd = bytes(f"{cmd} {reflectiontest}\r\n", 'ascii')
            self.send(bcmd)
            time.sleep(0.01)
            res = self.recv_lines(1)
            print(res)
            if reflectiontest in res.decode('ascii'):
                if login:
                    valid_reflection.append("<login>" + cmd)
                else:
                    valid_reflection.append(cmd)

            self.client.close()

        self.connect_server()
        if login:
            self.server_login()
        self.send(bytes(reflectiontest + "\r\n", 'ascii'))
        res = self.recv_lines(1)
        if reflectiontest in res.decode('ascii'):
            if login:
                valid_reflection.append("<login> <direct>")
            else:
                valid_reflection.append("<direct>")
        self.client.close()

        return valid_reflection

    def test_reflect_ascii(self):
        print("[*] start testing reflection")
        res = []
        if len(self.login_cmds) > 0:
            res = res + self._test_reflect_ascii_with_login(True)
        res = res + self._test_reflect_ascii_with_login(False)

        return res

    def test_exp(self):
        print("[*] start testing exp")
        exp = dict()

        if not "payloads" in self.test_config:
            return None
        payloads = self.test_config["payloads"]

        for payload_type in payloads:
            self.connect_server()
            exp[payload_type] = []
            for single_payload in payloads[payload_type]:
                test_content = HTTP_REQUEST_HEADERS_FULL + single_payload
                self.send(bytes(test_content, 'ascii'))
                time.sleep(0.1)
                this_res = self.recv_lines(test_content.count("\r\n") - 1)
                print(this_res)
                exp[payload_type].append(this_res.decode('ascii'))
            self.client.close()
        return exp

    def run_test(self):
        request = self.test_http_request_tolerance()
        header = self.test_http_header_tolerance()
        max = self.test_max_tolerance()
        exp = self.test_exp()
        valid_reflection = self.test_reflect_ascii()
        result = {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "request": request,
            "header": header,
            "max": max,
            "exp": exp,
            "valid-reflection": valid_reflection
        }
        with open(self.result_path, 'a') as f:
            f.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--name", type=str, required=True)
    args = parser.parse_args()

    tester = ServerToleranceTester(args.config, args.name)
    tester.run_test()
