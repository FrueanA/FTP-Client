import socket
from typing import Tuple

from ftp_url import FtpUrl
from helpers import FtpProtocolError


class FtpSession:
    # FTP control connection + operations
    def __init__(self, url: FtpUrl, verbose: bool = False):
        self.url = url
        self.verbose = verbose
        self.control_sock = None
        self._control_file = None

    def connect(self) -> None:
        # Open control socket + greeting
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_sock.settimeout(10) #  added a timeout bc of autograder issues
        self.control_sock.connect((self.url.host, self.url.port))
        self._control_file = self.control_sock.makefile("rb")

        code, _ = self.read_response()
        if not (200 <= code < 300):
            raise FtpProtocolError(f"Greeting failed: {code}")

    def _send_raw(self, data: bytes) -> None:
        # Send raw bytes on control channel
        if self.control_sock is None:
            raise FtpProtocolError("Control socket not connected")
        self.control_sock.sendall(data)

    def send_command(self, command: str, arg: str | None = None) -> None:
        # Send FTP command
        line = f"{command} {arg}\r\n" if arg else f"{command}\r\n"
        if self.verbose:
            print(f"--> {line.rstrip()}")
        self._send_raw(line.encode("ascii"))

    def read_response(self) -> Tuple[int, str]:
        # Read a single-line FTP response and return (code, text)
        if self._control_file is None:
            raise FtpProtocolError("Control file not initialized")

        line_bytes = self._control_file.readline()
        if not line_bytes:
            raise FtpProtocolError("Control connection closed")

        line = line_bytes.decode("utf-8", "replace").rstrip("\r\n")
        if self.verbose:
            print(f"<-- {line}")

        if len(line) < 3 or not line[:3].isdigit():
            raise FtpProtocolError(f"Invalid FTP response: {line}")

        code = int(line[:3])
        text = line[4:] if len(line) > 4 and line[3] == " " else line[3:]
        return code, text

    def login(self) -> None:
        self.send_command("USER", self.url.user)
        code, _ = self.read_response()

        if 200 <= code < 300:
            return
        elif 300 <= code < 400:
            self.send_command("PASS", self.url.password)
            code2, _ = self.read_response()
            if not (200 <= code2 < 300):
                raise FtpProtocolError(f"PASS failed ({code2})")
        else:
            raise FtpProtocolError(f"USER failed ({code})")

    def set_binary_mode(self) -> None:
        # TYPE I, MODE S, STRU F
        for cmd, arg in (("TYPE", "I"), ("MODE", "S"), ("STRU", "F")):
            self.send_command(cmd, arg)
            code, _ = self.read_response()
            if not (200 <= code < 300):
                raise FtpProtocolError(f"{cmd} failed ({code})")

    def quit(self) -> None:
        # quit + close sockets
        try:
            if self.control_sock:
                try:
                    self.send_command("QUIT")
                    self.read_response()
                except Exception:
                    pass
        finally:
            if self._control_file:
                try: self._control_file.close()
                except Exception: pass
                self._control_file = None
            if self.control_sock:
                try: self.control_sock.close()
                except Exception: pass
                self.control_sock = None

    def enter_passive_mode(self) -> Tuple[str, int]:
        # Send PASV and parse
        self.send_command("PASV")
        code, text = self.read_response()
        if code != 227:
            raise FtpProtocolError(f"PASV failed ({code})")

        start = text.find("(")
        end = text.find(")")
        if start == -1 or end == -1:
            raise FtpProtocolError("Bad PASV response")

        inside = text[start+1:end]
        parts = inside.split(",")

        if len(parts) != 6:
            raise FtpProtocolError("Bad PASV address format")

        nums = []
        try:
            for p in parts:
                nums.append(int(p.strip()))
        except ValueError:
            raise FtpProtocolError("Non-numeric PASV address")

        h1, h2, h3, h4, p1, p2 = nums
        ip = f"{h1}.{h2}.{h3}.{h4}"
        port = (p1 << 8) + p2
        return ip, port

    def open_data_connection(self) -> socket.socket:
        # Open passive data socket
        ip, port = self.enter_passive_mode()
        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.settimeout(10) #  added a timeout bc of autograder issues
        ds.connect((ip, port))
        return ds

    def list_directory(self, path: str) -> str:
        # LIST directory -> return listing text
        ds = self.open_data_connection()
        arg = path if path else None

        self.send_command("LIST", arg)
        code, _ = self.read_response()
        if code >= 400:
            ds.close()
            raise FtpProtocolError(f"LIST failed ({code})")

        chunks = []
        try:
            while True:
                data = ds.recv(4096)
                if not data:
                    break
                chunks.append(data.decode("utf-8", "replace"))
        finally:
            ds.close()

        code2, _ = self.read_response()
        if code2 >= 400:
            raise FtpProtocolError(f"LIST final failed ({code2})")

        return "".join(chunks)

    def retrieve_file(self, remote_path: str, local_path: str) -> None:
        # RETR remote -> local file
        ds = self.open_data_connection()
        self.send_command("RETR", remote_path)
        code, _ = self.read_response()
        if code >= 400:
            ds.close()
            raise FtpProtocolError(f"RETR failed ({code})")

        try:
            with open(local_path, "wb") as f:
                while True:
                    data = ds.recv(4096)
                    if not data:
                        break
                    f.write(data)
        finally:
            ds.close()

        code2, _ = self.read_response()
        if code2 >= 400:
            raise FtpProtocolError(f"RETR final failed ({code2})")

    def store_file(self, local_path: str, remote_path: str) -> None:
        # STOR local -> remote file
        ds = self.open_data_connection()
        self.send_command("STOR", remote_path)
        code, _ = self.read_response()
        if code >= 400:
            ds.close()
            raise FtpProtocolError(f"STOR failed ({code})")

        try:
            with open(local_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    ds.sendall(chunk)
        finally:
            ds.close()

        code2, _ = self.read_response()
        if code2 >= 400:
            raise FtpProtocolError(f"STOR final failed ({code2})")

    def delete_file(self, remote_path: str) -> None:
        # DELE remote file
        self.send_command("DELE", remote_path)
        code, _ = self.read_response()
        if not (200 <= code < 300):
            raise FtpProtocolError(f"DELE failed ({code})")

    def make_directory(self, remote_path: str) -> None:
        # MKD remote dir
        self.send_command("MKD", remote_path)
        code, _ = self.read_response()
        if not (200 <= code < 300):
            raise FtpProtocolError(f"MKD failed ({code})")

    def remove_directory(self, remote_path: str) -> None:
        # RMD remote dir
        self.send_command("RMD", remote_path)
        code, _ = self.read_response()
        if not (200 <= code < 300):
            raise FtpProtocolError(f"RMD failed ({code})")
