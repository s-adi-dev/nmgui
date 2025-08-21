# Network Manager GUI (nmgui)

A modern GTK4-based network management application for Linux systems using `nmcli`

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

### Arch Linux

Install the binary version from AUR:
```bash
yay -S nmgui-bin
```

### Other Distributions

Download the latest binary from [Releases](https://github.com/s-adi-dev/nmgui/releases):

```bash
# Download and install
sudo curl -L https://github.com/s-adi-dev/nmgui/releases/download/v1.1.0/nmgui.bin -o /usr/bin/nmgui
sudo chmod +x /usr/bin/nmgui

# Install desktop entry (optional)
curl -sL https://raw.githubusercontent.com/s-adi-dev/nmgui/main/nmgui.desktop | sudo tee /usr/share/applications/nmgui.desktop > /dev/null
```

**Note:** Only requires NetworkManager to be installed on your system.

### Manual
1. Clone the repository:
   ```bash
   git clone https://github.com/s-adi-dev/nmgui.git
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

## Hyprland Users

Add this to your config for floating window:
```ini
windowrule = float, title:^(.*Network Manager.*)$
```

## Development

To set up a development environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
