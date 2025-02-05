## Installation and Setup Guide

### Prerequisites

1. Required Software:
   - Python 3.8 veya üzeri (https://www.python.org/downloads/)
   - Visual Studio Code (https://code.visualstudio.com/)
   - Git (https://git-scm.com/downloads)

2. VS Code Eklentileri:
   - Python (Microsoft)
   - Python Extension Pack
   - Pylance
   - Python Indent
   - Python Environment Manager

### Python Kütüphaneleri Kurulumu

1. Temel Kütüphaneler:
   ```bash
   pip install flask werkzeug pandas numpy pillow
   ```

2. Yapay Zeka ve Makine Öğrenmesi Kütüphaneleri:
   ```bash
   pip install google-generativeai torch transformers scikit-learn
   ```

3. Veritabanı ve Güvenlik Kütüphaneleri:
   ```bash
   pip install python-dotenv supabase
   ```

4. Görüntü İşleme Kütüphaneleri:
   ```bash
   pip install opencv-python matplotlib
   ```

### Tek Komutla Tüm Kütüphanelerin Kurulumu:
```bash
pip install flask werkzeug pandas numpy pillow google-generativeai torch transformers python-dotenv supabase opencv-python matplotlib scikit-learn
```

### Çevre Değişkenleri Ayarları

1. Proje klasöründe `.env` dosyası oluşturun
2. Aşağıdaki değişkenleri ekleyin:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### Veri Setleri ve Model Dosyaları

Aşağıdaki klasörlerin ve dosyaların mevcut olduğundan emin olun:
- `datasets/`
  - symtoms_df.csv
  - precautions_df.csv
  - workout_df.csv
  - description.csv
  - medications.csv
  - diets.csv
- `models/`
  - svc.pkl

### Uygulamayı Çalıştırma

1. VS Code'da Projeyi Açın:
   - VS Code'u başlatın
   - File > Open Folder
   - Proje klasörünü seçin

2. Terminal'de Uygulamayı Başlatın:
   ```bash
   cd "path/to/Diagnosia"
   python main.py
   ```

3. Tarayıcıda Görüntüleme:
   - Web tarayıcınızı açın
   - http://localhost:5000 adresine gidin

### Sorun Giderme

Sık Karşılaşılan Sorunlar ve Çözümleri:

1. ModuleNotFoundError:
   - Gerekli kütüphaneleri yeniden yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Port Hatası:
   - 5000 portu kullanımdaysa, main.py dosyasında port numarasını değiştirin
   - Başka uygulamaları kapatın

3. Model Dosyası Hatası:
   - models/ klasöründe svc.pkl dosyasının varlığını kontrol edin

4. Veri Seti Hataları:
   - datasets/ klasöründeki tüm CSV dosyalarının varlığını kontrol edin

5. API Key Hatası:
   - .env dosyasındaki API anahtarlarının doğruluğunu kontrol edin

Yardım ve Destek:
- Hata mesajlarını detaylı bir şekilde paylaşın
- Sistem bilgilerinizi (Python versiyonu, işletim sistemi) belirtin
- Hata aldığınız adımı açıkça belirtin

Not: Tüm komutları Windows PowerShell veya Command Prompt'ta çalıştırın.
