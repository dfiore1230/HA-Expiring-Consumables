# HA Expiring Consumables

Home Assistant custom integration to track the life span of consumable items such as water filters, vacuum brushes, or UV lights. It creates a sensor showing how many days remain until replacement and provides a button to reset the start date when the item is changed.

## Features
- Track any consumable with configurable name, type, icon, duration, and start date.
- Sensor entity that reports remaining days and exposes attributes like due date, percent used, and expired status.
- Button entity to mark a consumable as replaced, resetting its start date to today.
- Services to adjust values on the fly: `consumable_expiration.set_start_date`, `consumable_expiration.set_duration`, and `consumable_expiration.mark_replaced`.
- Reconfigure existing consumables from the integration's **Reconfigure** option.

## Installation
1. Install via [HACS](https://hacs.xyz): add `https://github.com/dfiore1230/HA-Expiring-Consumables` as a **Custom Repository** of type *Integration*.
2. Install the integration and restart Home Assistant.
3. Alternatively, copy the `custom_components/consumable_expiration` folder to your Home Assistant `custom_components` directory and restart.

## Configuration
1. Navigate to **Settings → Devices & Services → Add Integration** and search for **Expiring Consumables**.
2. Enter the item name, optional type and icon, the expected duration in days, and the start date. You may also provide an expiry date to automatically calculate the start date.
3. After setup you will get:
   - A sensor displaying the days remaining.
   - A `Mark Replaced` button to reset the start date.
4. Use **Reconfigure** later to change the name, type, icon, duration, or dates.
5. Optional services are available for automations:
   - `consumable_expiration.set_start_date`
   - `consumable_expiration.set_duration`
   - `consumable_expiration.mark_replaced`

## Changelog
- **0.1.20** - Maybe this time it will work??
- **0.1.19** - Fix button idle state and partial option updates
- **0.1.18** - Allow reconfiguring consumables from the UI including name, type, duration and expiry date override
             - Fix expiry date override parsing when provided as a string
             - Ensure replace button state returns to idle after Home Assistant restart
- **0.1.17** – Bug fix for 0.1.16
- **0.1.16** – Set default state of replace button to idle, set override expiry date to respect override start date + days
- **0.1.15** – Set default state of replace button to idle, set override expiry date to respect override start date + days
- **0.1.14** – Remove mandatory fields restriction in editing.
- **0.1.13** – Allow reconfiguring consumables from the UI.
- **0.1.12** – Bug fixes for Expiration Override.
- **0.1.11** – Allow reconfiguring consumables from the UI including name, type, duration and expiry date override.
- **0.1.10** – Link sensor and button to a renamable device.
- **0.1.8** – Revert to original config flow and blank config fixes.
- **0.1.7** – More blank config fixes.
- **0.1.6** – Blank config fixes.
- **0.1.5** – Workflow fixes.
- **0.1.4** – Config Flow GUI fix.
- **0.1.3** – Setup dependencies to ensure HACS compatibility.
- **0.1.2** – Prepare package metadata for release.
- **0.1.1** – Add Home Assistant manifest and basic tests.
- **0.1.0** – Initial release.

See [CHANGELOG.md](CHANGELOG.md) for full details.
