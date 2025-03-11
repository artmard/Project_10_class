

import socket
import threading
import json

# Двумерный массив для хранения dot_list
dot_list = [[-100,-100,-100],[-100,-100,-100],[-100,-100,-100]]

# Настройки сервера
HOST = 'Noutbuk-Artem.local'
PORT = 12346


# Словарь для хранения комнат
rooms = {}
room_counter = 0
clients = {}

def handle_client(client_socket, room_id):
    global dot_list
    global rooms
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
                rooms[room_id]['messages'].append(new_array)
                dot_list.append(new_array)
                print(f"Updated dot_list: {dot_list}")
                # Отправляем обновленный dot_list обратно всем клиентам
                send_updated_dot_list(room_id)
        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

def send_updated_dot_list(room_id):
    global rooms
    global dot_list
    for client in rooms[room_id]['clients']:
        try:
            # Отправляем dot_list в формате JSON
            client.send(json.dumps(rooms[room_id]['messages']).encode('utf-8'))
        except Exception as e:
            print(f"Error sending data to client: {e}")

def accept_connections(server_socket):
    global room_counter
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Подключен клиент: {addr}")

        # Найти или создать комнату
        if room_counter not in rooms or len(rooms[room_counter]['clients']) >= 2:
            room_counter += 1  # Создать новую комнату, если текущая заполнена
            rooms[room_counter] = {'clients': [], 'messages': []}
        
        # Добавление клиента в комнату
        rooms[room_counter]['clients'].append(client_socket)

        # Запуск потока для обработки клиента
        threading.Thread(target=handle_client, args=(client_socket, room_counter)).start()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Сервер запущен на {HOST}:{PORT}")
    
    accept_connections(server_socket)

if __name__ == "__main__":
    start_server()