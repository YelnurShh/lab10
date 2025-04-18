import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(
        database="phonebook_db",
        user="postgres",
        password="", 
        host="localhost",
        port="5432"
    )

def load_csv_to_db():
    try:
        df = pd.read_csv('/Users/elnrsahar/Desktop/Python tasks/lab10/phone_book/contacts.csv')
        conn = get_connection()
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO contacts (id, name, phone, email)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['name'], row['phone'], row['email']))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Сәтті", "CSV файл жүктелді!")
        show_all_contacts()
    except Exception as e:
        messagebox.showerror("Қате", str(e))

def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, email FROM contacts ORDER BY id")
    rows = cur.fetchall()
    update_tree(rows)
    cur.close()
    conn.close()

def update_tree(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", tk.END, values=row)

def search_contact():
    name = entry_search.get()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, email FROM contacts WHERE name ILIKE %s", ('%' + name + '%',))
    rows = cur.fetchall()
    update_tree(rows)
    cur.close()
    conn.close()

def add_contact():
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()
    if not name or not phone:
        messagebox.showerror("Қате", "Аты мен телефоны міндетті!")
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)", (name, phone, email))
    conn.commit()
    cur.close()
    conn.close()
    messagebox.showinfo("Сәтті", "Контакт қосылды!")
    show_all_contacts()

def delete_contact():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Қате", "Контакт таңдаңыз!")
        return
    item = tree.item(selected[0])
    contact_id = item['values'][0]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    conn.commit()
    cur.close()
    conn.close()
    messagebox.showinfo("Сәтті", "Контакт өшірілді!")
    show_all_contacts()

def update_contact():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Қате", "Контакт таңдаңыз!")
        return
    item = tree.item(selected[0])
    contact_id = item['values'][0]
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()
    if not name or not phone:
        messagebox.showerror("Қате", "Аты мен телефоны міндетті!")
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE contacts SET name=%s, phone=%s, email=%s WHERE id=%s
    """, (name, phone, email, contact_id))
    conn.commit()
    cur.close()
    conn.close()
    messagebox.showinfo("Сәтті", "Контакт жаңартылды!")
    show_all_contacts()

root = tk.Tk()
root.title("📒 Phonebook")
root.geometry("750x500")

tk.Label(root, text="Іздеу (ат бойынша):").pack()
entry_search = tk.Entry(root, width=40)
entry_search.pack()
tk.Button(root, text="Іздеу", command=search_contact).pack(pady=5)

tk.Button(root, text="📥 CSV жүктеу", command=load_csv_to_db).pack()

columns = ("ID", "Аты", "Телефон", "Email")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(expand=True, fill=tk.BOTH)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Аты:").grid(row=0, column=0)
entry_name = tk.Entry(frame)
entry_name.grid(row=0, column=1)

tk.Label(frame, text="Телефон:").grid(row=0, column=2)
entry_phone = tk.Entry(frame)
entry_phone.grid(row=0, column=3)

tk.Label(frame, text="Email:").grid(row=0, column=4)
entry_email = tk.Entry(frame)
entry_email.grid(row=0, column=5)

tk.Button(root, text="➕ Қосу", command=add_contact).pack(pady=2)
tk.Button(root, text="♻️ Жаңарту", command=update_contact).pack(pady=2)
tk.Button(root, text="❌ Өшіру", command=delete_contact).pack(pady=2)
tk.Button(root, text="📃 Барлығын көрсету", command=show_all_contacts).pack(pady=5)

show_all_contacts()

root.mainloop()
