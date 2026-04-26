import socket
import os
import datetime
import threading
import email.utils
import time
HOST = '127.0.0.1'
PORT = 8080
WEB_ROOT = "./www"
LOG_FILE = "access.log"
# Ensure web root exists
if not os.path.exists(WEB_ROOT):
    os.makedirs(WEB_ROOT)

class MultiThreadedServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server running on http://{self.host}:{self.port}")
        #threading
        while True:
            client_sock, client_addr = self.server_socket.accept()
            thread = threading.Thread(target=self.client_request, args=(client_sock, client_addr))
            thread.daemon = True
            thread.start()

    def client_request(self, client_sock, client_addr):
        client_sock.settimeout(5.0)
        keep_alive = True
        while keep_alive:
            try:
                request_data = client_sock.recv(1024).decode('utf-8')
                if not request_data:
                    break
                lines = request_data.split("\r\n")
                request_line = lines[0].split()

                # 400 Bad Request
                if len(request_line) < 3:
                    self.send_error(client_sock, "400 Bad Request", "Malformed")
                    self.log_request(client_addr[0], "Unknown", "400")
                    return

                method = request_line[0].upper()
                file_path_req = request_line[1]
                if file_path_req == "/":
                    file_path_req = "/index.html"

                headers = {}
                for line in lines[1:]:
                    if ": " in line:
                        key, val = line.split(": ", 1)
                        headers[key.lower()] = val

                keep_alive = "keep-alive" in headers.get("connection", "").lower()

                # Logic for GET and HEAD
                if method not in ["GET", "HEAD"]:
                    self.send_error(client_sock, "400 Bad Request", "Method not supported.")
                    break

                # 403 Forbidden & File Security
                base_dir = os.path.abspath(WEB_ROOT)
                requested_file = file_path_req.lstrip("/")
                full_path = os.path.abspath(os.path.join(base_dir, requested_file))
                if not full_path.startswith(base_dir):
                    self.send_error(client_sock, "403 Forbidden", "Access Denied")
                    self.log_request(client_addr[0], file_path_req, "403")
                    return

                # 404 Not Found
                if not os.path.exists(full_path) or os.path.isdir(full_path):
                    self.send_error(client_sock, "404 Not Found", "File not found.", keep_alive)
                    self.log_request(client_addr[0], file_path_req, "404")
                    break

                # Handle If-Modified-Since (304 Not Modified)
                file_stat = os.stat(full_path)
                last_modified_time = file_stat.st_mtime
                
                if "if-modified-since" in headers:
                    ims_date = email.utils.parsedate_to_datetime(headers["if-modified-since"]).timestamp()
                    if last_modified_time <= ims_date:
                        self.send_response_headers(client_sock, "304 Not Modified", None, 0, last_modified_time, keep_alive)
                        self.log_request(client_addr[0], file_path_req, "304")
                        if not keep_alive: break
                        continue

                # 200 OK
                content_type = self.get_mime_type(full_path)
                file_size = file_stat.st_size
                self.send_response_headers(client_sock, "200 OK", content_type, file_size, last_modified_time, keep_alive)

                # Send body if GET
                if method == "GET":
                    with open(full_path, "rb") as f:
                        client_sock.sendall(f.read())
                
                self.log_request(client_addr[0], file_path_req, "200")

                if not keep_alive:
                    break

            except (socket.timeout, Exception):
                break
        
        client_sock.close()

    def send_response_headers(self, sock, status, c_type, length, last_mod, keep_alive):
        last_mod_str = email.utils.formatdate(last_mod, usegmt=True)
        response = f"HTTP/1.1 {status}\r\n"
        if c_type: response += f"Content-Type: {c_type}\r\n"
        if length > 0: response += f"Content-Length: {length}\r\n"
        response += f"Last-Modified: {last_mod_str}\r\n"
        response += f"Connection: {'keep-alive' if keep_alive else 'close'}\r\n"
        response += "\r\n"
        sock.sendall(response.encode('utf-8'))

    def send_error(self, sock, status, message, keep_alive=False):
        body = f"<html><body><h1>{status}</h1><p>{message}</p></body></html>"
        response = f"HTTP/1.1 {status}\r\n"
        response += "Content-Type: text/html\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += f"Connection: {'keep-alive' if keep_alive else 'close'}\r\n"
        response += "\r\n"
        response += body
        sock.sendall(response.encode('utf-8'))

    def get_mime_type(self, path):
        if path.endswith(".html"): return "text/html"
        if path.endswith(".jpg") or path.endswith(".jpeg"): return "image/jpeg"
        if path.endswith(".png"): return "image/png"
        return "text/plain"

    def log_request(self, ip, filename, status):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{ip} | {timestamp} | {filename} | {status}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

if __name__ == "__main__":
    server = MultiThreadedServer(HOST, PORT)
    server.start()