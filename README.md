# Network Manager GUI (nmgui)

A modern GTK4-based network management application for Linux systems.

## Features

- Scan and connect to WiFi networks
- View detailed network information
- Manage saved networks (connect, disconnect, forget)
- Clean, modern user interface

## Requirements

- Python 3.8+
- NetworkManager
- GTK4
- nmcli Python package

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nmgui.git
   cd nmgui
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application directly with Python:
```bash
python -m nmgui
```

Or build a standalone executable:
```bash
./build.sh
```

## Building

To build a standalone executable, run:
```bash
./build.sh
```

The executable will be created in the `dist/` directory.

## Development

To set up a development environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.