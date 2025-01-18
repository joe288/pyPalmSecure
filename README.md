# pyPalmSecure
This Python-based software is designed to interface with the Fujitsu PalmSecure sensor, allowing users to read data directly from the device. The application captures palm vein patterns and returns an image that can be further processed for various applications, such as biometric authentication or identity verification.

## source
https://github.com/MagicalTux/palmsecure/tree/master

## Features

- **Data Acquisition**: Seamlessly read palm vein data from the Fujitsu PalmSecure sensor.
- **Image Output**: Generate and return an image of the captured palm vein patterns for further analysis.
- **Raspberry Pi Compatibility**: The software is fully compatible with Raspberry Pi, making it ideal for embedded applications.
- **Pre-installed USB Drivers**: USB drivers for the Fujitsu PalmSecure sensor are already installed, ensuring a smooth setup process.
- **Recognition Loop**: The software operates in a continuous loop, monitoring for the correct hand positioning. An image is captured only when the hand is at the optimal distance from the sensor, ensuring accurate readings.
- **Easy Integration**: Designed to be easily integrated into larger systems or workflows.

## Requirements

- Python 3.x
- [Required libraries](requirements.txt)
- Raspberry Pi (optional, but recommended for embedded applications)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/joe288/pyPalmSecure.git
    ````
2. Install packages:
    ````bash
    sudo apt-get install libusb-1.0-0-dev
    sudo apt-get install libgl1
    ````
3. Install the required dependencies:
    ````bash
    pip install -r requirements.txt
    ````
## Usage
To use the software, simply run the main script. The application will enter a recognition loop, continuously checking for the correct hand positioning. An image will be captured only when the hand is at the optimal distance from the sensor.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
