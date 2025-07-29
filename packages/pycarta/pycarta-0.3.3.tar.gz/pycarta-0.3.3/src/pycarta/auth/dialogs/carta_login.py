import tkinter as tk
from tkinter import simpledialog


class CartaLogin(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Username:").grid(row=0)
        tk.Label(master, text="Password:").grid(row=1)

        self.username_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        return self.username_entry  # initial focus

    def apply(self):
        self.result = {
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
        }


def prompt_login():
    root = tk.Tk()
    root.withdraw()  # Hide the main root window
    dialog = CartaLogin(root, title="Carta Login")
    root.destroy()  # Only destroy AFTER dialog closes
    return dialog.result


# Example usage
if __name__ == "__main__":
    import json
    print(json.dumps(prompt_login()))
    