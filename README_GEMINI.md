# 🤖 Gemini + MCP Weather Client

Bu proje **Google Gemini AI** ile **MCP (Model Context Protocol) Weather Server** entegrasyonu yaparak akıllı hava durumu asistanı oluşturur.

## 🌟 Özellikler

- 🧠 **Gemini AI** ile doğal dil anlama
- 🌤️ **Gerçek zamanlı hava durumu** (US National Weather Service)
- 🔧 **Function Calling** ile otomatik tool kullanımı
- 💬 **Konuşma tabanlı** arayüz
- 🔗 **MCP protokolü** ile modüler yapı

## 🏗️ Sistem Mimarisi

```
User Input → Gemini AI → Function Calls → MCP Weather Server → NWS API → Response
```

### Bileşenler:
- **`gemini_client.py`**: Ana Gemini + MCP entegrasyon client'ı
- **`client.py`**: MCP Weather client (mevcut)
- **`weather-server-python/weather.py`**: MCP Weather server
- **`setup_gemini.py`**: Kurulum scripti

## 🚀 Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Google AI API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikey)'dan API key alın
2. Environment variable olarak ayarlayın:

**Windows:**
```cmd
set GOOGLE_AI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GOOGLE_AI_API_KEY=your_api_key_here
```

### 3. Otomatik Setup
```bash
python setup_gemini.py
```

## 🎯 Kullanım

### Basit Başlatma
```bash
python gemini_client.py
```

### Örnek Sohbet

```
You: Houston'da hava nasıl?
🤖 Gemini: Houston'da bugün güneşli ve sıcak! Maksimum sıcaklık 95°F (35°C) olacak...

You: Yarın New York'ta yağmur yağacak mı?
🤖 Gemini: New York için hava tahminini kontrol ediyorum...
🔧 Calling weather tool: get_forecast({'latitude': 40.7128, 'longitude': -74.006})
🤖 Gemini: Yarın New York'ta %60 yağmur ihtimali var. Şemsiye almanı öneririm!

You: California'da hava uyarısı var mı?
🤖 Gemini: California için aktif hava uyarılarını kontrol ediyorum...
🔧 Calling weather tool: get_alerts({'state': 'CA'})
🤖 Gemini: Şu anda California için aktif hava uyarısı bulunmuyor.
```

## 🛠️ Teknik Detaylar

### Function Calling Schema
MCP tools otomatik olarak Gemini function format'ına dönüştürülür:

```python
# MCP Tool
{
    "name": "get_forecast",
    "description": "Get weather forecast for a location",
    "inputSchema": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        }
    }
}

# Gemini Function
{
    "name": "get_forecast", 
    "description": "Get weather forecast for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number", "description": ""},
            "longitude": {"type": "number", "description": ""}
        },
        "required": ["latitude", "longitude"]
    }
}
```

### Desteklenen Şehirler
ABD'nin tüm büyük şehirleri desteklenir:
- New York, Los Angeles, Chicago, Houston
- Seattle, San Francisco, Boston, Miami
- Ve 30+ şehir daha...

### Hava Uyarıları
ABD eyalet kodları ile:
- CA (California)
- NY (New York) 
- TX (Texas)
- FL (Florida)
- Vb...

## 🔧 Geliştirme

### Debug Mode
```python
# gemini_client.py içinde
print(f'🔧 Calling weather tool: {function_name}({function_args})')
```

### Yeni Tool Ekleme
1. MCP server'a yeni tool ekle
2. Schema otomatik olarak Gemini'ye aktarılır
3. Gemini function calling ile kullanabilir

## 🤝 Katkı

1. Fork yapın
2. Feature branch oluşturun
3. Commit yapın
4. Pull request gönderin

## 📝 Lisans

MIT License

## 🆘 Sorun Giderme

### API Key Hataları
```
❌ Please set GOOGLE_AI_API_KEY environment variable
```
→ API key'i environment variable olarak ayarlayın

### MCP Bağlantı Hataları
```
❌ Weather server connection failed
```
→ `weather-server-python/weather.py` dosyasının var olduğundan emin olun

### Import Hataları
```
ModuleNotFoundError: No module named 'google.generativeai'
```
→ `pip install -r requirements.txt` çalıştırın

## 🌐 Kaynaklar

- [Google AI Studio](https://aistudio.google.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [National Weather Service API](https://api.weather.gov/)
