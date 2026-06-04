import socket

# Получаем имя хоста, а затем его IP-адрес
my_ip = socket.gethostbyname(socket.gethostname())

print(f"My IP is: {my_ip}")
