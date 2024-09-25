from pathlib import Path
import subprocess
from tkinter import Tk, Canvas, Button, PhotoImage
from tkinter import messagebox

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"rules\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window_width = 720
window_height = 480
window.geometry("720x480")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

window.attributes('-topmost', True)
window.focus_force()

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 480,
    width = 720,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("pravila.png"))
image_1 = canvas.create_image(
    361.47264895213834,
    241.00000000536863,
    image=image_image_1
)
def menu():
    window.destroy()
    subprocess.Popen(['python', 'menu.py'])
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda:(menu()),
    relief="flat"
)
button_1.place(
    x=550.0,
    y=73.0,
    width=119.0,
    height=33.0
)


window.resizable(False, False)
window.mainloop()
