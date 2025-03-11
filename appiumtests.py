from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
import json
import os
import datetime

# Vytvoř správný options objekt pro Android - zkontroluj správnou velikost písmen!
options = UiAutomator2Options()
options.set_capability("platformName", "Android")  # zkus použít set_capability místo přímého přiřazení
options.set_capability("automationName", "UiAutomator2")  # explicitně nastav automationName
options.set_capability("deviceName", "Android Emulator")

# Pro testování existující aplikace
options.set_capability("appPackage", "com.android.settings")
options.set_capability("appActivity", "com.android.settings.Settings")

# Přidání podpory pro Event Timings API
options.set_capability("appium:eventTimings", True)
options.set_capability("appium:enablePerformanceLogging", True)

try:
    # Zkus připojení s explicitní specifikací cesty
    print("Pokouším se připojit k Appium serveru...")
    driver = webdriver.Remote("http://localhost:4723", options=options)
    print("Připojení úspěšné!")
    
    # Delší čekání na načtení aplikace
    print("Čekám na načtení aplikace...")
    time.sleep(5)
    
    # Nejprve klikneme na "Network and Internet"
    print("Hledám 'Network and Internet'...")
    network_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Network and Internet']")
    print(f"Našel jsem element: {network_element.text}")
    network_element.click()
    print("Kliknul jsem na 'Network and Internet'")
    
    # Počkáme na načtení podstránky
    time.sleep(2)
    
    # Nyní hledáme "Internet"
    print("Hledám 'Internet'...")
    try:
        internet_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Internet']")
        print(f"Našel jsem element: {internet_element.text}")
        internet_element.click()
        print("Kliknul jsem na 'Internet'")
        
        # Počkáme na načtení stránky s Wi-Fi přepínačem
        time.sleep(2)
        
        # Hledáme Wi-Fi přepínač - nejprve najdeme element s textem "Wi-Fi"
        print("Hledám Wi-Fi přepínač...")
        wifi_text_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Wi-Fi']")
        print(f"Našel jsem element: {wifi_text_element.text}")
        
        # Nyní najdeme přepínač, který je v blízkosti textu Wi-Fi
        # Zkusíme najít přepínač podle typu widgetu
        wifi_switches = driver.find_elements(by=AppiumBy.XPATH, value="//android.widget.Switch")
        
        if len(wifi_switches) > 0:
            wifi_switch = wifi_switches[0]  # Bereme první přepínač, který je pravděpodobně pro Wi-Fi
            
            # Zjistíme aktuální stav přepínače
            is_wifi_on = wifi_switch.get_attribute("checked") == "true"
            print(f"Wi-Fi je {'zapnuté' if is_wifi_on else 'vypnuté'}")
            
            # Přepneme stav Wi-Fi (zapneme, když je vypnuté a vypneme, když je zapnuté)
            wifi_switch.click()
            print(f"Wi-Fi bylo {'vypnuto' if is_wifi_on else 'zapnuto'}")
            
            # Počkáme na změnu stavu
            time.sleep(3)
            
            # Znovu zkontrolujeme stav po přepnutí
            is_wifi_on_now = wifi_switch.get_attribute("checked") == "true"
            print(f"Wi-Fi je nyní {'zapnuté' if is_wifi_on_now else 'vypnuté'}")
            
            # Pokud je Wi-Fi zapnuté, vypíšeme seznam dostupných Wi-Fi sítí
            if is_wifi_on_now:
                # Počkáme na načtení seznamu Wi-Fi sítí
                time.sleep(3)
                
                # Vypíšeme seznam dostupných Wi-Fi sítí
                print("Seznam dostupných Wi-Fi sítí:")
                
                # Hledáme pouze elementy, které jsou v sekci Wi-Fi sítí
                # Můžeme použít více specifický XPath, který hledá pouze v RecyclerView nebo podobném kontejneru
                try:
                    # Zkusíme najít RecyclerView, který obsahuje seznam Wi-Fi sítí
                    wifi_container = driver.find_element(by=AppiumBy.XPATH, value="//androidx.recyclerview.widget.RecyclerView")
                    
                    # V kontejneru hledáme TextViews, které pravděpodobně obsahují názvy Wi-Fi sítí
                    wifi_networks = wifi_container.find_elements(by=AppiumBy.XPATH, value=".//android.widget.TextView")
                    
                    if len(wifi_networks) > 0:
                        for i, wifi in enumerate(wifi_networks[:5]):  # Omezíme výpis na prvních 5 položek
                            try:
                                wifi_name = wifi.text
                                if wifi_name and not wifi_name.isspace() and wifi_name != "Wi-Fi" and "5G" not in wifi_name:
                                    print(f"  {i+1}. {wifi_name}")
                            except Exception as e:
                                print(f"Chyba při čtení názvu Wi-Fi sítě: {e}")
                    else:
                        print("Nenalezeny žádné Wi-Fi sítě")
                except Exception as e:
                    print(f"Chyba při hledání seznamu Wi-Fi sítí: {e}")
                    # Alternativní přístup - vypíšeme všechny TextViews na obrazovce
                    all_texts = driver.find_elements(by=AppiumBy.XPATH, value="//android.widget.TextView")
                    print(f"Nalezeno {len(all_texts)} textových elementů:")
                    for i, text in enumerate(all_texts[:5]):
                        try:
                            text_content = text.text
                            if text_content and not text_content.isspace():
                                print(f"  {i+1}. {text_content}")
                        except:
                            pass
        else:
            print("Nenalezen Wi-Fi přepínač")
        
        # Návrat zpět
        time.sleep(2)
        driver.back()  # Zpět na Network and Internet
        time.sleep(1)
        driver.back()  # Zpět na hlavní obrazovku nastavení
        
    except Exception as e:
        print(f"Chyba při práci s Wi-Fi: {e}")
        # Vypíšeme všechny elementy na obrazovce pro diagnostiku
        print("Vypisuji všechny dostupné elementy na obrazovce:")
        page_source = driver.page_source
        print(page_source)
        raise Exception("Problém při práci s Wi-Fi nastavením")
    
    print("Test úspěšně dokončen!")
    
except Exception as e:
    print(f"Chyba: {e}")
    
finally:
    if 'driver' in locals():
        # Získání informací o událostech a časování
        try:
            print("Získávám informace o událostech a časování...")
            events = driver.get_events()
            
            # Vytvoření složky pro logy, pokud neexistuje
            log_dir = "appium_logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Vytvoření názvu souboru s časovým razítkem
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"appium_events_{timestamp}.json")
            
            # Uložení dat do JSON souboru
            with open(log_file, 'w') as f:
                json.dump({
                    "events": events
                }, f, indent=2)
            
            print(f"Informace o událostech a časování byly uloženy do souboru: {log_file}")
            
            # Vytvoření HTML souboru pro zobrazení dat
            html_file = os.path.join(log_dir, f"appium_events_{timestamp}.html")
            with open(html_file, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Appium Events - {timestamp}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #333; }}
                        .event {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                        .event-name {{ font-weight: bold; color: #0066cc; }}
                        .event-time {{ color: #666; }}
                        pre {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>Appium Events - {timestamp}</h1>
                    <p>Pro zobrazení detailních dat otevřete soubor: {log_file}</p>
                    <script>
                        // Načtení dat z JSON souboru
                        fetch('{log_file}')
                            .then(response => response.json())
                            .then(data => {{
                                // Zobrazení událostí
                                const eventsDiv = document.createElement('div');
                                eventsDiv.innerHTML = '<h2>Events</h2>';
                                document.body.appendChild(eventsDiv);
                                
                                if (data.events) {{
                                    for (const event of data.events) {{
                                        const eventDiv = document.createElement('div');
                                        eventDiv.className = 'event';
                                        eventDiv.innerHTML = `
                                            <div class="event-name">${{event.name || 'Unnamed Event'}}</div>
                                            <div class="event-time">Time: ${{event.time || 'N/A'}}</div>
                                            <pre>${{JSON.stringify(event, null, 2)}}</pre>
                                        `;
                                        eventsDiv.appendChild(eventDiv);
                                    }}
                                }}
                            }})
                            .catch(error => {{
                                console.error('Error loading data:', error);
                                document.body.innerHTML += `<p style="color: red;">Error loading data: ${{error.message}}</p>`;
                            }});
                    </script>
                </body>
                </html>
                """)
            
            print(f"HTML vizualizace byla vytvořena v souboru: {html_file}")
            print(f"Pro zobrazení otevřete soubor v prohlížeči: file://{os.path.abspath(html_file)}")
            print(f"Nebo navštivte http://localhost:8000/ pro zobrazení všech logů")
            
        except Exception as e:
            print(f"Chyba při získávání informací o událostech: {e}")
        
        driver.quit()
        print("Driver ukončen")