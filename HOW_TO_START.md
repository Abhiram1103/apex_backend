# QUICK START GUIDE - 3 Easy Options

## ⚡ FASTEST - Manual Start (Recommended)

Open **3 separate PowerShell terminals** and run:

### Terminal 1:
```powershell
python main.py
```

### Terminal 2:
```powershell
python skill_gap_api.py
```

### Terminal 3:
```powershell
python chatbot_api.py
```

**Wait times:**
- Job API: ~10 seconds → Look for "Uvicorn running"
- Skill Gap API: ~10 seconds → Look for "Uvicorn running"  
- Chatbot API: ~60-90 seconds → Look for "✅ All models loaded successfully!"

---

## 🚀 Option 2 - Simple Launcher

Run this to open 3 terminal windows automatically:

```powershell
python launch_apis_simple.py
```

Then wait 60-90 seconds and check each terminal window.

---

## 🔧 Option 3 - With Health Checks

```powershell
python start_all_apis.py
```

(This waits and checks if each API is responding)

---

## 🧪 Test After Starting

Once all 3 terminals show "Uvicorn running":

```powershell
python test_optimized_chatbot.py
```

---

## ⚠️ Troubleshooting

**"Port already in use"**
- Close any existing Python processes
- Use Task Manager to kill Python if needed

**"Chatbot taking too long"**
- First run downloads ~200MB of models
- Wait up to 2 minutes
- Check terminal for download progress

**"Models not loading"**
- Check internet connection (models download from HuggingFace)
- Check terminal for error messages
- Try: `pip install --upgrade transformers torch`

---

## ✅ Success Indicators

You should see in each terminal:

**Job API (Terminal 1):**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Skill Gap API (Terminal 2):**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Chatbot API (Terminal 3):**
```
Loading intent classification model...
Loading NER model for skill extraction...
Loading response generation model...
✅ All models loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8002
```

---

## 🎯 Once Running

Test URLs:
- http://localhost:8000/docs (Job API)
- http://localhost:8001/docs (Skill Gap API)
- http://localhost:8002/docs (Chatbot API)

Run tests:
```powershell
python test_optimized_chatbot.py
```

**Expected:** All 6 intents pass in 2-5 seconds each! 🎉
