<h1 align="center">NM GUI</h1>

A simple, lightweight GTK4-based GUI for managing networks using **NetworkManager** via `nmcli`.

## Features

- Clean and minimal GTK4 interface  
- Uses **nmcli** under the hood for backend operations  
- Fast and lightweight  
- Binary distribution available — no Python setup required  


## Interface Preview

![Main Interface](assets/interface.png)

## Installation

### Arch Linux

Install the **binary version** from the AUR:

```bash
yay -S nmgui-bin
````

<!-- Or install from source:

```bash
yay -S nmgui
``` -->

### Other Distributions

Manual installation scripts will be added in future updates.

## Manual Installation (Source Build)

If you're building from source, ensure the following dependencies are installed:

### Dependencies

* Python 3.10 or newer
* `python-gobject`
* `python-nmcli`
* `gtk4`
* `NetworkManager`

Clone the repository and run:

```bash
git clone https://github.com/s-adi-dev/nmgui.git
cd nmgui
python3 app/main.py
```

**Note:** The prebuilt binary version does **not** require Python or GTK dependencies. Only `NetworkManager` is required.


## Binary Version

You can download the latest `.bin`, `.zip`, or other release formats from the [Releases Page](https://github.com/s-adi-dev/nmgui/releases).

After downloading (e.g., `main.bin`), make it executable:

```bash
chmod +x nmgui.bin
```
Then run it directly:
```bash
./nmgui.bin
```
**Note:** Ensure NetworkManager is installed on your system.
<br/>
<br/>
Optionally, move the binary to /usr/bin/ (or any directory in your $PATH) to run it globally with:
```bash
sudo mv main.bin /usr/bin/nmgui

# Now you can run it globally
nmgui
```

## Usage

Once installed, launch the app using your application launcher (such as rofi, wofi, fuzzel, anyrun, etc.) or from the terminal:

```bash
nmgui
```

## Hyprland Configuration (Optional)

To launch the application in floating mode in Hyprland, add the following rule to your configuration:

```bash
windowrulev2 = float, title:^(.*Network Manager.*)$
```

## Contributing

Contributions are welcome.
Feel free to open issues, suggest features, or submit pull requests.

## License

This project is licensed under the [GNU General Public License v3.0](./LICENSE).
