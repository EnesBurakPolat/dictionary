import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def translate_file(input_file, output_file):
    translations = {}
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                word = line.strip()
                if word:
                    # Kullanıcıdan çeviri al
                    translation = simpledialog.askstring("Çeviri", f"{word} kelimesinin Türkçe karşılığını girin:")
                    if translation:
                        translations[word] = translation
        
        # Çevirileri dosyaya yaz
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for english, turkish in translations.items():
                outfile.write(f"{english.replace(' ', '_')}={turkish.replace(' ', '_')}\n")
        messagebox.showinfo("Başarılı", "Dosya başarıyla kaydedildi!")
    
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

def select_input_file():
    file_path = filedialog.askopenfilename(title="Girdi Dosyasını Seç", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        input_file_path.set(file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Çıktı Dosyasını Seç", defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        output_file_path.set(file_path)

def start_translation():
    input_file = input_file_path.get()
    output_file = output_file_path.get()
    
    if input_file and output_file:
        translate_file(input_file, output_file)
    else:
        messagebox.showwarning("Eksik Bilgi", "Lütfen girdi dosyasını ve çıktı dosyasını seçin.")

# Ana pencere
root = tk.Tk()
root.title("Çeviri Programı")

# Dosya yollarını saklayan değişkenler
input_file_path = tk.StringVar()
output_file_path = tk.StringVar()

# Arayüz elemanları
input_label = tk.Label(root, text="Girdi Dosyası:")
input_label.pack(pady=5)
input_entry = tk.Entry(root, textvariable=input_file_path, width=50)
input_entry.pack(pady=5)
input_button = tk.Button(root, text="Dosya Seç", command=select_input_file)
input_button.pack(pady=5)

output_label = tk.Label(root, text="Çıktı Dosyası:")
output_label.pack(pady=5)
output_entry = tk.Entry(root, textvariable=output_file_path, width=50)
output_entry.pack(pady=5)
output_button = tk.Button(root, text="Kaydet", command=select_output_file)
output_button.pack(pady=5)

translate_button = tk.Button(root, text="Çevir ve Kaydet", command=start_translation)
translate_button.pack(pady=20)

# Pencereyi çalıştır
root.mainloop()
