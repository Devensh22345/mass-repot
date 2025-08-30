# utils.py
def save_loop_state(state: bool):
    with open("loop_state.txt", "w") as f:
        f.write("1" if state else "0")

def load_loop_state():
    try:
        with open("loop_state.txt", "r") as f:
            return f.read().strip() == "1"
    except FileNotFoundError:
        return False
