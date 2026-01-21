import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# KONFIGURACJA GŁÓWNA
URL = "http://127.0.0.1:5500/index.html" 
LICZBA_WIZYT = 50

PROB_CLICK = 0.40   # 40% szans, że kliknie w jakiś link/produkt
PROB_VIDEO = 0.20   # 20% szans, że obejrzy wideo
PROB_FORM  = 0.05   # 5% szans, że wypełni formularz


SELECTOR_COOKIE = ["#onetrust-accept-btn-handler", "button:contains('Akceptuj')", "button[id*='cookie']", ".accept-cookies", "button[data-testid='cookie-accept']"]
SELECTOR_LINK   = "a.product-link, a.btn, .card a" 
SELECTOR_VIDEO  = "iframe[src*='youtube'], video"
SELECTOR_FORM   = "form"
SELECTOR_INPUT_NAME = "input[name='imie'], input[name='name']"
SELECTOR_INPUT_EMAIL = "input[name='email']"

# DARMOWA LISTA PROXY Z INTERNETU
PROXY_LIST = [
    "61.29.96.146:8000", "103.81.175.218:28022", "94.184.25.18:240", "94.184.25.71:242",
    "94.184.25.17:242", "94.184.25.27:241", "94.184.25.66:242", "94.184.25.74:241",
    "188.166.222.51:80", "71.168.71.12:8890", "89.22.237.70:80", "182.53.202.208:8080",
    "34.135.166.24:80", "156.246.90.81:80", "47.251.74.38:199", "62.149.165.171:80",
    "138.91.159.185:80", "35.224.171.0:80", "150.107.140.238:3128", "162.240.19.30:80"
]

def random_sleep(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))

def get_random_proxy():
    if not PROXY_LIST: return None
    return random.choice(PROXY_LIST)

def smooth_scroll(driver, max_scrolls=10):
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(random.randint(3, max_scrolls)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
            random_sleep(0.5, 1.5)
            
            if random.random() > 0.8:
                driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
                random_sleep(0.5, 1.0)
    except: pass

def handle_cookies(driver):
    print("Szukam cookies...")
    for selector in SELECTOR_COOKIE:
        try:
            if "contains" in selector:
                element = driver.find_element(By.XPATH, f"//button[contains(text(), 'Akceptuj') or contains(text(), 'Zgoda') or contains(text(), 'OK')]")
            else:
                element = driver.find_element(By.CSS_SELECTOR, selector)
            
            element.click()
            print("Ciasteczka zaakceptowane!")
            random_sleep(1, 2)
            return True
        except:
            continue
    return False

# AKCJE MODUŁOWE
def action_click_product(driver, bot_id):
    print(f"[{bot_id}] AKCJA: Klikanie w link...")
    try:
        links = driver.find_elements(By.CSS_SELECTOR, SELECTOR_LINK)
        if not links:
            print(f"[{bot_id}] Nie znaleziono linków do kliknięcia.")
            return

        # Wybierz widoczny link
        target_link = random.choice(links)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_link)
        random_sleep(1, 2)
        
        original_window = driver.current_window_handle
        windows_before = driver.window_handles
        
        # Klik
        driver.execute_script("arguments[0].click();", target_link)
        random_sleep(3, 5)
        
        # Czy otworzyło się nowe okno
        windows_after = driver.window_handles
        
        if len(windows_after) > len(windows_before):
            print(f"[{bot_id}] Otwarto nową kartę. Przełączam się")
            new_window = [w for w in windows_after if w not in windows_before][0]
            driver.switch_to.window(new_window)
            
            smooth_scroll(driver, max_scrolls=5)
            random_sleep(2, 4)
            
            print(f"[{bot_id}] Zamykam kartę i wracam.")
            driver.close()
            driver.switch_to.window(original_window)
        else:
            print(f"[{bot_id}] Ta sama karta. Wracam wstecz.")
            smooth_scroll(driver, max_scrolls=3)
            driver.back()
            
    except Exception as e:
        print(f"[{bot_id}] Błąd klikania: {e}")

def action_watch_video(driver, bot_id):
    print(f"[{bot_id}] AKCJA: Szukanie wideo")
    try:
        videos = driver.find_elements(By.CSS_SELECTOR, SELECTOR_VIDEO)
        if videos:
            vid = videos[0]
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", vid)
            watch_time = random.randint(5, 15)
            print(f"[{bot_id}] Oglądam wideo przez {watch_time}s...")
            time.sleep(watch_time)
        else:
            print(f"[{bot_id}] Brak wideo na stronie.")
    except Exception as e:
        print(f"[{bot_id}] Błąd wideo: {e}")

def action_fill_form(driver, bot_id):
    print(f"[{bot_id}] AKCJA: Wypełnianie formularza...")
    try:
        # Szukamy czy jest w ogóle input
        name_input = driver.find_element(By.CSS_SELECTOR, SELECTOR_INPUT_NAME)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", name_input)
        
        name_input.send_keys("Jan Testowy")
        random_sleep(0.5, 1)
        
        try:
            email_input = driver.find_element(By.CSS_SELECTOR, SELECTOR_INPUT_EMAIL)
            email_input.send_keys("jan@testowy.pl")
        except: pass
        
        random_sleep(2, 3)
        print(f"[{bot_id}] Formularz wypełniony (bez wysyłania).")
    except:
        print(f"[{bot_id}] Nie znaleziono formularza.")

# Logika BOTA 
def run_single_bot(bot_id):
    proxy = get_random_proxy()
    print(f"\n[{bot_id}/{LICZBA_WIZYT}] Start (Proxy: {proxy})")

    # Ustawienia Anti-Detect
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Skrypt maskujący webdrivera
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        driver.set_page_load_timeout(25) # Timeout dla proxy
        
        try:
            driver.get(URL)
        except:
            print(f"[{bot_id}] Timeout ładowania strony (wina proxy).")
            return # Kończymy tego bota, idziemy do następnego

        driver.set_page_load_timeout(60)
        random_sleep(2, 3)

        # 1. Cookies 
        handle_cookies(driver)

        # 2. Scroll Wstępny 
        smooth_scroll(driver, max_scrolls=3)

        # 3. LOSOWANIE AKCJI 
        # Każda akcja losuje się oddzielnie. Bot może zrobić wszystko, albo tylko scroll
        
        do_click = random.random() < PROB_CLICK
        do_video = random.random() < PROB_VIDEO
        do_form  = random.random() < PROB_FORM
        
        print(f"[{bot_id}] Plany: Click={do_click}, Video={do_video}, Form={do_form}")

        if do_click:
            action_click_product(driver, bot_id)
            random_sleep(2, 4)
        
        smooth_scroll(driver, max_scrolls=2)

        if do_video:
            action_watch_video(driver, bot_id)
            random_sleep(1, 3)

        if do_form:
            action_fill_form(driver, bot_id)

        print(f"[{bot_id}] Koniec wizyty.")

    except Exception as e:
        print(f"[{bot_id}] Błąd krytyczny: {e}")
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    for i in range(1, LICZBA_WIZYT + 1):
        run_single_bot(i)
        
        # Pauza między użytkownikami dla naturalności dla Googla
        pauza = random.randint(3, 8)
        print(f"Czekam {pauza}s.")
        time.sleep(pauza)