

import socket
import threading
import json

# Двумерный массив для хранения dot_list
dot_list = [[-100,-100,-100],[-100,-100,-100],[-100,-100,-100]]

def handle_client(client_socket):
    global dot_list
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            if (json.loads(data.decode('utf-8'))=='end'):
                dot_list = [[-100,-100,-100],[-100,-100,-100],[-100,-100,-100]]
            else:    
                # Преобразуем входные данные из JSON в список
                new_array = json.loads(data.decode('utf-8'))
                # Добавляем новый массив в dot_list
                dot_list.append(new_array)
                print(f"Updated dot_list: {dot_list}")
                # Отправляем обновленный dot_list обратно всем клиентам
                send_updated_dot_list()
        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

def send_updated_dot_list():
    global dot_list
    for client in clients:
        try:
            # Отправляем dot_list в формате JSON
            client.send(json.dumps(dot_list).encode('utf-8'))
        except Exception as e:
            print(f"Error sending data to client: {e}")

# Настройка сервера
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('Noutbuk-Artem.local', 9995))
server.listen(5)
clients = []

print("Server started. Waiting for clients...")

while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()