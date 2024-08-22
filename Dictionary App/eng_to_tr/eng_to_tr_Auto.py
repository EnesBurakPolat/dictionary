import tkinter as tk
from tkinter import filedialog
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

def log_error_and_retry(error_message):
    # Hata mesajını log dosyasına yaz
    with open('error_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{time.ctime()}: {error_message}\n")

    # 3 saniye bekle ve devam et
    time.sleep(3)
    stop_translation_process()
    continue_translation_process()

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
                    return

                word = line.strip()
                if word and word not in translated_words:
                    try:
                        translation = translator.translate(word, dest=target_language).text
                        outfile.write(f"{word.replace(' ', '_')}={translation.replace(' ', '_')}\n")
                    except Exception as e:
                        log_error_and_retry(f"Bir hata oluştu: {e}")
                        return
                
                current_line += 1
                progress = (current_line / total_lines) * 100
                progress_var.set(progress)
                count_label.config(text=f"İşlenen Kelime Sayısı: {current_line} / {total_lines} (Geçmiş: {len(translated_words)})")
                
                elapsed_time = time.time() - start_time
                avg_time_per_line = elapsed_time / current_line if current_line > 0 else 0
                estimated_total_time = avg_time_per_line * total_lines
                remaining_time = estimated_total_time - elapsed_time
                time_label.config(text=f"Geçen Süre: {format_time(elapsed_time)} | Tahmini Kalan Süre: {format_time(remaining_time)}")
                root.update_idletasks()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        formatted_time = format_time(elapsed_time)
        # Başarılı mesajını bir loga veya dosyaya yazabiliriz
        with open('translation_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f"{time.ctime()}: Çeviri tamamlandı! Süre: {formatted_time}\n")
    
    except Exception as e:
        log_error_and_retry(f"Bir hata oluştu: {e}")

def run_translation():
    input_file = input_file_path.get()
    output_file = output_file_path.get()
    
    if input_file and output_file:
        global stop_translation
        stop_translation = False
        translation_thread = threading.Thread(target=translate_file, args=(input_file, output_file))
        translation_thread.start()
        stop_button.config(state=tk.NORMAL)
        continue_button.config(state=tk.DISABLED)
    else:
        # Eksik bilgi varsa, hatayı loga yaz ve durdur
        log_error_and_retry("Eksik Bilgi: Lütfen girdi dosyasını ve çıktı dosyasını seçin.")

def stop_translation_process():
    global stop_translation
    stop_translation = True
    continue_button.config(state=tk.NORMAL)

def continue_translation_process():
    run_translation()

def select_input_file():
    file_path = filedialog.askopenfilename(title="Girdi Dosyasını Seç", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        input_file_path.set(file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Çıktı Dosyasını Seç", defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        output_file_path.set(file_path)

root = tk.Tk()
root.title("Çeviri Programı")
root.geometry("600x500")
root.configure(bg='#282828')

input_file_path = tk.StringVar()
output_file_path = tk.StringVar()

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

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, length=400, variable=progress_var, maximum=100)
progress_bar.pack(pady=10)

count_label = tk.Label(root, text="İşlenen Kelime Sayısı: 0 / 0 (Geçmiş: 0)", bg='#282828', fg='white')
count_label.pack(pady=5)

time_label = tk.Label(root, text="Geçen Süre: 0 saat 0 dakika 0 saniye | Tahmini Kalan Süre: 0 saat 0 dakika 0 saniye", bg='#282828', fg='white')
time_label.pack(pady=5)

root.mainloop()
