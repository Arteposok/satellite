import socket
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
import json

c = Console()

def test():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((c.input("[bold]IP adress[/bold] > "), 8888))
        with Live(Panel("Temp, Lux", title="Data"), refresh_per_second=2) as live:
            while True:
                x = s.recv(1024).decode()
                obj = json.loads(x)
                live.update(Panel(f"{obj[0]} C \t {obj[1]} ~lux", title="Data"))


test()
