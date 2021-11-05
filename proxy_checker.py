import ctypes
import threading
import time
from multiprocessing.dummy import Pool as ThreadPool
import requests
import json
threads = int(input("How many theads should be used? (Default is 100) \n") or "100")
tmout = int(input("what timeout should be used? (Default is 5s) \n") or "5")
proxies_json = {}
def proxy_check(proxies, type):
    class stats:
        invalid = 0
        working = 0
    def check(x):
        proxy = proxies[x].strip()
        if type == "http":
            proxy_dict = {
                'http': "http://" + proxy,
                'https': "https://" + proxy
            }
        elif type == "socks4":
            proxy_dict = {
                'http': "socks4://" + proxy,
                'https': "socks4://" + proxy
            }
        else: # socks5
            proxy_dict = {
                'http': "socks5://" + proxy,
                'https': "socks5://" + proxy
            }
        try:
            r = requests.get(url="http://azenv.net/", proxies=proxy_dict, timeout=tmout).text
            if r.__contains__("REQUEST_METHOD"):
                proxies_json[proxy] = {}
                proxies_json[proxy]["type"] = type
                stats.working += 1
            else:
                stats.invalid += 1

        except Exception as e:
            stats.invalid += 1


    running = True
    def titlebar_changer():
        while running:
            ctypes.windll.kernel32.SetConsoleTitleW(
                "simplecheck by scorpion3013, edited by xemulated | " +
                "Unchecked Proxies: " + str(len(proxies) - (stats.invalid + stats.working)) +
                " | Working Proxies: " + str(stats.working) +
                " | Bad Proxies: " + str(stats.invalid))
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

    if __name__ == "proxy_checker":
        thread_number_list = []
        for x in range(0, len(proxies)):
            thread_number_list.append(int(x))
        the_focking_threads = thread_starter(thread_number_list, threads)
    running = False
    print(stats.working, type, "are working")