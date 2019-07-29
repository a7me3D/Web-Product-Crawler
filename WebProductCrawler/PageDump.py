import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import os 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

from urllib.parse import urlparse

class PageDump():

    def __init__(self):
        #webdriver local path : the driver must be included like mentiond or you should modify it
        
        #where the source code of the wanted page will be saved 
        #I can directly return the source but idk why not
        # src_dir = os.path.dirname(os.path.realpath(__file__)) + r'\Dumps\/'

        #headers to act like normal user (detroit become human)
        #it can be detectd sometimes :p sadly 
        self.headers = {
                    'User-Agent': 'Mozilla/5.0(compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.google.com/',
                    'IsSecureConnection': True,
                    'IsAuthenticated': False
                }
        
        webdriver_local_path = r'\\selenium webdriver\\chromedriver_win32\\chromedriver.exe'
        self.dir_driver = os.path.abspath(os.path.join(__file__,'..')) + webdriver_local_path

        #webdriver options and config
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.headless = True

        prefs = {'profile.managed_default_content_settings.images':2}
        self.chrome_options.add_experimental_option("prefs", prefs)

        #Add Proxy to avoid detection
        PROXY = "" # IP:PORT or HOST:PORT
        self.proxyDict={#'http(s)':PROXY,
            }
        #self.chrome_options.add_argument('--proxy-server=http://%s' % PROXY)

        
    def AccessWebSite(self,url):
        # add http to the url  if not found (required for requests)
        if url.find('http://') == -1 and url.find('https://') == -1:
            url = 'http://' + url
        
        # trying to acces the url 
        print('connecting...')
        time.sleep(3)
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=3)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        try:
            req = session.get(url,proxies=self.proxyDict)
        except requests.exceptions.ConnectionError:         
                print('Bad Response from the website')
                exit()
        except requests.exceptions.Timeout:         
            print('Error occured please check your connection')
            exit()
        except:
            print('Something goes wrong !!')
            quit()

        #checking if the status code is not 2XX aka if the site is not allowed or bad things just happened
        # while accessing the url
        if not(req.ok):
            try: 
                req.raise_for_status()
            except requests.exceptions.HTTPError:             
                print('Forbidden access is denied')
                exit()
        else:
            print("Website Connexion Established :D !")
            return url

    
    def GetSRC(self,url):
        
        driver = webdriver.Chrome(executable_path=self.dir_driver,chrome_options=self.chrome_options,)

        #Test the website and return the url
        url = self.AccessWebSite(url)

        driver.get(url)
        time.sleep(3)

        if driver.current_url != url:
            #Return to base host and take cookies from it
            driver.get('https://'+urlparse(url)[1])
            try:
                cookies = driver.get_cookies()[0]
            except:
                cookies={}
            #Selenium want it like that 
            _cookies_keys= ['name', 'value', 'path', 'domain', 'secure']
            _cookies = {}
            for key in _cookies_keys:
                try:
                    value = cookies[key]
                except :
                    value = ''
                _cookies[key]=value

            #Send cookies to the wanted url   
            driver.add_cookie(_cookies)
            driver.get(url)
            time.sleep(3)
            
        if driver.current_url != url:
            print("Sorry Our Bot has been detected, We are working on it")
            quit()
        else:    
            print('No Probleme :)')
            html =  driver.page_source
            driver.quit()
            return html

        
        
        

    #making the html source file
    # with open(src_dir+fname+'Html.html','w',encoding='UTF-8') as f:
    #     #writing the source code to the file
    #     f.write(str(html))
