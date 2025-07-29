"""Abstraction layer for device interaction - Light."""
# src/utec_py_LF2b2w/devices/light.py

from typing import Tuple  # noqa: UP035

from .device import BaseDevice
from .device_const import (
    BrightnessRange,
    ColorState,
    ColorTempRange,
    DeviceCapability,
    DeviceCommand,
    SwitchState,
)


class Light(BaseDevice):
    """Represents a Light device in the U-Home API.

    Maps to Home Assistant's light platform.
    """

    @property
    def is_on(self) -> bool:
        """Get light state."""
        state = self._get_state_value(DeviceCapability.SWITCH, "switch")
        return state == SwitchState.ON if state is not None else False

    @property
    def brightness(self) -> int | None:
        """Get brightness level (0-100)."""
        return self._get_state_value(DeviceCapability.BRIGHTNESS, "level")

    @property
    def color_temp(self) -> int | None:
        """Get color temperature in Kelvin."""
        return self._get_state_value(DeviceCapability.COLOR_TEMPERATURE, "temperature")

    @property
    def rgb_color(self) -> Tuple[int, int, int] | None:
        """Get RGB color."""
        color_data = self._get_state_value(DeviceCapability.COLOR, "color")
        if color_data:
            color = ColorState.from_dict(color_data)
            return (color.r, color.g, color.b)
        return None

    @property
    def supported_features(self) -> set:
        """Get supported features for Home Assistant."""
        features = set()
        if self.has_capability(DeviceCapability.BRIGHTNESS):
            features.add("brightness")
        if self.has_capability(DeviceCapability.COLOR):
            features.add("color")
        if self.has_capability(DeviceCapability.COLOR_TEMPERATURE):
            features.add("color_temp")
        return features

    async def turn_on(self, **kwargs) -> None:
        """Turn on the light with optional attributes."""
        # Basic on command
        command = DeviceCommand(
            capability=DeviceCapability.SWITCH,
            name="switch",
            arguments={"value": SwitchState.ON},
        )
        await self.send_command(command)

        # Handle additional attributes
        if "brightness" in kwargs:
            await self.set_brightness(kwargs["brightness"])
        if "color_temp" in kwargs:
            await self.set_color_temp(kwargs["color_temp"])
        if "rgb_color" in kwargs:
            await self.set_rgb_color(*kwargs["rgb_color"])

    async def turn_off(self) -> None:
        """Turn off the light."""
        command = DeviceCommand(
            capability=DeviceCapability.SWITCH,
            name="switch",
            arguments={"value": SwitchState.OFF},
        )
        await self.send_command(command)

    async def set_brightness(self, brightness: int) -> None:
        """Set brightness level."""
        if not BrightnessRange.MIN <= brightness <= BrightnessRange.MAX:
            raise ValueError(
                f"Brightness must be between {BrightnessRange.MIN} and {BrightnessRange.MAX}"
            )
        command = DeviceCommand(
            capability=DeviceCapability.BRIGHTNESS,
            name="level",
            arguments={"value": brightness},
        )
        await self.send_command(command)

    async def set_color_temp(self, temp: int) -> None:
        """Set color temperature."""
        if not ColorTempRange.MIN <= temp <= ColorTempRange.MAX:
            raise ValueError(
                f"Color temperature must be between {ColorTempRange.MIN}K and {ColorTempRange.MAX}K"
            )
        command = DeviceCommand(
            capability=DeviceCapability.COLOR_TEMPERATURE,
            name="temperature",
            arguments={"value": temp},
        )
        await self.send_command(command)

    async def set_rgb_color(self, red: int, green: int, blue: int) -> None:
        """Set RGB color."""
        color = ColorState(r=red, g=green, b=blue)
        command = DeviceCommand(
            capability=DeviceCapability.COLOR,
            name="color",
            arguments={"value": color.to_dict()},
        )
        await self.send_command(command)
