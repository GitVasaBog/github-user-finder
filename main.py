import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        
        # Загрузка избранных
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Поле для поиска
        tk.Label(self.root, text="Введите имя пользователя GitHub:", font=("Arial", 12)).pack(pady=10)
        
        self.search_entry = tk.Entry(self.root, width=40, font=("Arial", 11))
        self.search_entry.pack(pady=5)
        
        self.search_btn = tk.Button(self.root, text="Найти", command=self.search_user, bg="green", fg="white")
        self.search_btn.pack(pady=5)
        
        # Список избранных
        tk.Label(self.root, text="Избранные пользователи:", font=("Arial", 12)).pack(pady=10)
        
        self.favorites_listbox = tk.Listbox(self.root, height=6)
        self.favorites_listbox.pack(fill=tk.X, padx=20, pady=5)
        self.favorites_listbox.bind('<<ListboxSelect>>', self.load_favorite)
        
        # Кнопки для избранного
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        self.add_btn = tk.Button(btn_frame, text="Добавить в избранное", command=self.add_to_favorites, state="disabled")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = tk.Button(btn_frame, text="Удалить из избранного", command=self.remove_from_favorites)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Информация о пользователе
        self.info_text = tk.Text(self.root, height=15, width=60)
        self.info_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Статус
        self.status_label = tk.Label(self.root, text="Готов к работе", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Обновление списка избранных
        self.update_favorites_list()
    
    def search_user(self):
        username = self.search_entry.get().strip()
        
        # Проверка - не пустое ли поле
        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не может быть пустым!")
            return
        
        self.status_label.config(text=f"Поиск пользователя {username}...")
        self.search_btn.config(state="disabled", text="Ищу...")
        
        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)
            
            if response.status_code == 200:
                user = response.json()
                self.show_user_info(user)
                self.add_btn.config(state="normal")
                self.current_user = username
                self.status_label.config(text=f"Пользователь {username} найден!")
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден!")
                self.status_label.config(text="Пользователь не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
            self.status_label.config(text="Ошибка соединения")
        
        self.search_btn.config(state="normal", text="Найти")
    
    def show_user_info(self, user):
        self.info_text.delete(1.0, tk.END)
        
        info = f"""
📌 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ
{'='*40}

👤 Логин: {user.get('login', 'Нет данных')}
📛 Имя: {user.get('name', 'Нет данных')}
🏢 Компания: {user.get('company', 'Нет данных')}
📍 Локация: {user.get('location', 'Нет данных')}
📧 Email: {user.get('email', 'Нет данных')}
📚 Репозиториев: {user.get('public_repos', '0')}
👥 Подписчиков: {user.get('followers', '0')}
👥 Подписок: {user.get('following', '0')}
🔗 Профиль: {user.get('html_url', 'Нет данных')}
📅 Создан: {user.get('created_at', 'Нет данных')[:10]}
        """
        
        self.info_text.insert(1.0, info)
    
    def add_to_favorites(self):
        if hasattr(self, 'current_user') and self.current_user:
            if self.current_user not in self.favorites:
                self.favorites.append(self.current_user)
                self.save_favorites()
                self.update_favorites_list()
                messagebox.showinfo("Успех", f"{self.current_user} добавлен в избранное!")
            else:
                messagebox.showinfo("Информация", "Пользователь уже в избранном")
    
    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if selection:
            username = self.favorites_listbox.get(selection[0])
            self.favorites.remove(username)
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Успех", f"{username} удален из избранного")
    
    def load_favorite(self, event):
        selection = self.favorites_listbox.curselection()
        if selection:
            username = self.favorites_listbox.get(selection[0])
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, username)
            self.search_user()
    
    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user)
    
    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

# Запуск программы
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()