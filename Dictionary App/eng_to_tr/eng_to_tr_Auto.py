import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from googletrans import Translator
import time
import threading
import os

# pip install googletrans==4.0.0-rc1
# python -m PyInstaller --onefile --noconsole eng_to_tr_Auto.py

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours} saat {minutes} dakika {secs} saniye"

def read_translated_words(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as outfile:
            lines = outfile.readlines()
            return set(line.split('=')[0] for line in lines)
    return set()

def show_error_and_stop(error_message):
    # Hata mesajını göster ve 3 saniye sonra kapat
    messagebox.showerror("Hata", error_message)
    root.after(3000, lambda: root.quit())  # Hata kutusunu 3 saniye sonra kapat

    # Çeviri işlemini durdur ve otomatik olarak durdur butonuna bas
    root.after(3000, stop_translation_process)
    root.after(4000, continue_translation_process)  # 1 saniye sonra devam ettir

def translate_file(input_file, output_file, target_language='tr'):
    translator = Translator()
    total_lines = sum(1 for line in open(input_file, 'r', encoding='utf-8'))
    
    global stop_translation
    stop_translation = False

    try:
        start_time = time.time()  # Başlangıç zamanını kaydet
        current_line = 0
        translated_words = read_translated_words(output_file)
        
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
            for line in infile:
                if stop_translation:
                    messagebox.showinfo("Durduruldu", "Çeviri işlemi durduruldu.")
                    return

                word = line.strip()
                if word and word not in translated_words:
                    try:
                        # Çeviri yap
                        translation = translator.translate(word, dest=target_language).text
                        outfile.write(f"{word.replace(' ', '_')}={translation.replace(' ', '_')}\n")
                    except Exception as e:
                        # Hata olursa göster ve durdur
                        show_error_and_stop(f"Bir hata oluştu: {e}")
                        return
                
                # İlerleme çubuğunu ve sayaç değerini güncelle
                current_line += 1
                progress = (current_line / total_lines) * 100
                progress_var.set(progress)
                count_label.config(text=f"İşlenen Kelime Sayısı: {current_line} / {total_lines} (Geçmiş: {len(translated_words)})")
                
                # Tahmini kalan süreyi güncelle
                elapsed_time = time.time() - start_time
                avg_time_per_line = elapsed_time / current_line if current_line > 0 else 0
                estimated_total_time = avg_time_per_line * total_lines
                remaining_time = estimated_total_time - elapsed_time
                time_label.config(text=f"Geçen Süre: {format_time(elapsed_time)} | Tahmini Kalan Süre: {format_time(remaining_time)}")
                root.update_idletasks()
        
        end_time = time.time()  # Bitiş zamanını kaydet
        elapsed_time = end_time - start_time
        formatted_time = format_time(elapsed_time)
        messagebox.showinfo("Başarılı", f"Çeviri tamamlandı! Süre: {formatted_time}")
    
    except Exception as e:
        # Hata durumunda göster ve durdur
        show_error_and_stop(f"Bir hata oluştu: {e}")

def run_translation():
    input_file = input_file_path.get()
    output_file = output_file_path.get()
    
    if input_file and output_file:
        global stop_translation
        stop_translation = False
        # Çeviri işlemini ayrı bir iş parçacığında çalıştır
        translation_thread = threading.Thread(target=translate_file, args=(input_file, output_file))
        translation_thread.start()
        stop_button.config(state=tk.NORMAL)  # Durdurma butonunu etkinleştir
        continue_button.config(state=tk.DISABLED)  # Devam Et butonunu devre dışı bırak
    else:
        messagebox.showwarning("Eksik Bilgi", "Lütfen girdi dosyasını ve çıktı dosyasını seçin.")

def stop_translation_process():
    global stop_translation
    stop_translation = True
    continue_button.config(state=tk.NORMAL)  # Devam Et butonunu etkinleştir

def continue_translation_process():
    run_translation()  # Çeviri işlemini yeniden başlat

def select_input_file():
    file_path = filedialog.askopenfilename(title="Girdi Dosyasını Seç", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        input_file_path.set(file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Çıktı Dosyasını Seç", defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        output_file_path.set(file_path)

# Ana pencere
root = tk.Tk()
root.title("Çeviri Programı")
root.geometry("600x500")  # Pencere boyutunu belirle

# Arka plan rengini ayarla
root.configure(bg='#282828')

# Dosya yollarını saklayan değişkenler
input_file_path = tk.StringVar()
output_file_path = tk.StringVar()

# Arayüz elemanları
input_label = tk.Label(root, text="Girdi Dosyası:", bg='#282828', fg='white')
input_label.pack(pady=5)
input_entry = tk.Entry(root, textvariable=input_file_path, width=50)
input_entry.pack(pady=5)
input_button = tk.Button(root, text="Dosya Seç", command=select_input_file, bg='#404040', fg='white')
input_button.pack(pady=5)

output_label = tk.Label(root, text="Çıktı Dosyası:", bg='#282828', fg='white')
output_label.pack(pady=5)
output_entry = tk.Entry(root, textvariable=output_file_path, width=50)
output_entry.pack(pady=5)
output_button = tk.Button(root, text="Kaydet", command=select_output_file, bg='#404040', fg='white')
output_button.pack(pady=5)

translate_button = tk.Button(root, text="Çevir ve Kaydet", command=run_translation, bg='#4CAF50', fg='white')
translate_button.pack(pady=20)

stop_button = tk.Button(root, text="Durdur", command=stop_translation_process, state=tk.DISABLED, bg='red', fg='white')
stop_button.pack(pady=20)

continue_button = tk.Button(root, text="Devam Et", command=continue_translation_process, state=tk.DISABLED, bg='blue', fg='white')
continue_button.pack(pady=20)

# İlerleme çubuğu
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, length=400, variable=progress_var, maximum=100)
progress_bar.pack(pady=10)

# Sayaç etiketi
count_label = tk.Label(root, text="İşlenen Kelime Sayısı: 0 / 0 (Geçmiş: 0)", bg='#282828', fg='white')
count_label.pack(pady=5)

# Geçen süre ve tahmini kalan süre etiketi
time_label = tk.Label(root, text="Geçen Süre: 0 saat 0 dakika 0 saniye | Tahmini Kalan Süre: 0 saat 0 dakika 0 saniye", bg='#282828', fg='white')
time_label.pack(pady=5)

# Pencereyi çalıştır
root.mainloop()
