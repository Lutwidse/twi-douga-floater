import argparse, random, string, datetime, time, threading
import requests, urllib3.request, urllib3.contrib.socks, socket, socks
from pathlib import Path
from requests import Timeout
from urllib3.exceptions import MaxRetryError
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser("れ～どめ～")
parser.add_argument("-tv", "--target_views", help="目標の閲覧数", type=int, required=True)
parser.add_argument("-t", "--threads", help="スレッド数", type=int, default=5, required=False)
parser.add_argument("-p", "--proxies", help="プロキシ", type=lambda p: Path(p).absolute(), required=True)
parser.add_argument("-v", "--videos", help="動画", type=lambda p: Path(p).absolute(), required=True)
args = parser.parse_args()

class Config(object):
    def __init__(self):
        self.URN = "www.nurumayu.net:PORT/twidouga/gettwi.php"
        self.CLIENT_TEXT = f"[twi-douga-floater]"
        self._PROXY_TEST_UA = {"User-agent": "Mozilla/5.0"}
        self.PROXY_TIMEOUT = 10
        self.OBSERVER_DELAY = 10
        self.REQUEST_RANDOM_DELAY = 10
        self.REQUEST_THRESHOLD = 5
        self.TARGET_VIEWS = args.target_views

        self.req_count = 0

        self.len_proxies = 0
        self.len_twitter_videos = 0

        self.proxies = []
        self.twitter_videos = {}

        # プロキシ
        unchecked_proxies = []
        with open(args.proxies) as f:
            lines = f.readlines()
            for l in lines:
                l = l.replace("\n", "")
                unchecked_proxies.append(l)
            f.close()

        print(f"{self.get_CLIENT_TEXT()} プロキシを検証中…")

        # TODO:try-exceptを使って簡潔にまとめる、その他の関数も適切にエラー処理を行うようにする

        pt = []

        for ip_port in unchecked_proxies:
            pt.append(threading.Thread(target=self._proxy_check_socks4_socks5, args=("socks4", ip_port,)))
        for t in pt:t.start()
        for t in pt:t.join()
        pt.clear()

        print(f"{self.get_CLIENT_TEXT()} 検証完了 [socks4]")

        self._proxy_del_unchecked_proxies(unchecked_proxies)

        for ip_port in unchecked_proxies:
            pt.append(threading.Thread(target=self._proxy_check_socks4_socks5, args=("socks5", ip_port,)))
        for t in pt:t.start()
        for t in pt:t.join()
        pt.clear()

        print(f"{self.get_CLIENT_TEXT()} 検証完了 [socks5]")

        self._proxy_del_unchecked_proxies(unchecked_proxies)

        for ip_port in unchecked_proxies:
            pt.append(threading.Thread(target=self._proxy_check_socks4_socks5, args=("http", ip_port,)))
        for t in pt:t.start()
        for t in pt:t.join()
        pt.clear()

        print(f"{self.get_CLIENT_TEXT()} 検証完了 [http]")

        self._proxy_del_unchecked_proxies(unchecked_proxies)

        for ip_port in unchecked_proxies:
            pt.append(threading.Thread(target=self._proxy_check_socks4_socks5, args=("https", ip_port,)))
        for t in pt:t.start()
        for t in pt:t.join()
        pt.clear()

        print(f"{self.get_CLIENT_TEXT()} 検証完了 [https]")

        self.update_len_proxies()
        print(f"{self.get_CLIENT_TEXT()} 検証完了 | 有効なプロキシ: {self.get_len_proxies()}個")
        
        # 動画
        with open(args.videos) as f:
            lines = f.readlines()
            for l in lines:
                l = l.replace("\n", "")
                self.twitter_videos[l] = 0
            f.close()
            self.update_len_twitter_videos()
        
        self.LEN_PROXIES = self.get_len_proxies()
        self.LEN_TWITTER_VIDEOS = self.get_len_twitter_videos()

    # ---Getter
    def get_req_count(self):
        return self.req_count
    
    def get_len_proxies(self):
        return len(self.proxies)
        
    def get_len_twitter_videos(self):
        return len(self.twitter_videos)

    def get_CLIENT_TEXT(self):
        return f"{self.CLIENT_TEXT} | {self.get_now()} |"
    
    # ---Setter
    def set_req_count(self):
        self.req_count += 1

    # ---Deleter
    def del_proxy(self, proxy):
        try:
            self.proxies.remove(proxy)
        except ValueError:
            pass

    def del_twitter_video(self, key):
        self.twitter_videos.pop(key)

    # ---Updater
    def update_len_proxies(self):
        self.len_proxies = len(self.proxies)

    def update_len_twitter_videos(self):
        self.len_twitter_videos = len(self.twitter_videos)
    
    # ---Proxy
    def _proxy_check_socks4_socks5(self, scheme, ip_port):
        try:
            proxy = f"{scheme}://{ip_port}"
            proxy_manager = urllib3.contrib.socks.SOCKSProxyManager(proxy)
            proxy_manager.request("GET", "http://www.google.com", headers=self._PROXY_TEST_UA, timeout=urllib3.Timeout(connect=self.PROXY_TIMEOUT, read=self.PROXY_TIMEOUT+5))
            
            self.proxies.append(proxy)
        except Timeout:
                pass
        except urllib3.exceptions.MaxRetryError:
            pass
        except urllib3.exceptions.NewConnectionError:
            pass
        except ValueError:
            pass

    def _proxy_check_http_https(self, scheme, ip_port):
        try:
            proxy = f"{scheme}://{ip_port}"
            proxy_manager = urllib3.ProxyManager(proxy)
            proxy_manager.request("GET", f"{scheme}://www.google.com", headers=self._PROXY_TEST_UA, timeout=urllib3.Timeout(connect=self.PROXY_TIMEOUT, read=self.PROXY_TIMEOUT+5))
            
            self.proxies.append(proxy)
        except Timeout:
                pass
        except urllib3.exceptions.MaxRetryError:
            pass
        except urllib3.exceptions.NewConnectionError:
            pass
        except ValueError:
            pass

    def _proxy_del_unchecked_proxies(self, unchecked_proxies):
        for p in self.proxies:
            _, ip_port = p.split("://")
            if ip_port in unchecked_proxies:
                unchecked_proxies.remove(ip_port)

    # ---Helper
    def get_now(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def random_ua(self):
        ua = UserAgent()
        user_agent = ua.random
        return user_agent

    def random_name(self, n):
        randlst = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
        return ''.join(randlst)

    def progress_check(self):
        return self.get_len_proxies() and self.get_len_twitter_videos()

    # random range number
    def rrn(self, n):
        return random.randrange(9**n, 10**n)

class ObserverClient(threading.Thread):
    def __init__(self, conf, lock):
        threading.Thread.__init__(self)
        self.conf = conf
        self.lock = lock

    def run(self):
        while self.conf.progress_check():
            time.sleep(self.conf.OBSERVER_DELAY)

            with self.lock:
                for video_url, video_count in list(list(self.conf.twitter_videos.items())):
                    if self.conf.TARGET_VIEWS <= video_count:
                        print(f"{self.conf.get_CLIENT_TEXT()} 完了 [ {video_url} ]")
                        self.conf.del_twitter_video(video_url)
                        self.conf.update_len_twitter_videos()
                        
                
                req_count = self.conf.get_req_count()
                info_text = "{}{}{}".format(
                    f"{self.conf.get_CLIENT_TEXT()} リクエスト [ 送信:{req_count}件 | 残り:{self.conf.LEN_TWITTER_VIDEOS * self.conf.TARGET_VIEWS - req_count}件 ] | ",
                    f"動画 [ 完了:{self.conf.LEN_TWITTER_VIDEOS - self.conf.get_len_twitter_videos()}個 | 残り:{self.conf.get_len_twitter_videos()}個 ] | ",
                    f"プロキシ [ 有効:{self.conf.get_len_proxies()}個 | 規制:{self.conf.LEN_PROXIES - self.conf.get_len_proxies()}個 ]"
                    )
                    
                print(info_text)

        print(f"{self.conf.get_CLIENT_TEXT()} 終了")
        input()
        exit(1)

class RequestClient(threading.Thread):
    def __init__(self, conf, lock):
        threading.Thread.__init__(self)
        self.conf = conf
        self.lock = lock

    def run(self):
        while self.conf.progress_check():
            try:
                time.sleep(random.randrange(self.conf.REQUEST_RANDOM_DELAY))
                random_proxy = self.get_random_proxy()
                protocol, _ = random_proxy.split("://")
                
                proxy_manager = None
                
                scheme = ""
                port = ""
                
                if protocol == "socks4" or protocol == "socks5":
                    proxy_manager = urllib3.contrib.socks.SOCKSProxyManager(random_proxy)
                    scheme = "https"
                    port = "443"
                elif protocol == "http":
                    proxy_manager = urllib3.ProxyManager(random_proxy)
                    scheme = "http"
                    port = "80"
                elif protocol == "https":
                    proxy_manager = urllib3.ProxyManager(random_proxy)
                    scheme = "https"
                    port = "443"
                    
                video_url, _ = self.get_random_twitter_video_pairs()
                
                headers, data = self.get_request_context(video_url)
                headers = headers.update(self.get_random_cookies())
                
                i, j = self.conf.URN.split("PORT")
                
                resp = proxy_manager.request("POST", f"{scheme}://{i}{port}{j}", headers=headers, fields=data, timeout=urllib3.Timeout(connect=self.conf.PROXY_TIMEOUT, read=self.conf.PROXY_TIMEOUT+5), retries=urllib3.Retry(self.conf.REQUEST_THRESHOLD, redirect=self.conf.REQUEST_THRESHOLD))
                
                status_code = resp.status
                
                if status_code == 403:
                    with self.lock:
                        self.conf.del_proxy(random_proxy)
                else:
                    with self.lock:
                        self.conf.twitter_videos[video_url] += 1
                        self.conf.set_req_count()

            except urllib3.exceptions.ReadTimeoutError:
                pass
            except urllib3.exceptions.MaxRetryError:
                pass
            except urllib3.exceptions.ConnectTimeoutError:
                pass
            except urllib3.exceptions.ProtocolError:
                pass
            except KeyError:
                # ぬるぽ ガッ
                pass
                
    def get_request_context(self, url):
        random_boundary = self.conf.random_name(16)
        headers = {"Connection": "close", "Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1", "Origin": f"https://www.nurumayu.net", "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{random_boundary}", "User-Agent": self.conf.random_ua(), "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://www.nurumayu.net/twidouga/gettwi.php", "Accept-Encoding": "gzip, deflate", "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"}
        data = {"param": url, "exec": "輸出"}
        return headers, data

    def get_random_twitter_video_pairs(self):
        try:
            return random.choice(list(list(self.conf.twitter_videos.items())))
        except IndexError:
            # ぬるぽ ガッ
            pass


    def get_random_cookies(self):
        return {"_ga": f"GA1.2.{self.conf.rrn(9)}.{self.conf.rrn(10)}", "_gid": f"GA1.2.{self.conf.rrn(9)}.{self.conf.rrn(10)}", "_gat": "1", "adr_id": f"{self.conf.random_name(48)}"}

    def get_random_proxy(self):
        proxy = random.choice(self.conf.proxies)
        return proxy

if __name__ == "__main__":
    conf = Config()
    lock = threading.Lock()
    oc = ObserverClient(conf, lock)
    oc.start()
    for _ in range(args.threads):
        rc = RequestClient(conf, lock)
        rc.start()