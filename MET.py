- import tkinter as tk

def on_button_click():
    label.config(text="Button clicked!")

# إنشاء نافذة التطبيق
root = tk.Tk()
root.title("My Tkinter Application")

# إضافة مكونات
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=20)

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=20)

# تشغيل التطبيق
root.mainloop()
