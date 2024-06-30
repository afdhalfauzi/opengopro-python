# livestream.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed, Sep  1, 2021  5:05:45 PM

# """Example to start and view a livestream"""

import argparse
import asyncio
from typing import Any

from rich.console import Console

from open_gopro import Params, WirelessGoPro, constants, proto
from open_gopro.logger import setup_logging
from open_gopro.util import add_cli_args_and_parse, ainput

import serial
import json
import requests

console = Console()  # rich consoler printer
rtmp_URL = "rtmp://angkasatimelapse.com/live/mykey"
wifi_ssid = "BMZimages"
wifi_password = "bennamazarina"
stream_started = False
GOPRO_BASE_URL = "http://10.5.5.9:8080"

#======ID=====
SHUTTER_ID = "146"    #146 photo 145 video
SHUTTER = {
     0 : "AUTO",
     1 : "1/125",
     2 : "1/250",
     3 : "1/500",
     4 : "1/1000",
     5 : "1/2000",
}

ISO_ID = "75"         #75 photo 102 video ISO MIN
ISO = {
     5 : "3200",
     4 : "1600",
     0 : "800",
     1 : "400",
     2 : "200",
     3 : "100",
}

AWB_ID = "115"
AWB = {
    3 : "6500K",
    7 : "6000K",
    2 : "5500K",
    12 : "5000K",
    11 : "4500K",
    0 : "AUTO",
    4  : "NATIVE",
    5 : "4000K",
    10 : "3200K",
    9 : "2800K",
    8 : "2300K",
}

EV_ID = "118"
EV = {
    8 : "-2.0",
    7 : "-1.5",
    6 : "-1.0",
    5 : "-0.5",
    4 : "0.0",
    3 : "0.5",
    2 : "1.0",
    1 : "1.5",
    0 : "2.0",
}

async def main(args: argparse.Namespace) -> None:
    setup_logging(__name__, args.log)
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0.5)
    
    async with WirelessGoPro(args.identifier) as gopro:
        http_command = GOPRO_BASE_URL + "/gp/gpControl/status"
        print("Getting current GoPro settings..")
        response = requests.get(http_command, timeout = 10)
        response.raise_for_status()
        settings_response = json.dumps(response.json())
        settings_json = json.loads(settings_response)
        
        
        SHUTTER_VALUE = settings_json['settings'][SHUTTER_ID]  #int
        ISO_VALUE = settings_json['settings'][ISO_ID]
        AWB_VALUE = settings_json['settings'][AWB_ID]
        EV_VALUE = settings_json['settings'][EV_ID]
        
        #build JSON using dictionary
        settings_json = {
            "stream" : 0,
            "shutter" : SHUTTER[SHUTTER_VALUE],
            "iso" : ISO[ISO_VALUE],
            "awb" : AWB[AWB_VALUE],
            "ev" : EV[EV_VALUE],
        }
        json_string = json.dumps(settings_json)
        print(json_string)
        ser.write(json_string.encode())
        
        print("Waiting for json command..")
        while True:
            if ser.in_waiting:
                json_string = ser.readline().decode("utf-8")
                print(json_string)
                json_data = json.loads(json_string)
                start_stream = json_data['stream']
                shutter = json_data['shutter']
                iso = json_data['iso']
                awb = json_data['awb']
                ev = json_data['ev']
                
                if start_stream == 1:
                    if not stream_started:
                        await start_livestream(args, gopro, ser)
                elif start_stream == 0:
                    await stop_livestream(args, gopro)
                    
                if shutter != SHUTTER_VALUE:
                    http_command = GOPRO_BASE_URL + "/gp/gpControl/setting/" + SHUTTER_ID + "/" + str(shutter)
                    print("Changing shutter speed into " + SHUTTER[shutter])
                    response = requests.get(http_command, timeout = 10)
                    SHUTTER_VALUE =  shutter
                if iso != ISO_VALUE:
                    http_command = GOPRO_BASE_URL + "/gp/gpControl/setting/" + ISO_ID + "/" + str(iso)
                    print("Changing ISO into " + ISO[iso])
                    ISO_VALUE = iso
                    response = requests.get(http_command, timeout = 10)
                if awb != AWB_VALUE:
                    http_command = GOPRO_BASE_URL + "/gp/gpControl/setting/" + AWB_ID + "/" + str(awb)
                    print("Changing AWB into " + AWB[awb])
                    response = requests.get(http_command, timeout = 10)
                    AWB_VALUE = awb
                if ev != EV_VALUE:
                    http_command = GOPRO_BASE_URL + "/gp/gpControl/setting/" + EV_ID + "/" + str(ev)
                    print("Changing EV into " + EV[ev])
                    response = requests.get(http_command, timeout = 10)
                    EV_VALUE = ev


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Connect to the GoPro via BLE only, configure then start a Livestream, then display it with CV2."
    )
    parser.add_argument("--ssid", type=str, help="WiFi SSID to connect to.", default=wifi_ssid)
    parser.add_argument("--password", type=str, help="Password of WiFi SSID.", default=wifi_password)
    parser.add_argument("--url", type=str, help="RTMP server URL to stream to.", default=rtmp_URL)
    parser.add_argument("--min_bit", type=int, help="Minimum bitrate.", default=1000)
    parser.add_argument("--max_bit", type=int, help="Maximum bitrate.", default=1000)
    parser.add_argument("--start_bit", type=int, help="Starting bitrate.", default=1000)
    parser.add_argument(
        "--resolution",
        help="Resolution.",
        choices=list(proto.EnumWindowSize.values()),
        default=proto.EnumWindowSize.WINDOW_SIZE_720,
    )
    parser.add_argument(
        "--fov", help="Field of View.", choices=list(proto.EnumLens.values()), default=proto.EnumLens.LENS_LINEAR
    )
    return add_cli_args_and_parse(parser, wifi=False)

# def update_iso_settings(value):
#     if 

async def start_livestream(args: argparse.Namespace, gopro: WirelessGoPro, ser: serial):
    stream_started = 1
    # async with WirelessGoPro(args.identifier, enable_wifi=False) as gopro:
    await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)
    await gopro.ble_command.register_livestream_status(
        register=[proto.EnumRegisterLiveStreamStatus.REGISTER_LIVE_STREAM_STATUS_STATUS]
    )

    console.print(f"[yellow]Connecting to {wifi_ssid}...")
    await gopro.connect_to_access_point(wifi_ssid, wifi_password)

    # Start livestream
    livestream_is_ready = asyncio.Event()

    async def wait_for_livestream_start(_: Any, update: proto.NotifyLiveStreamStatus) -> None:
        if update.live_stream_status == proto.EnumLiveStreamStatus.LIVE_STREAM_STATE_READY:
            livestream_is_ready.set()

    console.print("[yellow]Configuring livestream...")
    gopro.register_update(wait_for_livestream_start, constants.ActionId.LIVESTREAM_STATUS_NOTIF)
    await gopro.ble_command.set_livestream_mode(
        url=rtmp_URL,
        window_size=args.resolution,
        minimum_bitrate=args.min_bit,
        maximum_bitrate=args.max_bit,
        starting_bitrate=args.start_bit,    
        lens=args.fov,
    )

    # Wait to receive livestream started status
    console.print("[yellow]Waiting for livestream to be ready...\n")
    await livestream_is_ready.wait()

    # TODO Is this still needed?
    await asyncio.sleep(2)

    console.print("[yellow]Starting livestream")
    assert (await gopro.ble_command.set_shutter(shutter=Params.Toggle.ENABLE)).ok

    console.print("[yellow]Livestream is now streaming and should be available for viewing.")
    ser.write(b'{"stream":2}')
    # print("stream2")
    # await ainput("Press enter to stop livestreaming...\n")

    # await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)
    # await gopro.ble_command.release_network()
            
async def stop_livestream(args: argparse.Namespace, gopro: WirelessGoPro):
    # await ainput("Press enter to stop livestreaming...\n")
    await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)
    await gopro.ble_command.release_network()
    stream_started = 0

if __name__ == "__main__":
    asyncio.run(main(parse_arguments()))
# # livestream.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# # This copyright was auto-generated on Wed, Sep  1, 2021  5:05:45 PM

# """Example to start and view a livestream"""

# import argparse
# import asyncio
# from typing import Any

# from rich.console import Console

# from open_gopro import Params, WirelessGoPro, constants, proto
# from open_gopro.logger import setup_logging
# from open_gopro.util import add_cli_args_and_parse, ainput

# import serial
# import json

# console = Console()  # rich consoler printer


# async def main(args: argparse.Namespace) -> None:
#     setup_logging(__name__, args.log)

#     async with WirelessGoPro(args.identifier, enable_wifi=False) as gopro:
#         await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)
#         await gopro.ble_command.register_livestream_status(
#             register=[proto.EnumRegisterLiveStreamStatus.REGISTER_LIVE_STREAM_STATUS_STATUS]
#         )

#         console.print(f"[yellow]Connecting to {args.ssid}...")
#         await gopro.connect_to_access_point(args.ssid, args.password)

#         # Start livestream
#         livestream_is_ready = asyncio.Event()

#         async def wait_for_livestream_start(_: Any, update: proto.NotifyLiveStreamStatus) -> None:
#             if update.live_stream_status == proto.EnumLiveStreamStatus.LIVE_STREAM_STATE_READY:
#                 livestream_is_ready.set()

#         console.print("[yellow]Configuring livestream...")
#         gopro.register_update(wait_for_livestream_start, constants.ActionId.LIVESTREAM_STATUS_NOTIF)
#         await gopro.ble_command.set_livestream_mode(
#             url=args.url,
#             window_size=args.resolution,
#             minimum_bitrate=args.min_bit,
#             maximum_bitrate=args.max_bit,
#             starting_bitrate=args.start_bit,
#             lens=args.fov,
#         )

#         # Wait to receive livestream started status
#         console.print("[yellow]Waiting for livestream to be ready...\n")
#         await livestream_is_ready.wait()

#         # TODO Is this still needed?
#         await asyncio.sleep(2)

#         console.print("[yellow]Starting livestream")
#         assert (await gopro.ble_command.set_shutter(shutter=Params.Toggle.ENABLE)).ok

#         console.print("[yellow]Livestream is now streaming and should be available for viewing.")
#         await ainput("Press enter to stop livestreaming...\n")

#         await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)
#         await gopro.ble_command.release_network()


# def parse_arguments() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="Connect to the GoPro via BLE only, configure then start a Livestream, then display it with CV2."
#     )
#     parser.add_argument("ssid", type=str, help="WiFi SSID to connect to.")
#     parser.add_argument("password", type=str, help="Password of WiFi SSID.")
#     parser.add_argument("url", type=str, help="RTMP server URL to stream to.")
#     parser.add_argument("--min_bit", type=int, help="Minimum bitrate.", default=1000)
#     parser.add_argument("--max_bit", type=int, help="Maximum bitrate.", default=1000)
#     parser.add_argument("--start_bit", type=int, help="Starting bitrate.", default=1000)
#     parser.add_argument(
#         "--resolution",
#         help="Resolution.",
#         choices=list(proto.EnumWindowSize.values()),
#         default=proto.EnumWindowSize.WINDOW_SIZE_720,
#     )
#     parser.add_argument(
#         "--fov", help="Field of View.", choices=list(proto.EnumLens.values()), default=proto.EnumLens.LENS_LINEAR
#     )
#     return add_cli_args_and_parse(parser, wifi=False)


# def entrypoint() -> None:
#     asyncio.run(main(parse_arguments()))


# if __name__ == "__main__":
#     entrypoint()
