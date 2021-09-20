#! /usr/bin/env python3

import argparse
import struct
from copy import copy
from pathlib import Path
from typing import Tuple


BRIGHTNESSES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
COLOR_PROFILE_PATH = Path("/Library/ColorSync/Profiles/Displays")


def find_color_lcd_profile() -> Path:
    """Find the path of the profile to modify.

    The color profile of the built-in display of a MacBook Pro is called "Color LCD-{uuid}.icc",
    where the UUID is used to match profiles for the particular display."""
    for profile in COLOR_PROFILE_PATH.iterdir():
        if profile.name.startswith("Color LCD") and profile.suffix == ".icc":
            return profile

    raise ValueError("No Color LCD profile was found.")


def icc_brightness_int(brightness: float, min_brightness = 0.05) -> int:
    """Brightness values are stored as integers, with a brightness of 1.0 stored as hex 65536."""
    if brightness > 1.0 or brightness < min_brightness:
        raise ValueError(f"Brightness {brightness} swas invalid.  Must be between {min_brightness} and 1.0.")
    return int(0x00010000 * brightness)


def pack_uint32be(brightness_int: int) -> bytes:
    return struct.pack(">L", brightness_int)


def pack_profile_name(name: str) -> bytes:
    profile_name_bytes = name.encode("utf-16le")
    return profile_name_bytes


def output_profile_mluc_en(brightness: float) -> bytes:
    """Return the "en" localized output profile name for the mluc tag.

    The Display > Color tab in System Preferences uses this tag to display the profile name.
    """
    previous_profile_name = "Color LCD"
    return (f"Dim {brightness}").ljust(len(previous_profile_name))[0:len(previous_profile_name)]


def create_profile(input_profile: bytearray, brightness: float) -> Tuple[str, bytearray]:
    """Create a modified brightness profile.

    :return: (profile name, profile contents)
    """
    profile = copy(input_profile)
    brightness_int = icc_brightness_int(brightness)
    profile_name = output_profile_mluc_en(brightness)

    # We overwrite the "en" localization in the mluc tag to create a new profile name.
    # Since we are not changing any offsets, the old name and new name must be the same length.
    profile_name_bytes = pack_profile_name(profile_name)

    mluc_address = 0x5b9
    profile[mluc_address:mluc_address + len(profile_name_bytes)] = profile_name_bytes

    # We overwrite the R, G, B max brightness values in the ICC profile's vcgt tag.
    # Compute brightness integer to overwrite
    brightness_bytes = pack_uint32be(brightness_int)

    # R, G, B max brightness addresses in the 4088-byte default Color LCD ICC profile
    rgb_addresses = [0xf10, 0xf1c, 0xf28]
    for address in rgb_addresses:
        profile[address:address + len(brightness_bytes)] = brightness_bytes

    return profile_name, profile


def create_profile_path(input_profile_path: Path, profile_name: str, output_dir: Path) -> Path:
    """Create the name of the output profile by grabbing the ID of the input profile."""
    profile_name = profile_name + input_profile_path.stem[len("Color LCD"):] + ".icc"
    return output_dir / profile_name


def main(args):
    input_profile_path = find_color_lcd_profile()
    input_profile = bytearray(input_profile_path.read_bytes())
    output_dir = Path(args.output_dir)
    print(f"Writing modifications of color profile {input_profile_path} ...")

    for brightness in BRIGHTNESSES:
        print(f"Writing profile with max brightness {brightness} ...")
        profile_name, profile = create_profile(input_profile, brightness)
        output_path = create_profile_path(input_profile_path, profile_name, output_dir)
        print(f"Writing profile to {output_path} ...")

        with output_path.open("wb") as f:
            f.write(profile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(COLOR_PROFILE_PATH),
        help="Path to which to write color profiles"
    )
    args = parser.parse_args()
    main(args)


# TODO
# - see if I can write an AppleScript or something to select a particular color profile without
#   going into the settings
# - write up a README
# - write up this cheap hack - blog post
