import socket

from app.inputs.read_input_redis import read_input_redis


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment the code below to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connect, address = server_socket.accept()  # wait for client
    read_input_redis(connect)


if __name__ == "__main__":
    main()
