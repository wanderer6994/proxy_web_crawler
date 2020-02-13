#! /usr/bin/python3
# rootVIII
from argparse import ArgumentParser
from re import findall
from random import randint, random
from requests import get
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import exit
from threading import Thread
from time import sleep


class ProxyCrawler:
    def __init__(self, url, keyword):
        self.sockets, self.agents = [], []
        self.keyword = keyword
        self.url = url
        self.proxy_host = ''
        self.proxy_port = 0
        self.fp = None
        self.browser = None
        self.request_count = 0
        # request_MAX: # of requests to be made
        # before refreshing the list of proxies
        self.request_MAX = 5
        self.set_agents()
        self.scrape_sockets()

    @staticmethod
    def random_sleep(length):
        if length != 'long':
            sleep(randint(5, 10) + random())
        else:
            sleep(randint(30, 60) + random())

    def set_current_proxy(self):
        self.fp = webdriver.FirefoxProfile()
        self.fp.set_preference('network.proxy.type', 1)
        self.fp.set_preference('network.proxy.http', self.proxy_host)
        self.fp.set_preference('network.proxy.http_port', self.proxy_port)
        self.fp.set_preference('network.proxy.ssl', self.proxy_host)
        self.fp.set_preference('network.proxy.ssl_port', self.proxy_port)
        self.fp.set_preference('general.useragent.override', self.agent())
        self.fp.update_preferences()

    def scrape_sockets(self):
        print('acquiring new proxies')
        r = get("https://www.sslproxies.org/")
        matches = findall(r"<td>\d+\.\d+\.\d+\.\d+</td><td>\d+</td>", r.text)
        revised = [m.replace('<td>', '') for m in matches]
        self.sockets = [s[:-5].replace('</td>', ':') for s in revised]

    def search(self, socket):
        print('starting search')
        temp_socket = socket.split(':')
        self.proxy_host = temp_socket[0]
        self.proxy_port = int(temp_socket[1])
        self.set_current_proxy()
        self.browser = webdriver.Firefox(firefox_profile=self.fp)
        self.browser.get('https://www.bing.com/')
        assert 'Bing' in self.browser.title
        print('using socket: %s:%d' % (self.proxy_host, self.proxy_port))
        print('searching for keyword(s):   %s' % self.keyword)
        self.random_sleep('short')
        search_box = self.browser.find_element_by_name('q')
        self.random_sleep('short')
        search_box.send_keys(self.keyword)
        self.random_sleep('long')
        search_box.send_keys(Keys.RETURN)
        self.random_sleep('long')
        page_index = 0

        # Search until the desired URL is found
        while True:
            page_index += 1
            print('current index:   %d' % page_index)
            page_links = self.browser.find_elements_by_xpath("//a[@href]")
            found_link = None
            for link in page_links:
                if self.url[8:] in link.get_attribute('href'):
                    print('found %s at index %d' % (self.url, page_index))
                    found_link = link
                    break
            if found_link is not None:
                found_link.click()
                break
            else:
                self.random_sleep('long')
                idx = str(page_index + 1)
                self.browser.find_element_by_link_text(idx).click()
                self.random_sleep('short')

        # Found page
        self.random_sleep('short')
        while self.url[8:] not in self.browser.current_url:
            print('Waiting for page to load...')
            self.random_sleep('short')
        target_links = self.browser.find_elements_by_xpath("//a[@href]")
        random_page_num = randint(0, len(target_links) - 1)
        target_link = target_links[random_page_num]
        self.random_sleep('long')
        target_link.click()
        self.random_sleep('long')
        print('Visiting random page: %s' % self.browser.current_url)
        self.random_sleep('long')

    def start_search(self):
        for socket in self.sockets:
            try:
                self.search(socket)
            except Exception as e:
                print('%s\n: %s' % (type(e).__name__, str(e)))
                print('trying next socket...')
            finally:
                self.browser.quit()
                self.request_count += 1
                if self.request_count > self.request_MAX:
                    self.request_count = 0
                    self.scrape_sockets()

    def agent(self):
        return self.agents[randint(0, len(self.agents) - 1)]

    # Add/remove desired user-agents below
    def set_agents(self):
        self.agents = [
            "Opera/9.80 (S60; SymbOS; Opera Mobi/498; U; sv)",
            "Mozilla/2.02 [fr] (WinNT; I)",
            "WeatherReport/1.2.2 CFNetwork/485.12.7 Darwin/10.4.0",
            "W3C_Validator/1.432.2.10",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
            "Cyberdog/2.0 (Macintosh; 68k)",
            "MJ12bot/v1.0.8 (http://majestic12.co.uk/bot.php?+)",
            "Exabot/2.0",
            "Mozilla/5.0 (compatible; news bot /2.1)",
            "curl/7.19.6 (i686-pc-cygwin)",
            "ConveraCrawler/0.4",
            "Mozilla/4.0 (MSIE 6.0; Windows NT 5.1; Search)",
            "EARTHCOM.info/1.6 [www.earthcom.info]",
            "librabot/1.0 (+http://search.msn.com/msnbot.htm)",
            "NetResearchServer/2.5(loopimprovements.com/robot.html)",
            "PHP/5.2.10",
            "msnbot-Products/1.0 (+http://search.msn.com/msnbot.htm)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;)"
        ]


def main():
    while True:
        bot = ProxyCrawler(d.url, d.keyword)
        bot.start_search()


if __name__ == "__main__":
    description = 'Usage: python proxy_crawler.py -u '
    description += '<https://example.com> -k <search keyword>'
    parser = ArgumentParser(description=description)
    parser.add_argument('-u', '--url', required=True, help='url')
    parser.add_argument('-k', '--keyword', required=True, help='keyword')
    d = parser.parse_args()
    if 'https://' not in d.url:
        print('Include protocol in URL: https://')
        exit(1)
    try:
        thread = Thread(target=main)
        thread.daemon = True
        thread.start()
        thread.join()
    except KeyboardInterrupt:
        print('\nExiting\n')
