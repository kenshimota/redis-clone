from socket import socket

def read_input_redis(connection:  socket) -> None:
    while True:
        data = connection.recv(1024)
        if not data:
            break
        connection.sendall(b"+PONG\r\n")
