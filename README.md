# 🧠 DocuMind AI — Kurumsal RAG Tabanlı Akıllı Doküman Asistanı

**DocuMind AI**, kullanıcıların kendi PDF, Word (`.docx`) ve Metin (`.txt`) dokümanlarını yükleyerek doğal dilde sohbet edebildiği, **sıfır halüsinasyon** prensibiyle çalışan ve her yanıtını **birebir sayfa/paragraf alıntılarıyla** doğrulayan modüler bir **RAG (Retrieval-Augmented Generation)** uygulamasıdır.

## 🚀 Öne Çıkan Özellikler

* **Çoklu Doküman Desteği:** `.pdf`, `.docx` ve `.txt` formatındaki belgeleri otomatik olarak okur ve anlamlı parçalara (chunking) ayırır.
* **Sohbet Hafızası (History-Aware Retriever):** Önceki mesajları hatırlayarak bağlamlı takip sorularını (ör. *"Peki bunların sonuçları nelerdir?"*) otomatik olarak yeniden formüle eder.
* **Halüsinasyon Önleme & Kaynak Doğrulama:** Yalnızca yüklenen belgelerdeki bilgilere dayanarak yanıt verir; her yanıtın altında ilgili dosya adını, sayfa numarasını ve **birebir metin alıntısını** gösterir.
* **Çok Katmanlı Model Yedekleme (Fallback):** Google Gemini (`gemini-3.7-flash`, `gemini-3.1-flash-lite`, `gemini-3.6-flash`) ve `gemma-4-31b-it` modelleri arasında otomatik geçiş yaparak yüksek erişilebilirlik sağlar.
* **Canlı Akış (Streaming) & Raporlama:** Yanıtları kelime kelime canlı olarak akıtır ve sohbet geçmişini tek tıkla `.txt` raporu olarak dışa aktarır.

## 🏗️ Modüler Proje Mimarisi

```text
rag-asistani/
├── data/                   # Yüklenen dokümanların saklandığı dizin
├── src/                    # Çekirdek uygulama modülleri
│   ├── __init__.py
│   ├── config.py           # Ortam değişkenleri ve sistem sabitleri
│   ├── loader.py           # Çoklu format doküman okuyucu ve metin parçalayıcı
│   ├── vector_store.py     # ChromaDB vektör veritabanı yönetimi
│   └── llm_chain.py        # LCEL tabanlı hafızalı RAG ve Fallback zinciri
├── main.py                 # Streamlit web arayüzü
├── requirements.txt        # Bağımlılıklar
└── .env                    # API anahtarı (GitHub'a yüklenmez)
```

## 🛠️ Kurulum ve Çalıştırma

1. **Repoyu klonlayın:**
   ```bash
   git clone https://github.com
   cd rag-asistani
   ```

2. **Sanal ortamı oluşturun ve aktif edin:**
   ```bash
   python -m venv venv
   # Windows (Git Bash):
   source venv/Scripts/activate
   # Mac / Linux:
   source venv/bin/activate
   ```

3. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **API anahtarını tanımlayın:**
   Ana dizinde `.env` adında bir dosya oluşturun ve Google AI Studio anahtarınızı ekleyin:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Uygulamayı başlatın:**
   ```bash
   streamlit run main.py
   ```
