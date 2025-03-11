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
- Appium Server 2.0+
- Android SDK
- ADB (Android Debug Bridge)
- Connected Android device with USB debugging enabled

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd AppiumTests
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
.\venv\Scripts\activate  # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Start Appium server:
```bash
appium --use-drivers=uiautomator2 --allow-insecure=chromedriver_autodownload
```

2. Connect your device via USB and enable USB debugging

3. Verify device connection:
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

## Test Output

- JSON log in `appium_logs/appium_events_[timestamp].json`
- HTML report in `appium_logs/appium_events_[timestamp].html`
- Screenshots of key steps integrated in HTML report

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

2. Modify selectors in `wifi_test.py` according to your XML structure

## Contributing

If you have modifications for other devices or improvements, please create a Pull Request with:
- Device description
- System version
- Changes made

## License

MIT 