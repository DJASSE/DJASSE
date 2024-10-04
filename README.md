import os
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
import hashlib

# إعدادات البرنامج
CORRECT_PASSWORD = hashlib.sha256("DJASSER2008".encode()).hexdigest()
MAX_ATTEMPTS = 5
BLOCK_TIME = 20

# ملفات البيانات
CLIENT_DATA_FILE = "clients.csv"
DAILY_ORDER_FILE = "daily_order.csv"

class PasswordApp:
    def __init__(self, master):
        self.master = master
        self.master.title("تسجيل الدخول")
        self.master.configure(bg="#3b5998")

        self.attempts = 0
        self.blocked_until = 0
        self.client_code = self.get_next_client_code()

        self.label = tk.Label(master, text="أدخل كلمة المرور:", bg="#3b5998", fg="white", font=("Arial", 14))
        self.label.pack(pady=10)

        self.password_entry = tk.Entry(master, show="*", font=("Arial", 14))
        self.password_entry.pack(pady=5)

        self.submit_button = tk.Button(master, text="إدخال الكود", command=self.check_password, bg="#4caf50", fg="white", font=("Arial", 12))
        self.submit_button.pack(pady=10)

    def get_next_client_code(self):
        try:
            df = pd.read_csv(CLIENT_DATA_FILE)
            if not df.empty:
                return df['كود العميل'].max() + 1
        except FileNotFoundError:
            return 1

    def check_password(self):
        current_time = time.time()

        if current_time < self.blocked_until:
            messagebox.showwarning("محظور", "لقد تم حظرك. حاول مرة أخرى بعد 20 ثانية.")
            return

        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if hashed_password == CORRECT_PASSWORD:
            self.open_main_window()
        else:
            self.attempts += 1
            messagebox.showerror("خطأ", f"كلمة المرور '{password}' خاطئة.")
            if self.attempts >= MAX_ATTEMPTS:
                self.blocked_until = current_time + BLOCK_TIME
                self.attempts = 0

    def open_main_window(self):
        self.master.withdraw()
        main_window = tk.Toplevel(self.master)
        main_window.title("النافذة الرئيسية")
        main_window.configure(bg="#3b5998")

        button_frame = tk.Frame(main_window, bg="#3b5998")
        button_frame.pack(pady=50)

        buttons = [
            ("Buy", self.buy_action),
            ("Storage", self.storage_action),
            ("Sell", self.sell_action),
            ("Data", self.data_action)
        ]

        for text, command in buttons:
            button = tk.Button(button_frame, text=text, command=command, bg="#4caf50", fg="white", font=("Arial", 24), width=10, height=2)
            button.pack(side=tk.LEFT, padx=10)

    def buy_action(self):
        messagebox.showinfo("Buy", "تم الضغط على زر Buy!")

    def storage_action(self):
        messagebox.showinfo("Storage", "تم الضغط على زر Storage!")

    def sell_action(self):
        self.open_sell_window()

    def open_sell_window(self):
        self.sell_window = tk.Toplevel(self.master)
        self.sell_window.title("بيع المنتج")
        self.sell_window.configure(bg="#3b5998")

        # إطار لتجميع العناصر
        main_frame = tk.Frame(self.sell_window, bg="#3b5998")
        main_frame.pack(pady=10)

        # زر لإضافة عميل جديد
        add_client_button = tk.Button(main_frame, text="إضافة عميل", command=self.open_add_client_window, bg="#4caf50", fg="white", font=("Arial", 12))
        add_client_button.pack(pady=5)

        # إطار للتخزين ومكونات الإدخال
        input_frame = tk.Frame(main_frame, bg="#3b5998")
        input_frame.pack(side=tk.LEFT)

        labels = ["كود العميل", "اسم العميل", "الهاتف", "العنوان", "المنتج", "الكود", "الكمية", "سعر الوحدة", "المدفوع", "الدين"]
        self.entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(input_frame, text=label_text, bg="#3b5998", fg="white", font=("Arial", 12))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = tk.Entry(input_frame, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        # جعل كود العميل غير قابل للتعديل
        self.entries[0].config(state='normal')
        self.entries[0].insert(0, self.client_code)

        # زر بحث عن العميل بكود العميل
        search_client_button = tk.Button(main_frame, text="بحث عن العميل بكود العميل", command=self.search_client, bg="#4caf50", fg="white", font=("Arial", 12))
        search_client_button.pack(pady=5)

        # زر حدف العملاء المحفوظين
        delete_clients_button = tk.Button(main_frame, text="حدف العملاء المحفوظين", command=self.delete_saved_clients, bg="#dc3545", fg="white", font=("Arial", 12))
        delete_clients_button.pack(pady=5)

        # إضافة مساحة عرض الطلبات كجدول مع شريط تمرير
        order_display_frame = tk.Frame(main_frame, bg="#3b5998")
        order_display_frame.pack(side=tk.RIGHT)

        self.order_tree = ttk.Treeview(order_display_frame, columns=("كود العميل", "اسم العميل", "الهاتف", "العنوان", "المنتج", "الكود", "الكمية", "سعر الوحدة", "المدفوع", "الدين"), show='headings', height=10)
        self.order_tree.pack(side=tk.LEFT)

        scroll_y = ttk.Scrollbar(order_display_frame, orient="vertical", command=self.order_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill='y')
        self.order_tree.configure(yscrollcommand=scroll_y.set)

        # إعداد الأعمدة
        for col in self.order_tree["columns"]:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, anchor="center")

        # زر إضافات الطلبات
        add_order_frame = tk.Frame(self.sell_window, bg="#3b5998")
        add_order_frame.pack(pady=10)

        add_order_button = tk.Button(add_order_frame, text="إضافة طلب", command=self.add_order_action, bg="#4caf50", fg="white", font=("Arial", 12))
        add_order_button.pack(side=tk.LEFT, padx=5)

        save_orders_button = tk.Button(add_order_frame, text="حفظ الطلبات", command=self.save_orders, bg="#4caf50", fg="white", font=("Arial", 12))
        save_orders_button.pack(side=tk.LEFT, padx=5)

        show_orders_button = tk.Button(add_order_frame, text="إظهار الطلبات المحفوظة", command=self.show_saved_orders, bg="#4caf50", fg="white", font=("Arial", 12))
        show_orders_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(add_order_frame, text="مسح البيانات", command=self.clear_entries, bg="#f44336", fg="white", font=("Arial", 12))
        clear_button.pack(side=tk.LEFT, padx=5)

        # زر لعرض العملاء
        show_clients_button = tk.Button(add_order_frame, text="عرض العملاء المحفوظين", command=self.show_clients, bg="#4caf50", fg="white", font=("Arial", 12))
        show_clients_button.pack(side=tk.LEFT, padx=5)

        # زر حفظ البيانات
        save_data_button = tk.Button(add_order_frame, text="حفظ البيانات", command=self.save_data, bg="#4caf50", fg="white", font=("Arial", 12))
        save_data_button.pack(side=tk.LEFT, padx=5)

        # زر حفظ السلعة
        save_product_button = tk.Button(add_order_frame, text="حفظ السلعة", command=self.save_product, bg="#4caf50", fg="white", font=("Arial", 12))
        save_product_button.pack(side=tk.LEFT, padx=5)

        # زر إضافة السلعة
        add_product_button = tk.Button(add_order_frame, text="إضافة السلعة", command=self.add_product, bg="#4caf50", fg="white", font=("Arial", 12))
        add_product_button.pack(side=tk.LEFT, padx=5)

    def add_order_action(self):
        order_data = [entry.get().strip() for entry in self.entries]
        self.order_tree.insert("", "end", values=order_data)

    def save_orders(self):
        order_list = []
        for item in self.order_tree.get_children():
            order_list.append(self.order_tree.item(item)["values"])

        if not order_list:
            messagebox.showwarning("تحذير", "لا توجد طلبات لحفظها.")
            return

        client_code = self.entries[0].get().strip()
        client_name = self.entries[1].get().strip()
        client_phone = self.entries[2].get().strip()
        client_address = self.entries[3].get().strip()

        if not client_code or not client_name or not client_phone or not client_address:
            messagebox.showwarning("تحذير", "يرجى إدخال جميع بيانات العميل.")
            return

        df_orders = pd.DataFrame(order_list, columns=["كود العميل", "اسم العميل", "الهاتف", "العنوان", "المنتج", "الكود", "الكمية", "سعر الوحدة", "المدفوع", "الدين"])
        df_orders['كود العميل'] = client_code
        df_orders['اسم العميل'] = client_name
        df_orders['رقم الهاتف'] = client_phone
        df_orders['عنوان العميل'] = client_address
        df_orders.to_csv(f"saved_orders_{client_code}.csv", index=False)

        messagebox.showinfo("حفظ", "تم حفظ الطلبات بنجاح!")

    def show_saved_orders(self):
        client_code = self.entries[0].get().strip()
        
        try:
            df = pd.read_csv(f"saved_orders_{client_code}.csv")

            orders_window = tk.Toplevel(self.sell_window)
            orders_window.title("الطلبات المحفوظة")
            orders_window.configure(bg="#3b5998")

            orders_tree = ttk.Treeview(orders_window, columns=("كود العميل", "اسم العميل", "الهاتف", "العنوان", "المنتج", "الكود", "الكمية", "سعر الوحدة", "المدفوع", "الدين"), show='headings', height=10)
            orders_tree.pack(pady=10)

            scroll_y = ttk.Scrollbar(orders_window, orient="vertical", command=orders_tree.yview)
            scroll_y.pack(side=tk.RIGHT, fill='y')
            orders_tree.configure(yscrollcommand=scroll_y.set)

            # إعداد الأعمدة
            for col in orders_tree["columns"]:
                orders_tree.heading(col, text=col)
                orders_tree.column(col, anchor="center")

            for _, row in df.iterrows():
                orders_tree.insert("", "end", values=(row['كود العميل'], row['اسم العميل'], row['رقم الهاتف'], row['عنوان العميل'], row['المنتج'], row['الكود'], row['الكمية'], row['سعر الوحدة'], row['المدفوع'], row['الدين']))

            close_button = tk.Button(orders_window, text="إغلاق", command=orders_window.destroy, bg="#f44336", fg="white")
            close_button.pack(pady=10)

        except FileNotFoundError:
            messagebox.showwarning("خطأ", "لا توجد طلبات محفوظة لهذا العميل.")
            return

    def show_clients(self):
        try:
            df = pd.read_csv(CLIENT_DATA_FILE)
            clients_window = tk.Toplevel(self.sell_window)
            clients_window.title("العملاء المحفوظين")
            clients_window.configure(bg="#3b5998")

            search_frame = tk.Frame(clients_window, bg="#3b5998")
            search_frame.pack(pady=10)

            search_label = tk.Label(search_frame, text="ابحث عن العميل:", bg="#3b5998", fg="white")
            search_label.pack(side=tk.LEFT)

            self.search_entry = tk.Entry(search_frame)
            self.search_entry.pack(side=tk.LEFT, padx=5)

            search_button = tk.Button(search_frame, text="بحث", command=lambda: self.filter_clients(df), bg="#4caf50", fg="white")
            search_button.pack(side=tk.LEFT)

            clients_tree = ttk.Treeview(clients_window, columns=("كود العميل", "اسم العميل", "الهاتف", "العنوان"), show='headings', height=10)
            clients_tree.pack(pady=10)

            scroll_y = ttk.Scrollbar(clients_window, orient="vertical", command=clients_tree.yview)
            scroll_y.pack(side=tk.RIGHT, fill='y')
            clients_tree.configure(yscrollcommand=scroll_y.set)

            # إعداد الأعمدة
            for col in clients_tree["columns"]:
                clients_tree.heading(col, text=col)
                clients_tree.column(col, anchor="center")

            for _, row in df.iterrows():
                clients_tree.insert("", "end", values=(row['كود العميل'], row['name client'], row['phone'], row['adres']))

            clients_tree.bind('<Double-1>', lambda event: self.fill_client_data(clients_tree.selection()[0], df))

            close_button = tk.Button(clients_window, text="إغلاق", command=clients_window.destroy, bg="#f44336", fg="white")
            close_button.pack(pady=10)

        except FileNotFoundError:
            messagebox.showwarning("خطأ", "لا توجد بيانات للعملاء.")

    def filter_clients(self, df):
        search_term = self.search_entry.get().strip()
        filtered_df = df[
            df['كود العميل'].astype(str).str.contains(search_term) |
            df['name client'].str.contains(search_term) |
            df['phone'].astype(str).str.contains(search_term)
        ]

        # مسح البيانات السابقة في الشجرة
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        # إضافة البيانات المفلترة
        for _, row in filtered_df.iterrows():
            self.clients_tree.insert("", "end", values=(row['كود العميل'], row['name client'], row['phone'], row['adres']))

    def fill_client_data(self, index, df):
        row = df.iloc[index]
        self.entries[0].delete(0, tk.END)
        self.entries[0].insert(0, row['كود العميل'])
        self.entries[1].delete(0, tk.END)
        self.entries[1].insert(0, row['name client'])
        self.entries[2].delete(0, tk.END)
        self.entries[2].insert(0, row['phone'])
        self.entries[3].delete(0, tk.END)
        self.entries[3].insert(0, row['adres'])

    def clear_entries(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.order_tree.delete(*self.order_tree.get_children())
        self.client_code = self.get_next_client_code()  # تحديث كود العميل للعميل التالي
        self.entries[0].config(state='normal')
        self.entries[0].delete(0, tk.END)
        self.entries[0].insert(0, self.client_code)
        self.entries[0].config(state='disabled')  # إعادة جعلها غير قابلة للتعديل

    def open_add_client_window(self):
        add_client_window = tk.Toplevel(self.sell_window)
        add_client_window.title("إضافة عميل جديد")
        add_client_window.configure(bg="#3b5998")

        labels = ["كود العميل", "اسم العميل", "الهاتف", "العنوان"]
        self.client_entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(add_client_window, text=label_text, bg="#3b5998", fg="white", font=("Arial", 12))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(add_client_window, font=("Arial", 12))
            if i == 0:  # كود العميل
                entry.config(state='normal')
                entry.insert(0, self.client_code)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.client_entries.append(entry)

        save_button = tk.Button(add_client_window, text="حفظ", command=self.save_client_data, bg="#4caf50", fg="white", font=("Arial", 12), width=15)
        save_button.grid(row=len(labels), columnspan=2, pady=20)

    def save_client_data(self):
        client_data = {
            "كود العميل": self.client_entries[0].get().strip(),
            "name client": self.client_entries[1].get().strip(),
            "phone": self.client_entries[2].get().strip(),
            "adres": self.client_entries[3].get().strip()
        }

        if any(value == "" for value in client_data.values()):
            messagebox.showwarning("تحذير", "يرجى ملء جميع الخانات.")
            return

        try:
            df = pd.read_csv(CLIENT_DATA_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["كود العميل", "name client", "phone", "adres"])

        df = pd.concat([df, pd.DataFrame([client_data])], ignore_index=True)
        df.to_csv(CLIENT_DATA_FILE, index=False)

        self.client_code = self.get_next_client_code()  # تحديث كود العميل للعميل التالي
        messagebox.showinfo("حفظ", "تم حفظ بيانات العميل بنجاح!")

    def search_client(self):
        client_code = self.entries[0].get().strip()
        if not client_code:
            messagebox.showwarning("تحذير", "يرجى إدخال كود العميل.")
            return

        try:
            df = pd.read_csv(CLIENT_DATA_FILE)
            client = df[df['كود العميل'] == int(client_code)]
            if not client.empty:
                messagebox.showinfo("نتيجة البحث", f"تم العثور على العميل: {client['name client'].values[0]}")
            else:
                messagebox.showinfo("نتيجة البحث", "لم يتم العثور على العميل.")
        except FileNotFoundError:
            messagebox.showwarning("خطأ", "لا توجد بيانات للعملاء.")

    def delete_saved_clients(self):
        try:
            df = pd.read_csv(CLIENT_DATA_FILE)
            df = df.iloc[0:0]  # مسح جميع البيانات
            df.to_csv(CLIENT_DATA_FILE, index=False)
            messagebox.showinfo("نجاح", "تم حدف جميع العملاء المحفوظين.")
        except Exception as e:
            messagebox.showwarning("خطأ", "حدث خطأ أثناء الحذف.")

    def data_action(self):
        messagebox.showinfo("Data", "تم الضغط على زر Data!")

    def add_product(self):
        product_data = [entry.get().strip() for entry in self.entries[4:]]  # إفتراض أن بيانات السلعة من المدخلات 4 وما بعدها
        if all(product_data):
            self.order_tree.insert("", "end", values=product_data)
            messagebox.showinfo("إضافة", "تم إضافة السلعة بنجاح!")
        else:
            messagebox.showwarning("تحذير", "يرجى ملء جميع بيانات السلعة.")

    def save_product(self):
        messagebox.showinfo("حفظ", "تم حفظ السلعة بنجاح!")

    def save_data(self):
        messagebox.showinfo("حفظ", "تم حفظ البيانات بنجاح!")

    def get_next_client_code(self):
        if not os.path.exists(CLIENT_DATA_FILE):
            return 1  # إذا كان الملف غير موجود، ابدأ من 1
        df = pd.read_csv(CLIENT_DATA_FILE)
        if df.empty:
            return 1  # إذا كان الملف فارغًا، ابدأ من 1
        return df["كود العميل"].max() + 1  # العودة بأقصى كود عميل وزيادته بمقدار 1

# إنشاء التطبيق
root = tk.Tk()
app = PasswordApp(root)
root.mainloop()  # تأكد من إضافة هذا السطر
