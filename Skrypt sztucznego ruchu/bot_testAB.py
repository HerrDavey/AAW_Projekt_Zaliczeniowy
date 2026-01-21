import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Adres hostowania
url = "http://127.0.0.1:5500/index.html" 

# Ilesztucznych użytkowników stworzyć?
number_of_users =  100

print(f"Generowanie {number_of_users} unikalnych użytkowników.")

for i in range(number_of_users):

    chrome_options = Options()
    chrome_options.add_argument("--incognito") 
    # chrome_options.add_argument("--headless") # Odkomentuj aby nie widzieć przeglądarki w trakcie działania 

    # Start przeglądarki
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Wejście na stronę
        driver.get(url)
        print(f"Użytkownik {i+1}: Wszedł na stronę")
        
        # Symulacja czasu na stronie (żeby GA4 zdążyło załadować GTM)
        time.sleep(3) 

    except Exception as e:
        print(f"Błąd: {e}")
    
    finally:
        #Zamknięcie przeglądarki czyści ciasteczka
        driver.quit()
        
        # Krótka przerwa między sesjami
        time.sleep(1)

print("Koniec.")