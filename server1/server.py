import socket
import threading
import numpy as np


def handle_client(client_socket):
    """Handles client requests with matrix multiplication."""
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break

        try:
            # Receive matrix size from the client
            matrix_size = int(request)
            if matrix_size <= 0:
                response = "Matrix size must be a positive integer."
            else:
                # Generate two random matrices of the specified size
                matrix_a = np.random.rand(matrix_size, matrix_size)
                matrix_b = np.random.rand(matrix_size, matrix_size)

                # Perform matrix multiplication (CPU-intensive)
                result = np.dot(matrix_a, matrix_b)

                # Send back a success message
                response = f"Matrix multiplication of size {matrix_size}x{matrix_size} completed."
        except ValueError:
            response = "Invalid input, please send a valid integer."

        # Send response back to the client
        client_socket.send(response.encode())

    client_socket.close()


def start_server(host="0.0.0.0", port=9999):
    """Starts the server and listens for incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[SERVER] Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_server(
        host="192.168.122.225"
    )  # Replace with the actual IP for server1 or server2
