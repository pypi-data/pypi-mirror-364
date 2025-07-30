# xwarning

`xwarning` is a Python module that enhances the default `warnings` system using [Rich](https://github.com/Textualize/rich), providing beautiful, color-coded warning messages with icons.

## Features

- Emoji-based warning indicators
- Rich-colored terminal output
- Drop-in replacement for `warnings.warn()`
- Built-in support for common warning types:
  - `DeprecationWarning`
  - `UserWarning`
  - `FutureWarning`
  - `RuntimeWarning`
  - `SyntaxWarning`
  - `ImportWarning`
  - `UnicodeWarning`
  - Generic `Warning`
- Optional file logging:
  - If `log_file` is a string, logs to the specified filename
  - If `True`, logs to system temp directory (Windows) or `/var/log` (Linux)
- Fully configurable:
  - Toggle icons on/off
  - Toggle colors on/off


## Installation

```bash
pip install xwarning
```

## Usage

```python
>> from xwarning import warn, warning, configure

# Simple usage you can use 'warn' similar as 'warning'
>> warn("This is deprecated warning !", type="deprecated")

>> warn("This is user warning !", type="user")

>> warn("This is future warning !", type="future")

>> warn("This is runtime warning !", type="runtime")

>> warn("This is syntax warning !", type="syntax")

>> warn("This is import warning !", type="import")

>> warn("This is unicode warning !", type="unicode")

>> warn("This is general warning !", type="general")

>> configure(show_icon=False, show_color=True)

# Logging to file
>> log_path = "warnings.log"
>> configure(log_file=log_path)

>> warn(f"This will go to the log file! with log file name '{log_path}'", type="user")

>> log_path = True
>> configure(log_file=log_path)
>> warn(f"This will go to the log file! with log file name as bool in temp or /var/log directory", type="user")

# Extra instance
>> printer1 = WarningPrinter()
>> printer1.configure(show_icon=False, log_file=True)
>> printer1.warn("this user warning with printer1", type="user")

>> printer2 = WarningPrinter()
>> printer2.configure(show_icon=True, show_color=False)
>> printer2.warn("this runtime warning with printer2", type="runtime")

>> printer1.filterwarnings("ignore", category=UserWarning)

>> printer1.warn("This not will appear as a user warning with `filterwarning`", type="user")
>> printer1.warn("This will appear as a runtime warning without `filterwarning`", type="runtime")


```

## Example Output

```
🛑 DEPRECATED: This is deprecated
⚠️ USER: This is a user warning!
```

[![Example Outputs](https://github.com/cumulus13/xwarning/raw/refs/heads/master/example_outputs.png)](https://github.com/cumulus13/xwarning/raw/refs/heads/master/example_outputs.png)


## License

MIT License. See [LICENSE](./LICENSE) for details.

## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)