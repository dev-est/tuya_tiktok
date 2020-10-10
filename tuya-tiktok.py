import os
from tuyapy import TuyaApi
import time
from bs4 import BeautifulSoup
import requests
import re
import simplejson as json
from fake_useragent import UserAgent
import asyncio


ua = UserAgent()


def get_followers(username):
    header = {"User-Agent": ua.chrome}
    page = requests.get(f"https://www.tiktok.com/@{username}?lang=en", headers=header)
    soup = BeautifulSoup(page.content.decode('utf-8'), 'html.parser')
    data = soup(text=re.compile(r'"shareMeta":'))
    for script in data:
        js = json.loads(script)
        follower_count = int(js['props']['pageProps']['userInfo']['stats']['followerCount'])
    return follower_count


def tiktok_notif(devices,repeat,turn_off=True):
    colours_list = [0,28,64,128,155,180,241,297]

    async def device_colour_control(device,color,saturation,brightness):
        if brightness > 255:
            brightness = 255
        if brightness < 29 :
            brightness = 29
        device.set_color([color,saturation,brightness])
        time.sleep(0.19)
        device.set_brightness(brightness)

    async def toggle_off():
        for i in devices:
            devices[i].turn_off()

    async def main():
        tasks = []
        for t in range(repeat):
            for i in colours_list:
                for j in devices.keys():
                    tasks.append(asyncio.ensure_future(device_colour_control(devices[j],i,100,255)))
        if turn_off:
            tasks.append(asyncio.ensure_future(toggle_off()))

        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

def main():
    username = input("Please enter username: ")
    repeat = int(input("How many times would you like your lights to flash? Max (10): "))
    if repeat > 10:
        repeat = 10
    elif repeat < 0:
        repeat = 1
    api = TuyaApi()
    api.init(os.getenv('TUYA_LOGIN'),os.getenv('TUYA_PASSWORD'),"44","tuya")
    device_id = api.get_all_devices()
    devices = dict((i.name(),i) for i in device_id if i.obj_type == 'light')
    current_followers = get_followers(username)

    while True:
        followers_now = get_followers(username)
        if current_followers != followers_now:
            gained_followers = (int(followers_now) - int(current_followers))
            print(f"Change by {gained_followers}, New Follower count is {followers_now} " )
            tiktok_notif(devices,repeat)
            time.sleep(10)
            current_followers = followers_now
        else:
            print(f"Currently {current_followers} followers")
            time.sleep(100)

if __name__ == "__main__":
    main()