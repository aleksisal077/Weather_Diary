import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class WeatherJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.records = []
        self.filename = "weather_storage.json"
        
        self.load_from_file(self.filename)
        self.setup_ui()
        self.update_table()
    
    def setup_ui(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление записи", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле Описание
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Поле Осадки
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=4, padx=10, pady=5)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=1, column=4, padx=10, pady=5)
        
        input_frame.columnconfigure(3, weight=1)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(filter_frame, text="Применить", command=self.apply_date_filter).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_date_filter).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по температуре (> °C):").grid(row=1, column=0, padx=5, pady=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(filter_frame, text="Применить", command=self.apply_temp_filter).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_temp_filter).grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопки сохранения и загрузки
        file_frame = ttk.Frame(self.root)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_file_dialog).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_file_dialog).pack(side="left", padx=5)
        
        # Таблица для отображения записей
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=350)
        self.tree.column("precipitation", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_str):
        try:
            temp = float(temp_str)
            return True, temp
        except ValueError:
            return False, None
    
    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        is_valid_temp, temperature = self.validate_temperature(temp_str)
        if not is_valid_temp:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return
        
        record = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.records.append(record)
        self.update_table()
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись добавлена")
    
    def update_table(self, records_to_show=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = records_to_show if records_to_show is not None else self.records
        for record in data:
            self.tree.insert("", tk.END, values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))
    
    def apply_date_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        if not filter_date:
            messagebox.showwarning("Предупреждение", "Введите дату для фильтрации")
            return
        
        if not self.validate_date(filter_date):
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        
        filtered = [r for r in self.records if r["date"] == filter_date]
        self.update_table(filtered)
        
        if not filtered:
            messagebox.showinfo("Информация", "Записей за эту дату не найдено")
    
    def reset_date_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.update_table()
    
    def apply_temp_filter(self):
        filter_temp_str = self.filter_temp_entry.get().strip()
        if not filter_temp_str:
            messagebox.showwarning("Предупреждение", "Введите значение температуры")
            return
        
        is_valid, threshold = self.validate_temperature(filter_temp_str)
        if not is_valid:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        filtered = [r for r in self.records if r["temperature"] > threshold]
        self.update_table(filtered)
        
        if not filtered:
            messagebox.showinfo("Информация", f"Записей с температурой выше {threshold}°C не найдено")
    
    def reset_temp_filter(self):
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
    
    def save_to_file_dialog(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.save_to_file(filepath)
    
    def save_to_file(self, filepath):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_file_dialog(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.load_from_file(filepath)
    
    def load_from_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.update_table()
            messagebox.showinfo("Успех", f"Данные загружены из {filepath}")
        except FileNotFoundError:
            messagebox.showwarning("Предупреждение", "Файл не найден")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Неверный формат JSON")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherJournalApp(root)
    root.mainloop()