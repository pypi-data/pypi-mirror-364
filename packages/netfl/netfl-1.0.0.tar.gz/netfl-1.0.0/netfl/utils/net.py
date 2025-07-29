import os
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib import request
from time import sleep

from netfl.utils.log import log


def serve_file(filename: str, port: int = 9393) -> None:
    class FileServer(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == f"/{filename}":
                self.path = filename
                return super().do_GET()
            self.send_error(404, "File not found")

        def log_message(self, format, *args):
            pass
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' does not exist.")
    
    server_address = ("", port)
    httpd = HTTPServer(server_address, FileServer)
    log(f"Serving file {filename} on port {port}")
    httpd.serve_forever()


def download_file(filename: str, address: str, port: int = 9393) -> None:
    url = f"http://{address}:{port}/{filename}"
    file_path = os.path.join(os.getcwd(), filename)
    
    try:
        log(f"Downloading file {filename}")
        request.urlretrieve(url, file_path)
        log(f"File downloaded successfully")
    except Exception as e:
        log(f"Error downloading file: {e}")


def is_host_reachable(address: str, port: int, timeout: int = 5) -> bool:
    try:
        sock = socket.create_connection((address, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False


def wait_host_reachable(address: str, port: int, timeout: int = 5) -> None:
    log(f"Waiting for the host to become reachable on {address}:{port}")
    while not is_host_reachable(address, port,):
        log(f"Host is unreachable, retrying in {timeout} seconds")
        sleep(timeout)
