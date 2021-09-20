# Reduce white point on Mac laptop built-in displays

The display hardware in laptop and phone screens has a pre-set minimum
brightness.  To reach brightnesses lower than this minimum brightness, iOS
includes an accessibility feature called "Reduce White Point" that displays
white as an intermediate gray value.  MacOS lacks this feature.

This tool generates ICC color profiles for a Mac laptop's built-in display that
allow the white point to be reduced.

# Usage

The color profile generator requires root privileges to write color profiles to
a system location, so it must be run with `sudo`:

```bash
./reduce_white_point.py
```

If you don't trust it, that's fine -- write the color profiles to the working
directory and copy them yourself:

```bash
./reduce_white_point.py --output-dir .
sudo cp *.icc /Library/ColorSync/Profiles/Displays/
```

Once the tool is run, new color profiles will be available in System
Preferences:

![New color profiles](/img/New color profiles.png)

# Dependencies
## Run
This tool requires Python 3 to run.  No additional libraries are required.

# TODO

- Write tooling to select a particular color profile without needing to open
  System Preferences
- This is a cheap hack.  Write up a blog post explaining it.
