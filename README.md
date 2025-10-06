# UbiBot WS-1 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/richardctrimble/ubibot_ws1.svg)](https://github.com/richardctrimble/ubibot_ws1/releases/)

A Home Assistant integration for UbiBot WS-1 environmental monitoring devices.

## Features

This integration provides the following sensors from your UbiBot WS-1 device:

- **Temperature** (°C)
- **Humidity** (%)
- **Light** (lux)
- **Voltage** (V)
- **WiFi Signal** (dB)
- **Vibration** (count)
- **Knocks** (count)
- **Traffic Out** (kB)
- **Traffic In** (kB)

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/richardctrimble/ubibot_ws1`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "UbiBot WS-1" and install it
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/richardctrimble/ubibot_ws1/releases)
2. Extract the `ubibot_ws1` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"UbiBot WS-1"**
4. Enter your UbiBot credentials:
   - **Account Key**: Your UbiBot account API key
   - **Channel ID**: Your device's channel ID

### Finding Your Credentials

- **Account Key**: Found in your UbiBot account settings
- **Channel ID**: The numeric ID of your device channel (visible in the UbiBot web interface URL)

## Options

After setup, you can configure the following options:

- **Update Interval**: How often to poll the UbiBot API (1-60 minutes, default: 2 minutes)

## Troubleshooting

### Common Issues

1. **"Cannot connect"** error:
   - Verify your account key is correct
   - Check that your channel ID exists
   - Ensure your device is online and reporting data

2. **Sensors showing "unavailable"**:
   - Check if your device is actively sending data
   - Verify the update interval isn't too frequent
   - Look at the Home Assistant logs for API errors

### Debug Logging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.ubibot_ws1: debug
```

## Version History

### 2.0.0
- Complete rewrite for modern Home Assistant compatibility
- Added proper device info and entity naming
- Improved error handling and configuration validation
- Added support for traffic sensors
- Modern config flow with options

### 1.x.x
- Legacy versions (deprecated)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
