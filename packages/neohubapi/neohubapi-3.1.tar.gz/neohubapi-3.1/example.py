#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2020-2021 Andrius Štikonas <andrius@stikonas.eu>
# SPDX-License-Identifier: MIT


import asyncio
import logging

from neohubapi import neohub


async def run():
    hub = neohub.NeoHub(host="192.168.1.228")
    system = await hub.get_system()
    live_hub_data = await hub.get_all_live_data()
    devices = live_hub_data[neohub.ATTR_DEVICES]
    print("Thermostats:")
    for device in devices:
        print(f"Target temperature of {device.name}: {device.target_temperature}")
        await device.identify()

    print(f"Target temperature step: {await hub.target_temperature_step()}")


def main():
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(run())


if __name__ == "__main__":
    main()
