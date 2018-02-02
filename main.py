#!/usr/bin/env python
import argparse
import time
import requests
import re
import logging
from bs4 import BeautifulSoup
#from lxml import html

from selenium import webdriver

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class MarkupError(Exception): 
    pass


class HtmlCrawler:
    
    DEFAULT_PATH = None
    DEFAULT_START_URL = None
    
    def __init__(self, start_url=None, path=None):
        self.start_url = start_url or self.DEFAULT_START_URL
        self.path = path or self.DEFAULT_PATH
        assert self.start_url
    
    def scrape(self):
        """Scrape the website and return parsed table.
        """
        url = self._navigate(self.start_url, self.path)
        soup = self._get_soup(url)
        return self._parse(soup)
        
    def _navigate(self, url, path):
        next_url = url
        for word in path:
            soup = self._get_soup(next_url)
            a = soup.find("a", text=re.compile("^\s*" + word + "\s*$"))
            # Trying to find <a> word <a/> in more complex situation
            if not a:
                a_string = soup.find(string=re.compile("^\s*" + word + "\s*$"))
                if a_string:
                    a_parents = a_string.find_parents("a")
                    if a_parents:
                        a = a_parents[0]
            if not a:
                raise MarkupError(
                    "Error:There is no tag <a> {} </a>"
                    "on the page {}".format(word, next_url))
            next_url = a.get("href")
        return next_url

    def _parse(self, soup):
        try:
            team_string = soup.find(string=re.compile("^\s*" + 'Germany' + "\s*$")) #TODO! Team 
            team_parent = team_string.find_parent()
            team_tag_class = team_parent['class']
            team_tag_name = team_parent.name

            odd_string = soup.find(string=re.compile("^\s*\d*/\d*\s*$"))
            odd_parent = odd_string.find_parent()
            odd_tag_class = odd_parent['class']
            odd_tag_name = odd_parent.name

            odds_list = soup.find_all(odd_tag_name, {"class": odd_tag_class})
            team_list = soup.find_all(team_tag_name, {"class": team_tag_class})
            odds = [odd.text.strip() for odd in odds_list]
            teams = [team.text.strip() for team in team_list]
            return dict(zip(teams, odds))
        except Exception as err:
            raise err
            print(err)
            return {}
    
    def _get_soup(self, url, timeout=10, headers=None):
        try:
            if not headers:
                headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            return soup
        except requests.exceptions.ProxyError as errp:
            print ("Proxy Error:", errp)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error. Timeout is set to {} sec:".format(timeout), errt)
        except requests.exceptions.RequestException as err:
            print ("Error:", err)
        return None


class JavascriptCrawler:

    DEFAULT_PATH = None
    DEFAULT_START_URL = None
    
    def __init__(self, start_url=None, path=None):
        self.start_url = start_url or self.DEFAULT_START_URL
        self.path = path or self.DEFAULT_PATH
        assert self.start_url

        firefox_options = Options()  
        #firefox_options.add_argument("--headless") 
        self.driver = webdriver.Firefox(firefox_options=firefox_options)
    
    def scrape(self):
        """Scrape the website and return parsed table.
        """
        self._navigate(self.start_url, self.path)
        return self._parse()

    def _navigate(self, url, path):
        driver = self.driver
        driver.get(url)
        driver.execute_script("""
            window.getElementsByText = (str) => { 
                  return Array.prototype.slice.call(
                      document.querySelectorAll('a,span')).
                      filter(el => el.textContent.trim() === str.trim());
            } """)

        for text in path:
            found = self._click_on_text(text)
            if not found:
                raise MarkupError(
                    "Cannot found clickable `{text}` on a page"
                    .format(text=text))

    def _click_on_text(self, text):
        """Find a link with the given text and click on it.

        Returns:
            bool, True if the link was found and clicked, False otherwise.
        """
        link = self.driver.execute_script(
            "return window.getElementsByText('{text}', tag = 'a')[0]"
            .format(text=text.replace("'", "\\'")))
        if not link:
            return False

        link.click()
        time.sleep(5)
        return True


class SkyBetCrawler(JavascriptCrawler):
    DEFAULT_START_URL = 'https://www.skybet.com/'
    DEFAULT_PATH = ['Football', 'Competitions', 'World Cup 2018',
                    'Outrights', 'World Cup 2018 Winner']


class WillIamHillCrawler(HtmlCrawler):
    DEFAULT_PATH = ["Football", "World Cup 2018", "World Cup 2018 - To Reach The Quarter Finals"]
                    #"World Cup 2018 - Outright"]
    DEFAULT_START_URL = "http://sports.williamhill.com/"
        
        
class PaddyPowerCrawler(HtmlCrawler):
    DEFAULT_PATH = ["Football Betting", "Outrights", "World Cup 2018"]
    DEFAULT_START_URL = "http://www.paddypower.com"
     
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-interval', 
                        default='5',
                        help="Odds updating interval in minutes, default is %(default)s min."
                        )
    parser.add_argument('--team-names', 
                        default="['Germany', 'France', 'Argentina']",
                        help="Team names, default is %(default)s"
                        )
    args = parser.parse_args()

    
    crawlers = {
        "SkyBet": SkyBetCrawler(),
        #"WilliamHill": WillIamHillCrawler(),
        #"PaddyPower": PaddyPowerCrawler()
    }

    for c in crawlers.values():
        try:
            print(c.scrape())
        except Exception as e:
            raise
            print(e)
    stop

    
    url = "https://www.skybet.com/"
    #r = requests.get(url)
    
    #=============================================== skybet
    js_func_get_by_text = "window.getElementsByText = (str, tag = 'a') => { "\
              "return Array.prototype.slice.call(" \
              "document.getElementsByTagName(tag))." \
              "filter(el => el.textContent.trim() === str.trim());}"
        
    firefox_options = Options()  
    #firefox_options.add_argument("--headless") 
    driver = webdriver.Firefox(firefox_options=firefox_options)
    try:
        driver.get(url)
        driver.implicitly_wait(5)
        res = driver.execute_script(js_func_get_by_text)
        print(res)
        driver.execute_script("window.getElementsByText('Football', tag = 'a')[0].click();")
        driver.implicitly_wait(20)
        time.sleep(10)
        driver.execute_script("window.getElementsByText('Competitions', tag = 'a')[0].click();")
        time.sleep(15)
        driver.implicitly_wait(20)
        driver.execute_script("window.getElementsByText('World Cup 2018', tag = 'span')[0].click();")
        time.sleep(15)
        driver.implicitly_wait(20)
        driver.execute_script("window.getElementsByText('Outrights', tag = 'a')[0].click();")
        
        time.sleep(15)
        driver.implicitly_wait(20)
        driver.execute_script("window.getElementsByText('World Cup 2018 Winner', tag = 'a')[0].click();")
        
        
        dddddddddddddddddddddddd
        football_link = driver.execute_script("$f = window.getElementsByText('Football', tag = 'a')[0]")
        driver.execute_script("$f.click()")
        #football_link[0].click()
        driver.implicitly_wait(10)
        comp_link = driver.execute_script("$c = window.getElementsByText('Competitions', tag = 'a')[0]")
        driver.execute_script("$c.click()")
        print("!!!!", comp_link)
        comp_link[0].click()
        
        driver.implicitly_wait(20)
        #World Cup 2018
        wc_link = driver.execute_script("$p = window.getElementsByText('Premier League', tag = 'span')")
        driver.execute_script("$p.click()")
        print("||| ", wc_link)
        wc_link[0].click()
        
        hjhljhljh
        res = driver.find_elements(By.XPATH, "//a[text()='Football']")
        football_link = res[0]
        print(football_link)
        #driver.SwitchTo().Frame("frameID");
        football_link.click()
        #//*[matches(@id, 'sometext\d+_text')]
        #[matches(.,' doubles ')]
        driver.implicitly_wait(5)
        compet = driver.find_elements(By.XPATH, '//a[contains(text(),"Competitions")]')
        print(compet)
        compet_link = compet[0]
        compet_link.click()
        driver.implicitly_wait(5)
        wc_link = driver.find_element(By.XPATH, "//.[text()='World Cup 2018']")
        print(wc_link)
        wc_link.click()
    except Exception as ex:
        #driver.close()
        raise ex
    

    #==================================================https://mobile.bet365.com
    
    home_url = "https://mobile.bet365.com"


    chrome_options = Options()  
    #chrome_options.add_argument("--headless")  
    
    driver = webdriver.Chrome(chrome_options=chrome_options)  
 
    
        
    driver.get(home_url)
    print(driver.current_url)
    driver.wait = WebDriverWait(driver, 15)
    #print(dir(driver))
    #print(dir(driver.find_elements_by_tag_name('Head')[0]))
    site_dom = driver.find_elements_by_class_name('iconLabel')
    res = driver.find_elements(By.XPATH, "//div[text()='Soccer']")
    print(res)
    #print(site_dom.find_elements_by_id('betslipBar'))
    #p_element = driver.find_element_by_id(id_='intro-text')
    #print(p_element.text)
    
    
    
    
