from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
import json
import os
import datetime
import base64

class EventLogger:
    def __init__(self):
        self.events = []
        self.start_time = time.time()

    def log_event(self, event_type, details, screenshot=None):
        event = {
            "type": event_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "time_from_start": round(time.time() - self.start_time, 2),
            "details": details
        }
        if screenshot:
            event["screenshot"] = screenshot
        self.events.append(event)
        return event

    def save_to_file(self, log_dir):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"appium_events_{timestamp}.json")
        
        with open(log_file, 'w') as f:
            json.dump({
                "events": self.events,
                "total_duration": round(time.time() - self.start_time, 2)
            }, f, indent=2)
        
        return log_file, timestamp

def get_element_details(element):
    try:
        return {
            "text": element.text,
            "location": element.location,
            "size": element.size,
            "enabled": element.is_enabled(),
            "displayed": element.is_displayed(),
            "attributes": element.get_property("attributes")
        }
    except:
        return {"error": "Could not get element details"}

# Create correct options object for Android - check correct case!
options = UiAutomator2Options()
options.set_capability("platformName", "Android")  # try using set_capability instead of direct assignment
options.set_capability("automationName", "UiAutomator2")  # explicitly set automationName
options.set_capability("deviceName", "Android Emulator")

# For testing existing application
options.set_capability("appPackage", "com.android.settings")
options.set_capability("appActivity", "com.android.settings.Settings")

# Adding support for Event Timings API
options.set_capability("appium:eventTimings", True)
options.set_capability("appium:enablePerformanceLogging", True)

logger = EventLogger()

try:
    # Try connect with explicit specific path
    print("Trying to connect to Appium server...")
    driver = webdriver.Remote("http://localhost:4723", options=options)
    print("Connection successful!")
    
    # Log device information
    device_info = {
        "capabilities": driver.capabilities,
        "device_time": driver.device_time,
        "orientation": driver.orientation,
        "platform_version": driver.capabilities.get("platformVersion")
    }
    logger.log_event("device_info", device_info)
    
    # Longer waiting for application loading
    print("Waiting for application loading...")
    time.sleep(5)
    
    # Take screenshot of initial state
    screenshot = driver.get_screenshot_as_base64()
    logger.log_event("initial_state", {"status": "app_loaded"}, screenshot)
    
    # First click on "Network and Internet"
    print("Searching for 'Network and Internet'...")
    start_time = time.time()
    network_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Network and Internet']")
    logger.log_event("element_found", {
        "element": "Network and Internet",
        "search_time": round(time.time() - start_time, 2),
        "details": get_element_details(network_element)
    })
    print(f"Found element: {network_element.text}")
    network_element.click()
    logger.log_event("element_clicked", {"element": "Network and Internet"})
    print("Clicked on 'Network and Internet'")
    
    # Wait for page loading
    time.sleep(2)
    screenshot = driver.get_screenshot_as_base64()
    logger.log_event("navigation", {"to": "Network and Internet"}, screenshot)
    
    # Now searching for "Internet"
    print("Searching for 'Internet'...")
    try:
        start_time = time.time()
        internet_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Internet']")
        logger.log_event("element_found", {
            "element": "Internet",
            "search_time": round(time.time() - start_time, 2),
            "details": get_element_details(internet_element)
        })
        
        internet_element.click()
        logger.log_event("element_clicked", {"element": "Internet"})
        print("Clicked on 'Internet'")
        
        # Wait for page loading
        time.sleep(2)
        screenshot = driver.get_screenshot_as_base64()
        logger.log_event("navigation", {"to": "Internet settings"}, screenshot)
        
        # Searching for Wi-Fi switch - first find element with text "Wi-Fi"
        print("Searching for Wi-Fi switch...")
        wifi_text_element = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Wi-Fi']")
        logger.log_event("element_found", {
            "element": "Wi-Fi text",
            "details": get_element_details(wifi_text_element)
        })
        print(f"Found element: {wifi_text_element.text}")
        
        # Now find switch which is near text "Wi-Fi"
        wifi_switches = driver.find_elements(by=AppiumBy.XPATH, value="//android.widget.Switch")
        
        if len(wifi_switches) > 0:
            wifi_switch = wifi_switches[0]  # Take first switch, which is probably for Wi-Fi
            
            # Check current state of switch
            is_wifi_on = wifi_switch.get_attribute("checked") == "true"
            logger.log_event("wifi_state", {
                "initial_state": "on" if is_wifi_on else "off",
                "switch_details": get_element_details(wifi_switch)
            })
            print(f"Wi-Fi is {'on' if is_wifi_on else 'off'}")
            
            # If WiFi is off, turn it on and wait for networks to load
            if not is_wifi_on:
                print("WiFi is off, turning it on...")
                wifi_switch.click()
                logger.log_event("wifi_toggled", {
                    "previous_state": "off",
                    "action": "turning_on"
                })
                # Wait longer for WiFi to initialize and scan for networks
                time.sleep(5)
                
                # Verify WiFi was turned on
                is_wifi_on_now = wifi_switch.get_attribute("checked") == "true"
                logger.log_event("wifi_state", {
                    "current_state": "on" if is_wifi_on_now else "off",
                    "switch_details": get_element_details(wifi_switch)
                })
                print(f"Wi-Fi is now {'on' if is_wifi_on_now else 'off'}")
                
                if not is_wifi_on_now:
                    raise Exception("Failed to turn on WiFi")
                
                # Wait additional time for networks to appear
                print("Waiting for networks to appear...")
                time.sleep(5)
            
            # Now that WiFi is on, look for networks
            print("Searching for available WiFi networks...")
            
            try:
                # Try to find RecyclerView, which contains list of Wi-Fi networks
                wifi_container = driver.find_element(by=AppiumBy.XPATH, value="//androidx.recyclerview.widget.RecyclerView")
                logger.log_event("wifi_container_found", {"container_details": get_element_details(wifi_container)})
                
                # Find all network items - they are LinearLayouts with specific content-desc
                network_items = wifi_container.find_elements(by=AppiumBy.XPATH, 
                    value=".//android.widget.LinearLayout[contains(@content-desc, 'Wi-Fi signal') or contains(@content-desc, 'Secure network')]")
                
                networks_info = []
                print(f"Found {len(network_items)} WiFi networks")
                
                for network_item in network_items:
                    try:
                        # Get network name from title element
                        name_element = network_item.find_element(by=AppiumBy.ID, value="android:id/title")
                        network_name = name_element.text
                        
                        # Get connection status if available
                        try:
                            status_element = network_item.find_element(by=AppiumBy.ID, value="android:id/summary")
                            status = status_element.text
                        except:
                            status = None
                        
                        if network_name and not any(item in network_name.lower() for item in ['add network', 'saved networks', 'network preferences']):
                            network_info = {
                                "name": network_name,
                                "status": status,
                                "content_desc": network_item.get_attribute("content-desc")
                            }
                            networks_info.append(network_info)
                            print(f"Found network: {network_name} ({status if status else 'not connected'})")
                    except Exception as e:
                        logger.log_event("wifi_network_error", {
                            "error": str(e),
                            "element_content_desc": network_item.get_attribute("content-desc")
                        })
                
                if networks_info:
                    logger.log_event("wifi_networks_found", {
                        "count": len(networks_info),
                        "networks": networks_info
                    })
                    screenshot = driver.get_screenshot_as_base64()
                    logger.log_event("wifi_networks_screen", {"status": "networks_listed"}, screenshot)
                else:
                    logger.log_event("wifi_networks_empty", {"message": "No networks found in the list"})
                    screenshot = driver.get_screenshot_as_base64()
                    logger.log_event("wifi_networks_screen", {"status": "no_networks"}, screenshot)
                    
            except Exception as e:
                error_screenshot = driver.get_screenshot_as_base64()
                logger.log_event("wifi_list_error", {
                    "error": str(e),
                    "page_source": driver.page_source
                }, error_screenshot)
                print(f"Error searching for Wi-Fi networks: {e}")
            
            # Now turn WiFi back off if it was originally off
            if not is_wifi_on:
                print("Turning WiFi back off...")
                wifi_switch.click()
                time.sleep(2)
                final_state = wifi_switch.get_attribute("checked") == "true"
                logger.log_event("wifi_final_state", {
                    "state": "on" if final_state else "off",
                    "matches_original": final_state == is_wifi_on
                })
        else:
            logger.log_event("error", {"message": "Wi-Fi switch not found"})
            print("Wi-Fi switch not found")
        
        # Return back
        time.sleep(2)
        driver.back()  # Back to Network and Internet
        logger.log_event("navigation", {"action": "back", "to": "Network and Internet"})
        time.sleep(1)
        driver.back()  # Back to main settings screen
        logger.log_event("navigation", {"action": "back", "to": "main settings"})
        
        print("Test successfully completed!")
        
    except Exception as e:
        error_screenshot = driver.get_screenshot_as_base64()
        logger.log_event("error", {
            "message": str(e),
            "page_source": driver.page_source
        }, error_screenshot)
        print(f"Error working with Wi-Fi: {e}")
        # Print all elements on screen for diagnosis
        print("Printing all available elements on screen:")
        page_source = driver.page_source
        print(page_source)
        raise Exception("Problem with Wi-Fi settings")
    
except Exception as e:
    logger.log_event("critical_error", {"message": str(e)})
    print(f"Error: {e}")
    
finally:
    if 'driver' in locals():
        # Getting information about events and timing
        try:
            print("Getting information about events and timing...")
            appium_events = driver.get_events()
            logger.log_event("appium_events", {"events": appium_events})
            
            # Create folder for logs, if not exists
            log_dir = "appium_logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file, timestamp = logger.save_to_file(log_dir)
            print(f"Events and timing information was saved to file: {log_file}")
            
            # Create HTML file for displaying data
            html_file = os.path.join(log_dir, f"appium_events_{timestamp}.html")
            
            # Load JSON data
            with open(log_file, 'r') as f:
                json_data = f.read()
            
            with open(html_file, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Appium Test Report - {timestamp}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                        h1 {{ color: #333; text-align: center; }}
                        .event {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: white; }}
                        .event-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
                        .event-type {{ font-weight: bold; color: #0066cc; }}
                        .event-time {{ color: #666; }}
                        .event-details {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        .screenshot {{ max-width: 100%; height: auto; margin-top: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                        .error {{ color: #dc3545; }}
                        .success {{ color: #28a745; }}
                        .navigation {{ color: #17a2b8; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Appium Test Report - {timestamp}</h1>
                        <div id="summary"></div>
                        <div id="events"></div>
                    </div>
                    
                    <script>
                        const data = {json_data};  // JSON data is now embedded directly
                        
                        function formatTime(isoString) {{
                            const date = new Date(isoString);
                            return date.toLocaleTimeString();
                        }}
                        
                        function getEventClass(type) {{
                            if (type.includes('error')) return 'error';
                            if (type.includes('navigation')) return 'navigation';
                            if (type === 'test_completed') return 'success';
                            return '';
                        }}
                        
                        // Summary
                        const summaryDiv = document.getElementById('summary');
                        summaryDiv.innerHTML = `
                            <h2>Test Summary</h2>
                            <p>Total Duration: ${{data.total_duration}} seconds</p>
                            <p>Total Events: ${{data.events.length}}</p>
                        `;
                        
                        // Events
                        const eventsDiv = document.getElementById('events');
                        eventsDiv.innerHTML = '<h2>Detailed Events</h2>';
                        
                        data.events.forEach(event => {{
                            const eventDiv = document.createElement('div');
                            eventDiv.className = `event ${{getEventClass(event.type)}}`;
                            
                            let screenshotHtml = '';
                            if (event.screenshot) {{
                                screenshotHtml = `<img src="data:image/png;base64,${{event.screenshot}}" class="screenshot" />`;
                            }}
                            
                            eventDiv.innerHTML = `
                                <div class="event-header">
                                    <span class="event-type">${{event.type}}</span>
                                    <span class="event-time">
                                        Time: ${{formatTime(event.timestamp)}}
                                        (${{event.time_from_start}}s from start)
                                    </span>
                                </div>
                                <div class="event-details">
                                    <pre>${{JSON.stringify(event.details, null, 2)}}</pre>
                                </div>
                                ${{screenshotHtml}}
                            `;
                            eventsDiv.appendChild(eventDiv);
                        }});
                    </script>
                </body>
                </html>
                """)
            
            print(f"HTML visualization was created in file: {html_file}")
            print(f"Or visit http://localhost:8000/ to view all logs")
            
        except Exception as e:
            print(f"Error getting events information: {e}")
        
        driver.quit()
        print("Driver closed")