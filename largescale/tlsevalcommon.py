import re
import OpenSSL
import json

def get_port_list():
    with open("port_list", 'r') as f:
        ports = f.read()
        return ports.split(',')

class TLSValidator:
    def __init__(self) -> None:
        self._PEM_RE = re.compile(b'-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?', re.DOTALL)
        self.x509_begin = "-----BEGIN CERTIFICATE-----\n"
        self.x509_end = "\n-----END CERTIFICATE-----"
        with open("/etc/ssl/certs/ca-certificates.crt", 'rb') as f:
            self.root_x509 = f.read()
        self.processed_chain = self.parse_chain(self.root_x509)
        self.store = OpenSSL.crypto.X509Store()
        for root_item in self.processed_chain:
            self.store.add_cert(OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, root_item))

    def parse_chain(self, chain):
        # returns a list of certificates
        return [c.group() for c in self._PEM_RE.finditer(chain)]

    def validate(self, cert, chain=[]) -> bool:
        x509_cert = bytes(self.x509_begin + cert + self.x509_end, 'ascii')
        client_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, x509_cert)

        for chain_item in chain:
            chain_item_x509 = bytes(self.x509_begin + chain_item + self.x509_end, 'ascii')
            self.store.add_cert(OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, chain_item_x509))

        ctx = OpenSSL.crypto.X509StoreContext(self.store, client_cert)
        try:
            ctx.verify_certificate()
        except OpenSSL.crypto.X509StoreContextError:
            return False
        return True

class Zgrab2Item:
    def __init__(self, line) -> None:
        self.__line = line
        self.__json = json.loads(line)
        self.__tag = list(self.__json["data"].keys())[0]
        self.__proto = self.__json["data"][self.__tag]["protocol"]
        try:
            if self.__proto == "tls":
                self.__handshake_log = self.__json["data"][self.__tag]["result"]["handshake_log"]
            else:
                self.__handshake_log = self.__json["data"][self.__tag]["result"]["tls"]["handshake_log"]
        except KeyError:
            self.__handshake_log = None
        except TypeError:
            self.__handshake_log = None

    def host(self):
        return self.__json["ip"]

    def domain(self):
        return self.__json["domain"]

    def port(self):
        if self.__tag == "tls":
            return 443
        else:
            return self.__tag[3:]

    def status(self):
        return self.__json["data"][self.__tag]["status"]

    def banner(self):
        try:
            banner = self.__json["data"][self.__tag]["result"]["banner"]
        except KeyError:
            banner = None
        except TypeError:
            banner = None
        return banner

    def proto(self):
        return self.__json["data"][self.__tag]["protocol"]

    def error(self):
        return self.__json["data"][self.__tag]["error"]

    def server_raw_cert(self):
        if self.__handshake_log is None:
            return None

        try:
            cert = self.__handshake_log["server_certificates"]["certificate"]["raw"]
        except KeyError:
            cert = None
        return cert

    def server_cert_subject(self):
        if self.__handshake_log is None:
            return None

        try:
            cert = self.__handshake_log["server_certificates"]["certificate"]
            parsed = cert["parsed"]
            subject = parsed["subject"]
        except KeyError:
            subject = None
        return subject

    def cn(self):
        if self.__handshake_log is None:
            return None

        try:
            cert = self.__handshake_log["server_certificates"]["certificate"]
            parsed = cert["parsed"]
            cn = parsed["subject"]["common_name"]
        except KeyError:
            cn = []
        return cn

    def san(self):
        if self.__handshake_log is None:
            return None

        try:
            cert = self.__handshake_log["server_certificates"]["certificate"]
            parsed = cert["parsed"]
            san = parsed["extensions"]["subject_alt_name"]["dns_names"]
        except KeyError:
            san = []
        return san

    def chain_raw(self) -> list[str]:
        chain_x509 = []
        if self.__handshake_log is None:
            return None

        try:
            certs_chain = self.__handshake_log["server_certificates"]["chain"]
        except KeyError:
            return []

        for chain_item in certs_chain:
            chain_x509.append(chain_item["raw"])
        return chain_x509

    def server_fingerprint_sha256(self):
        if self.__handshake_log is None:
            return None

        try:
            cert = self.__handshake_log["server_certificates"]["certificate"]
            parsed = cert["parsed"]
            fingerprint = parsed["fingerprint_sha256"]
        except KeyError:
            fingerprint = None
        return fingerprint

class Zgrab2ErrorChecker:
    def __init__(self, item: Zgrab2Item) -> None:
        self.__item = item

    def check_unknown_error_smtp(self):
        status = self.__item.status()
        error = self.__item.error()
        if status == "protocol-error" and error == "Invalid response for SMTP":
            return True

    def check_unknown_error_imap(self):
        status = self.__item.status()
        error = self.__item.error()
        if status == "protocol-error" and error == "Invalid response for IMAP":
            return True

    def check_unknown_error_pop3(self):
        status = self.__item.status()
        error = self.__item.error()
        if status == "protocol-error" and error == "Invalid response for POP3":
            return True

    def warn_on_unknown(self) -> None:
        proto = self.__item.proto()
        status = self.__item.status()
        error = self.__item.error()

        if proto == "smtp":
            if self.check_unknown_error_smtp():
                return

        if proto == "imap":
            if self.check_unknown_error_imap():
                return

        if proto == "pop3":
            if self.check_unknown_error_pop3():
                return

        if status in ["connection-timeout", "io-timeout"]:
            return
        if status == "unknown-error" and error == "tls: first record does not look like a TLS handshake":
            return
        if status == "unknown-error" and "tls: oversized record received with length" in error:
            return
        if status == "unknown-error" and error == "remote error: alert(112)":
            return

        print(f"[!] unknown item: {self.__item.__line}")
