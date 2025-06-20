import dearpygui.dearpygui as dpg
import socket as sk
import numpy as np
import threading
import json

dpg.create_context()
dpg.create_viewport(title="graph", width=500, height=500)

x_base = np.arange(100, dtype=np.float32).tolist()
temp = np.ones(100).tolist()
lux = np.ones(100).tolist()


def get_data():
    global temp, lux, x_base
    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as sock:
        sock.connect(("192.168.4.1", 8888))
        while True:
            data = json.loads(sock.recv(1024).decode())
            temp.append(data[0])
            lux.append(data[1])
            x_base.append(x_base[-1] + 1)
            temp = temp[-20:]
            lux = lux[-20:]
            x_base = x_base[-20:]
            dpg.set_value("temp", (x_base, temp))
            dpg.set_value("temp_l", data[0])
            dpg.set_value("lux", (x_base, lux))
            dpg.set_value("lux_l", data[1])
            dpg.set_axis_limits("x_axis", x_base[0], x_base[-1])


alredy_ran = False


def run(_):
    if not alredy_ran:
        threading.Thread(target=get_data, daemon=True).start()


with dpg.window(tag="main"):
    with dpg.plot(label="Value graphs", height=400, width=400):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
        dpg.add_line_series(
            x_base, temp, label="Temperature", parent="y_axis", tag="temp"
        )
        dpg.add_line_series(x_base, lux, label="LUX", parent="y_axis", tag="lux")

    dpg.add_button(label="connect", callback=run)

    with dpg.group(horizontal=True):
        dpg.add_text(label="[]", tag="temp_l")
        dpg.add_text(label="[]", tag="lux_l")

dpg.set_primary_window("main", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
