import socket
import threading
import time


def create_client(server_ip, server_port):
    """Creates a TCP client that connects to the specified server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print(f"[CLIENT] Connected to {server_ip}:{server_port}")
        return client_socket
    except ConnectionRefusedError:
        print(f"[CLIENT] Error connecting to {server_ip}:{server_port}")
        return None


def send_matrix_requests(client_socket, matrix_size):
    """Sends matrix size request to the server and handles response."""
    try:
        client_socket.send(str(matrix_size).encode())
        response = client_socket.recv(1024).decode()
        print(f"[CLIENT] Received: {response}")
    except Exception as e:
        print(f"[CLIENT] Error sending request: {e}")
    finally:
        client_socket.close()


def load_server(server_ip, server_port, initial_matrix_size, request_count, delay):
    """Generates load by sending multiple requests to the server and increases matrix size over time."""
    matrix_size = initial_matrix_size
    for i in range(request_count):
        client_socket = create_client(server_ip, server_port)
        if client_socket:
            send_matrix_requests(client_socket, matrix_size)

        # Gradually increase the matrix size for more load
        matrix_size += 50  # Increase matrix size by 50 each time
        time.sleep(delay)  # Wait before sending the next request


def determine_load_mode():
    """Prompt for mode and return parameters for load generation."""
    mode = input("Enter mode (high/low): ").strip().lower()
    if mode == "high":
        print("High load mode selected.")
        return (
            1000,
            0.01,
            300,
        )  # High load: 1000 requests, small delay, starting matrix size 300
    else:
        print("Low load mode selected.")
        return (
            100,
            0.1,
            150,
        )  # Low load: 100 requests, longer delay, starting matrix size 150


if __name__ == "__main__":
    # Define server IPs and ports
    server1_ip = "192.168.122.225"
    server2_ip = "192.168.122.24"
    server_port = 9999

    # Get mode and corresponding load parameters
    request_count, delay, initial_matrix_size = determine_load_mode()

    # Create threads for each server
    server1_thread = threading.Thread(
        target=load_server,
        args=(server1_ip, server_port, initial_matrix_size, request_count, delay),
    )
    server2_thread = threading.Thread(
        target=load_server,
        args=(server2_ip, server_port, initial_matrix_size, request_count, delay),
    )

    # Start both threads to load both servers simultaneously
    server1_thread.start()
    server2_thread.start()

    # Wait for both threads to complete
    server1_thread.join()
    server2_thread.join()

    print("[CLIENT] Load testing completed on both servers.")
