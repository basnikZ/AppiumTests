# Appium WiFi Settings Test

Automated test for checking WiFi settings in Android system using the Appium framework.

## Test Environment

Test was developed and verified on:
- **Phone:** Google Pixel 9
- **Operating System:** GrapheneOS
- **Application:** Standard Android Settings app

⚠️ **Important Notice:** Due to various Android customizations by manufacturers and different system versions, you might need to adjust selectors and element paths for your specific device.

## Prerequisites

- Python 3.11+
- Appium Desktop 2.0+ (with UiAutomator2 driver)
- Android device with:
  - USB debugging enabled
  - Settings app accessible
  - Permission to modify WiFi settings

## Required Python Packages
- Appium-Python-Client==3.1.1
- selenium==4.18.1
- urllib3==2.2.1

## Installation

1. Download and install Appium Desktop from [Appium GitHub Releases](https://github.com/appium/appium-desktop/releases)

2. Clone the repository:
```bash
git clone [repository-url]
cd AppiumTests
```

3. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
.\venv\Scripts\activate  # For Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Enable USB debugging on your Android device:
   - Go to Settings > About phone
   - Tap Build number 7 times to enable Developer options
   - Go to Settings > System > Developer options
   - Enable USB debugging

2. Start Appium Desktop:
   - Click 'Start Server'
   - Server address should be: http://127.0.0.1:4723
   - Click 'Start Inspector Session' to verify server is working

3. Connect your device via USB and verify connection:
```bash
adb devices
```

## Running the Test

```bash
python wifi_test.py
```

## Test Functionality

The test performs the following steps:
1. Opens Settings application
2. Navigates to Network & Internet > Internet
3. Checks WiFi status
4. If WiFi is off, turns it on
5. Lists available WiFi networks
6. Returns WiFi to its original state
7. Generates detailed report

## Test Output and Viewing Results

The test generates two types of output files in the `appium_logs` directory:

### JSON Log
- Located at: `appium_logs/appium_events_[timestamp].json`
- Contains raw test data and events
- Useful for debugging or data analysis

### HTML Report
- Located at: `appium_logs/appium_events_[timestamp].html`
- Interactive visual report with:
  - Test summary
  - Timeline of events
  - Screenshots at key steps
  - Detailed event information

### Viewing Reports

1. **Direct HTML Viewing:**
   - Navigate to `appium_logs` directory
   - Open the `.html` file in any web browser
   - All data and screenshots are embedded in the file

2. **Using Local Server (Optional):**
   ```bash
   cd appium_logs
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser

### Screenshots
- Automatically captured at key moments:
  - Initial app state
  - After navigation steps
  - WiFi network list
  - Error states (if any)
- Embedded directly in the HTML report
- Base64 encoded to avoid external file dependencies

## Known Limitations

1. Selectors are optimized for GrapheneOS on Google Pixel 9
2. On other devices, you might encounter:
   - Different element names
   - Different Settings app structure
   - Different paths to WiFi settings
   - Different timing needed for network scanning

## Troubleshooting

If the test doesn't work on your device:

1. Check the XML structure of your Settings app:
```bash
adb shell uiautomator dump
adb pull /sdcard/window_dump.xml
```

2. Open `window_dump.xml` to analyze the element structure

3. Common issues:
   - **Connection refused:** Make sure Appium Desktop is running
   - **Device not found:** Check USB connection and debugging status
   - **Element not found:** Different UI structure, adjust selectors
   - **Permission denied:** Check app permissions on device

4. Modify selectors in `wifi_test.py` according to your XML structure

## Contributing

If you have modifications for other devices or improvements, please create a Pull Request with:
- Device description
- System version
- Changes made
- Test results and screenshots

## License

MIT 