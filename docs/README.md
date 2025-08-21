<h1 align="center">NM GUI</h1>

A simple, lightweight GTK4-based GUI for NetworkManager using `nmcli`.

![Main Interface](assets/interface.png)

## Features

- Clean and minimal GTK4 interface
- Uses `nmcli` for backend operations
- Fast and lightweight
- Available as a prebuilt binary (no Python setup required)

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
sudo curl -L https://github.com/s-adi-dev/nmgui/releases/download/v1.0.0/nmgui.bin -o /usr/bin/nmgui
sudo chmod +x /usr/bin/nmgui

# Install desktop entry (optional)
curl -sL https://raw.githubusercontent.com/s-adi-dev/nmgui/main/nmgui.desktop | sudo tee /usr/share/applications/nmgui.desktop > /dev/null
```

**Note:** Only requires NetworkManager to be installed on your system.

## Building from Source

If you prefer to build from source, ensure the ensure the following dependencies are installed:

#### Dependencies

* Python 3.10 or newer
* `python-gobject`
* `python-nmcli`
* `gtk4`
* `NetworkManager`

Clone the repository and run:


```bash
git clone https://github.com/s-adi-dev/nmgui.git
cd nmgui

# Run the application
python3 app/main.py
```

## Usage

Launch from your application menu or terminal:
```bash
nmgui
```

### Hyprland Users

Add this to your config for floating window:
```ini
windowrulev2 = float, title:^(.*Network Manager.*)$
```

## Contributing

This application is still under development and may contain bugs.
If you encounter issues or errors, please open an issue or submit a pull request with a fix.

For problems related to `python-nmcli`, note that this project uses a fork maintained here:
[python-nmcli-fork](https://github.com/s-adi-dev/nmcli)

Pull requests to this fork are welcome, and relevant changes will be forwarded to the original repository.

Contributions of any kind (bug fixes, improvements, or new features) are appreciated. 

## License

GNU General Public License v3.0 - see [LICENSE](./LICENSE) file for details.
