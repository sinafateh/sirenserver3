# 🚨 Siren Server - سیستم تست و مانیتورینگ سایرن‌ها

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://python.org)

## 📖 معرفی پروژه

سیستم تست و مانیتورینگ سایرن‌های هشدار دهنده با استفاده از **ESP32** و **FastAPI**.

### ✨ قابلیت‌ها

- 🔐 سیستم احراز هویت (ادمین/اپراتور)
- 📊 داشبورد مانیتورینگ لحظه‌ای
- 📨 سیستم اعلان‌ها و پیام‌ها
- 👥 مدیریت کاربران
- 📈 نمایش گرافیکی داده‌ها
- 🌙 پشتیبانی از Dark/Light Mode

## 🛠️ تکنولوژی‌ها

- **Backend:** FastAPI, SQLite, Jinja2
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Hardware:** ESP32-S3, OLED 128x64

## 🚀 اجرا

```bash
# نصب کتابخانه‌ها
pip install -r requirements.txt

# اجرای سرور
python -m uvicorn app.main:app --reload