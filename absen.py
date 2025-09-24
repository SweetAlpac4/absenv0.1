from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import os, time, datetime

# Ambil username & password dari .env
load_dotenv()
USERNAME = os.getenv("NPM")
PASSWORD = os.getenv("PASSWORD")

# Setup Chrome headless
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

driver = webdriver.Chrome(options=options)

try:
    now = datetime.datetime.now(ZoneInfo("Asia/Jakarta"))
    if now.weekday() >= 5 or not (8 <= now.hour < 21):
        print("⏰ Di luar jam kuliah. Tidak mencoba absen.")
    else:
        driver.get("https://simkuliah.usk.ac.id/")
        wait = WebDriverWait(driver, 10)

        # Login
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))).click()
        time.sleep(2)

        if "login" in driver.current_url.lower():
            print(" Gagal login. Cek username/password atau CAPTCHA.")
            driver.save_screenshot("login_failed.png")
            exit()

        # Buka halaman absensi
        driver.get("https://simkuliah.usk.ac.id/index.php/absensi")
        time.sleep(2)

        absen_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn.btn-success")

        if not absen_buttons:
            print("ℹ Tidak ada tombol absen yang bisa diklik. Mungkin tidak ada jadwal.")
        else:
            for idx, button in enumerate(absen_buttons, start=1):
                try:
                    print(f"--- Memproses Absen #{idx} ---")
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)
                    driver.save_screenshot(f"after_absen_click_{idx}.png")

                    # Klik konfirmasi
                    konfirmasi_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "confirm"))
                    )
                    driver.execute_script("arguments[0].click();", konfirmasi_button)
                    time.sleep(2)
                    driver.save_screenshot(f"after_konfirmasi_click_{idx}.png")
                    print(f" Absen #{idx} selesai.")

                except Exception as e:
                    print(f" Gagal memproses absen #{idx}:", e)

            jam = now.strftime("%H:%M")
            os.system(f'notify-send "Absensi Berhasil" "Jam {jam}, semua absen berhasil dicoba."')

except Exception as e:
    print(" Terjadi error:", e)
    driver.save_screenshot("error.png")
    print("Screenshot error disimpan sebagai 'error.png'")
finally:
    driver.quit()
