import socket
from rich.panel import Panel
from rich.live import Live
import json

def test():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((input("IP adress > "), 8888))
        with Live(Panel("Temp, Lux"), refresh_per_second=2) as live:
            while True:
                x = s.recv(1024).decode()
                obj = json.loads(x)
                live.update(Panel(f"{obj[0]} C \t {obj[1]} ~lux"))


test()
