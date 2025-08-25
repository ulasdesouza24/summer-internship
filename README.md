# 🌤️ Gemini + MCP Weather Assistant

Bu proje **Google Gemini AI** ile **MCP (Model Context Protocol)** entegrasyonu yaparak gelişmiş bir hava durumu asistanı oluşturur. MCP standardına tam uyumlu, gerçek zamanlı hava durumu verisi sağlar.

## 🏗️ Mimari

### MCP (Model Context Protocol) Yapısı

Bu proje [MCP standardını](https://modelcontextprotocol.io/) tam olarak korur ve şu katılımcıları içerir:

#### **MCP Host** 
- **Dosya**: `web_app.py` / `ultra_simple_app.py`
- **Rol**: AI uygulaması olarak MCP client'ları koordine eder
- **Teknoloji**: FastAPI / Flask web uygulaması

#### **MCP Client**
- **Dosya**: `client.py` → `MCPClient` sınıfı
- **Rol**: MCP server'a bağlanır ve context alır
- **Protokol**: JSON-RPC 2.0 ile dedicated one-to-one connection
- **Entegrasyon**: `gemini_client.py` ile Gemini AI'ye context sağlar

#### **MCP Server**
- **Dosya**: `weather-server-python/weather.py`  
- **Rol**: Weather context provider
- **Framework**: FastMCP
- **Veri Kaynağı**: US National Weather Service API

### Veri Akışı

```
Web Interface (MCP Host)
    ↓
Gemini AI + MCP Client (MCP Client)  
    ↓ JSON-RPC 2.0
Weather Server (MCP Server)
    ↓ HTTPS
National Weather Service API
```

## 🌟 Özellikler

### 🤖 **Akıllı Hava Durumu Asistanı**
- **Doğal dil anlama**: "Yarın Seattle'da yağmur yağacak mı?" tarzı sorular
- **Bağlamsal yanıtlar**: Ham weather data yerine kullanıcı sorusuna özel cevaplar
- **Pratik öneriler**: Şemsiye, kıyafet, aktivite önerileri

### 🌤️ **Gerçek Zamanlı Weather Data**
- **35+ US şehri** desteği
- **Weather alerts** (50 eyalet)
- **5 günlük tahmin**
- **National Weather Service** resmi verisi

### 💻 **Modern Web Arayüzü**
- **Responsive design**
- **Chat interface**
- **Örnek sorular** (quick start)
- **Real-time responses**

### 🔧 **MCP Tools**
- `get_forecast(latitude, longitude)`: Hava durumu tahmini
- `get_alerts(state)`: Weather alerts/warnings

## 🚀 Kurulum

### 1. Gereksinimler
```bash
git clone <repository>
cd mcp-gemini-client
pip install -r requirements.txt
```

### 2. Google AI API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikey)'dan API key alın
2. `.env` dosyası oluşturun:
```env
GOOGLE_AI_API_KEY=your_api_key_here
DEBUG_MODE=false
```

### 3. Otomatik Setup
```bash
python setup_gemini.py
```

## 📱 Kullanım

### Web Arayüzü (Önerilen)

#### FastAPI Versiyonu
```bash
python web_app.py
```
**URL**: http://localhost:8000

#### Ultra Simple Flask Versiyonu  
```bash
python ultra_simple_app.py
```
**URL**: http://localhost:3000

### Komut Satırı
```bash
# Terminal chat
python gemini_client.py

# Demo mode
python demo_gemini_weather.py --demo

# İnteraktif mode
python demo_gemini_weather.py
```

## 💬 Örnek Sohbet

```
You: Should I bring umbrella in New York tonight?
🤖 Gemini: New York için hava durumunu kontrol ediyorum...
🔧 Calling weather tool: get_forecast({'latitude': 40.7128, 'longitude': -74.006})
🤖 Gemini: Tonight in New York there's only a 20% chance of rain with mostly cloudy skies. You probably won't need an umbrella, but it might be worth bringing a light jacket since it'll be around 70°F! 🌃

You: What should I wear in Houston today?
🤖 Gemini: Houston'da bugün çok sıcak olacak! Maksimum 95°F (35°C) güneşli hava. Hafif, nefes alabilir kıyafetler ve bol su içmeyi öneririm! ☀️🥤

You: Any storms coming to Texas?
🤖 Gemini: Texas için weather alert'lerini kontrol ediyorum...
🔧 Calling weather tool: get_alerts({'state': 'TX'})
🤖 Gemini: Currently there's a flood advisory in the Texas Panhandle area, but the Houston area looks clear. Stay safe and avoid flooded roads! 🌊⚠️
```

## 🛠️ Teknik Detaylar

### MCP Protocol Implementation
- **JSON-RPC 2.0** ile tam uyumlu communication
- **Tool calling** automatic schema conversion
- **Error handling** ve connection management
- **Async/await** pattern ile performans

### Desteklenen Şehirler
```
🇺🇸 Major Cities:
New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia

🇺🇸 West Coast:  
San Francisco, Seattle, Portland, Las Vegas, Denver, Sacramento

🇺🇸 South:
Austin, Jacksonville, Charlotte, Fort Worth, El Paso, Memphis, Nashville, Atlanta, Miami

🇺🇸 Midwest/Northeast:
Detroit, Columbus, Milwaukee, Kansas City, Omaha, Boston, Baltimore, Washington

🇺🇸 Southwest:
Albuquerque, Tucson, Colorado Springs, Oklahoma City, Mesa, Virginia Beach
```

### Weather Alerts
Tüm 50 US eyaleti için:
- **Flood warnings**
- **Storm alerts** 
- **Air quality alerts**
- **Severe weather notifications**

## 🧪 Test

### Entegrasyon Testleri
```bash
python test_gemini_integration.py
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Manual Test
```bash  
python quick_test.py
```

## 📂 Proje Yapısı

```
mcp-gemini-client/
├── 📄 README.md                     # Bu dosya
├── 🐍 gemini_client.py             # Ana Gemini + MCP entegrasyon
├── 🐍 client.py                    # MCP Weather client  
├── 🐍 web_app.py                   # FastAPI web arayüzü
├── 🐍 ultra_simple_app.py          # Basit Flask alternatifi
├── 🐍 demo_gemini_weather.py       # Demo ve interaktif mod
├── 🐍 setup_gemini.py              # Kurulum scripti
├── 🐍 test_gemini_integration.py   # Test suite
├── 📋 requirements.txt             # Python bağımlılıkları
├── 🔐 .env                         # API keys (create this)
├── weather-server-python/          # MCP Weather Server
│   ├── 🐍 weather.py              # FastMCP server
│   └── 📋 pyproject.toml          # Server dependencies
└── testsprite_tests/               # Test results
```

## 🔧 Geliştirme

### Yeni MCP Tool Ekleme
1. `weather-server-python/weather.py`'ye yeni tool ekleyin
2. Schema otomatik olarak Gemini'ye aktarılır
3. `gemini_client.py`'de handler ekleyin (isteğe bağlı)

### Debug Mode
```env
DEBUG_MODE=true
```

### Custom Prompts
`gemini_client.py` → `_generate_intelligent_response()` metodunu düzenleyin

## 🤝 Katkı

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

MIT License - detaylar için `LICENSE` dosyasına bakın.

## 🆘 Sorun Giderme

### API Key Hataları
```
❌ Please set GOOGLE_AI_API_KEY environment variable
```
**Çözüm**: `.env` dosyasında API key'i ayarlayın

### MCP Bağlantı Hataları  
```
❌ Weather server connection failed
```
**Çözüm**: `weather-server-python/weather.py` dosyasının var olduğundan emin olun

### Import Hataları
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Çözüm**: `pip install -r requirements.txt` çalıştırın

### Web App Çalışmıyor
1. `python quick_test.py` ile temel işlevselliği test edin
2. Browser Developer Tools → Console'da JavaScript hatalarını kontrol edin
3. `ultra_simple_app.py` alternatifini deneyin

## 🌐 Kaynaklar

- **[MCP Protocol](https://modelcontextprotocol.io/)** - Model Context Protocol Documentation
- **[Google AI Studio](https://aistudio.google.com/)** - Gemini API Key
- **[National Weather Service API](https://api.weather.gov/)** - Weather Data Source
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python MCP Server Framework

## 🎯 Gelecek Planlar

- [ ] Uluslararası şehir desteği
- [ ] Weather haritaları entegrasyonu  
- [ ] Sesli asistan desteği
- [ ] Mobile app versiyonu
- [ ] Historical weather data
- [ ] Weather-based activity recommendations

---

**⭐ Bu projeyi beğendiyseniz star vermeyi unutmayın!**

**🐛 Bug bulursanız veya öneriniz varsa issue açın!**

**🤖 Powered by Gemini AI + MCP Protocol + Real Weather Data** 🌤️
