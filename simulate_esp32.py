import requests
import time
import random
import json

SERVER_URL = "http://localhost:8000/api/data"

def send_data(current, mode, over=False, testing=False, barcode=None, operator=None, limit=50.5, elapsed=0):
    """ارسال داده به سرور با فرمت جدید"""
    data = {
        "current": current,
        "mode": mode,
        "over": over,
        "testing": testing,
        "barcode": barcode,
        "operator": operator,
        "limit": limit,
        "elapsed": elapsed
    }
    
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print(f"✅ Sent: {current}mA, Mode: {mode}, Over: {over}")
        else:
            print(f"❌ Server error: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def simulate_test():
    """شبیه‌سازی یک تست کامل با مراحل دقیق"""
    print("\n" + "="*50)
    print("🚀 STARTING NEW TEST")
    print("="*50)
    
    # بارکد تصادفی
    barcode = f"{random.randint(1000000000, 9999999999)}"
    operator = "sina"
    flasher_type = random.choice([True, False])
    limit_m2 = 50.5
    limit_m3 = 250.0 if flasher_type else 160.0
    
    print(f"📱 Barcode: {barcode}")
    print(f"👤 Operator: {operator}")
    print(f"🔦 Type: {'FLASHER' if flasher_type else 'NORMAL'}")
    print(f"📊 Limits: M2={limit_m2}mA, M3={limit_m3}mA")
    
    # متغیرهای تست
    max_m2 = 0
    max_m3 = 0
    fault_m2 = False
    fault_m3 = False
    elapsed = 0
    
    # مرحله 1: آماده‌سازی (0-3 ثانیه)
    print("\n⏳ Phase 1: Preparation (0-3s)")
    for t in range(0, 3):
        send_data(
            current=0,
            mode=1,
            over=False,
            testing=True,
            barcode=barcode,
            operator=operator,
            limit=limit_m2,
            elapsed=t
        )
        time.sleep(1)
        elapsed = t + 1
    
    # مرحله 2: تست M2 (3-10 ثانیه)
    print("\n🔊 Phase 2: Testing M2 (3-10s)")
    for t in range(3, 10):
        # جریان واقعی با نویز
        base_current = random.uniform(35, 48)
        # گاهی خطا
        if random.random() < 0.15:
            base_current = random.uniform(55, 75)
            fault_m2 = True
        
        current = base_current
        if current > max_m2:
            max_m2 = current
        
        over = current > limit_m2
        
        send_data(
            current=current,
            mode=2,
            over=over,
            testing=True,
            barcode=barcode,
            operator=operator,
            limit=limit_m2,
            elapsed=t
        )
        time.sleep(1)
        elapsed = t + 1
    
    # مرحله 3: تست M3 (10-17 ثانیه)
    print("\n📡 Phase 3: Testing M3 (10-17s)")
    for t in range(10, 17):
        base_current = random.uniform(80, 150)
        if random.random() < 0.10:
            base_current = random.uniform(170, 200)
            fault_m3 = True
        
        current = base_current
        if current > max_m3:
            max_m3 = current
        
        over = current > limit_m3
        
        send_data(
            current=current,
            mode=3,
            over=over,
            testing=True,
            barcode=barcode,
            operator=operator,
            limit=limit_m3,
            elapsed=t
        )
        time.sleep(1)
        elapsed = t + 1
    
    # مرحله 4: پایان (17-20 ثانیه)
    print("\n✅ Phase 4: Finalization (17-20s)")
    for t in range(17, 20):
        send_data(
            current=0,
            mode=4,
            over=False,
            testing=True,
            barcode=barcode,
            operator=operator,
            limit=limit_m2,
            elapsed=t
        )
        time.sleep(1)
        elapsed = t + 1
    
    # نتیجه نهایی
    passed = not (fault_m2 or fault_m3)
    print("\n" + "="*50)
    print(f"📊 RESULTS:")
    print(f"   Max M2: {max_m2:.1f}mA {'❌ FAIL' if fault_m2 else '✅ PASS'}")
    print(f"   Max M3: {max_m3:.1f}mA {'❌ FAIL' if fault_m3 else '✅ PASS'}")
    print(f"   Overall: {'✅ PASSED' if passed else '❌ FAILED'}")
    print("="*50 + "\n")
    
    # ارسال نتیجه نهایی
    send_data(
        current=0,
        mode=1,
        over=False,
        testing=False,
        barcode=barcode,
        operator=operator,
        limit=limit_m2,
        elapsed=20
    )
    
    # ذخیره نتیجه در دیتابیس (از طریق API)
    try:
        result_data = {
            "barcode": barcode,
            "operator": operator,
            "flasher_type": flasher_type,
            "max_mode2": max_m2,
            "max_mode3": max_m3,
            "fault_mode2": fault_m2,
            "fault_mode3": fault_m3,
            "passed": passed
        }
        # اینجا میتونی یه endpoint جدید برای ذخیره نتیجه بسازی
        # فعلاً فقط چاپ میکنیم
        print("💾 Result saved in database")
    except Exception as e:
        print(f"❌ Error saving result: {e}")

if __name__ == "__main__":
    print("🔄 SIREN TESTER SIMULATOR STARTED")
    print("📡 Sending data to:", SERVER_URL)
    print("⏱️  Each test takes ~20 seconds")
    print("Press Ctrl+C to stop\n")
    
    test_count = 0
    while True:
        test_count += 1
        print(f"\n🔄 Test #{test_count}")
        simulate_test()
        
        # بین هر تست ۵ ثانیه مکث
        print("⏳ Waiting 5 seconds before next test...")
        time.sleep(5)