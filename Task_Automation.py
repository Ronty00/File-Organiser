import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import time
import threading
import json
import schedule

data_file = "undo_data.json"

# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer & Maintenance")
        self.geometry("600x400")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text="Select a folder to organize:", font=("Arial", 14))
        self.label.pack(pady=10)

        self.folder_path = tk.StringVar()
        self.path_entry = ctk.CTkEntry(self, textvariable=self.folder_path, width=350, font=("Arial", 12))
        self.path_entry.pack(pady=5)

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.select_folder)
        self.browse_button.pack(pady=5)

        self.organize_button = ctk.CTkButton(self, text="Organize Files", command=self.organize_files, fg_color="green")
        self.organize_button.pack(pady=10)

        self.undo_button = ctk.CTkButton(self, text="Undo Last Action", command=self.undo_last_action, fg_color="red")
        self.undo_button.pack(pady=5)

        self.clean_button = ctk.CTkButton(self, text="Clean System", command=self.clean_system, fg_color="blue")
        self.clean_button.pack(pady=5)

        self.progress = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="yellow")
        self.status_label.pack()

        self.setup_scheduler()

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def organize_files(self):
        folder_to_organize = self.folder_path.get()
        if not folder_to_organize:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        file_categories = {
            "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov"],
            "Music": [".mp3", ".wav", ".flac"],
            "Archives": [".zip", ".rar", ".tar", ".gz"],
            "Programs": [".exe", ".msi"],
            "Scripts": [".py", ".sh", ".bat"],
            "JSON": [".json"],
            "Others": []
        }

        moved_files = []
        total_files = len(os.listdir(folder_to_organize))
        self.progress["maximum"] = total_files
        
        for category in file_categories.keys():
            category_path = os.path.join(folder_to_organize, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

        for i, file in enumerate(os.listdir(folder_to_organize)):
            file_path = os.path.join(folder_to_organize, file)
            if os.path.isdir(file_path):
                continue

            file_moved = False
            for category, extensions in file_categories.items():
                if file.lower().endswith(tuple(extensions)):
                    dest_path = os.path.join(folder_to_organize, category, file)
                    shutil.move(file_path, dest_path)
                    moved_files.append((file_path, dest_path))
                    file_moved = True
                    break

            if not file_moved:
                dest_path = os.path.join(folder_to_organize, "Others", file)
                shutil.move(file_path, dest_path)
                moved_files.append((file_path, dest_path))
            
            self.progress["value"] = i + 1
            self.update()
            time.sleep(0.1)

        with open(data_file, "w") as f:
            json.dump(moved_files, f)
        
        self.status_label.configure(text="✅ Organization Complete!", text_color="lightgreen")
        messagebox.showinfo("Success", "Files have been successfully organized!")

    def undo_last_action(self):
        if not os.path.exists(data_file):
            messagebox.showerror("Error", "No undo data available.")
            return
        
        with open(data_file, "r") as f:
            moved_files = json.load(f)

        for src, dest in moved_files[::-1]:
            shutil.move(dest, src)
        
        os.remove(data_file)
        self.status_label.configure(text="🔄 Undo Complete!", text_color="orange")
        messagebox.showinfo("Undo", "Files have been restored to original locations.")
    
    def clean_system(self):
        temp_folders = [r"C:/Windows/Temp", r"C:/Users/Public/Temp"]
        deleted_files = 0

        for temp_folder in temp_folders:
            if os.path.exists(temp_folder):
                for file in os.listdir(temp_folder):
                    file_path = os.path.join(temp_folder, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            deleted_files += 1
                    except:
                        pass
        
        self.status_label.configure(text=f"🧹 Cleaned {deleted_files} temp files!", text_color="lightblue")
        messagebox.showinfo("System Cleaned", f"Removed {deleted_files} temporary files.")
    
    def setup_scheduler(self):
        schedule.every().day.at("00:00").do(self.organize_files)
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        threading.Thread(target=run_scheduler, daemon=True).start()

# Run the application
if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
