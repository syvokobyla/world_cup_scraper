#!/usr/bin/env python
import argparse
import time
import requests
import re
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class MarkupError(Exception): 
    """Should be thrown if markup of page is not as it was expected."""
    pass


class BaseCrawler:
    """Interface class for crawlers."""
    
    DEFAULT_PATH = None
    DEFAULT_START_URL = None
    
    def __init__(self, start_url=None, path=None):
        self.start_url = start_url or self.DEFAULT_START_URL
        self.path = path or self.DEFAULT_PATH
        assert self.start_url

    def scrape(self):
        """Scrape the website and return parsed table.
        """
        raise NotImplementedError()
   
    def _navigate(self, url, path):
        """Navigate from url to necessary page using key words from list 'path'.
        
        Args:
            url : string
                Starting url.
            path : list of strings
                Words from this list are used to find and click next necessary
                link. And so on. 
                
        Returns:
            string, the link to necessary page.
        """  
        raise NotImplementedError()

    def _parse(self, soup):
        """Parse the soup, find teams and scores.
        
        Args:
            soup : BeautifulSoup
                soup of web page with teams and scores.
        Returns:
            team => score dictionary or {}
        """
        try:
            #Find the class and tag name, where team name is stored.
            team_string = soup.find(string=re.compile("^\s*" + 'Germany' + "\s*$"))
            team_parent = team_string.find_parent()
            team_tag_class = team_parent['class']
            team_tag_name = team_parent.name
            
            #Find the class and tag name, where odd is stored.
            odd_string = soup.find(string=re.compile("^\s*\d*/\d*\s*$"))
            odd_parent = odd_string.find_parent()
            odd_tag_class = odd_parent['class']
            odd_tag_name = odd_parent.name

            #Find all teams and their odds
            odds_list = soup.find_all(odd_tag_name, {"class": odd_tag_class})
            team_list = soup.find_all(team_tag_name, {"class": team_tag_class})
            odds = [odd.text.strip() for odd in odds_list]
            teams = [team.text.strip() for team in team_list]
            return dict(zip(teams, odds))
        except Exception as err:
            raise err
            print(err)
            return {}


class HtmlCrawler(BaseCrawler):
    """Crawler for simple html sites."""
    
    def scrape(self):
        """Scrape the website and return parsed table.
        """
        #Navigate to necessary page. 
        url = self._navigate(self.start_url, self.path)
        #Get soup of that page.
        soup = self._get_soup(url)
        #Return parsed data.
        return self._parse(soup)
        
    def _navigate(self, url, path):
         """Navigate from url to necessary page using key words from list 'path'.
         """
        next_url = url
        for word in path:
            logging.debug("Navigate to %s", word)
            soup = self._get_soup(next_url)
            #Trying to find <a/> containing word from path list. 
            a = soup.find("a", text=re.compile("^\s*" + word + "\s*$"))
            # Trying to find <a> word <a/> in more complex situation.
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
    
    def _get_soup(self, url, timeout=10, headers=None):
        """Get soup from url.
        """
        if not headers:
            #Headers to mimic browser and not be recognized as bot.
            headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        r = requests.get(url, timeout=timeout, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        return soup


class JavascriptCrawler(BaseCrawler):
    """Crawler for js sites."""
    
    def __init__(self, start_url=None, path=None):
        super().__init__(start_url, path)

        firefox_options = Options()
        firefox_options.add_argument("--headless") 
        self.driver = webdriver.Firefox(firefox_options=firefox_options)
    
    def scrape(self):
        """Scrape the website and return parsed table.
        """
        self._navigate(self.start_url, self.path)
        soup = BeautifulSoup(self.driver.page_source)
        return self._parse(soup)

    def _navigate(self, url, path):
         """Navigate from url to necessary page using key words from list 'path'.
         """
        driver = self.driver
        driver.get(url)
        #Execute the js script which looks for element with
        #necessary text and click on it.
        driver.execute_script("""
            window.getLinkByText = (str) => { 
                return Array.prototype.slice.call(
                document.querySelectorAll('a,span')).
                filter(el => el.textContent.trim() === str.trim())[0];
            }

            window.findAndClick = (str) => {
                let link = window.getLinkByText(str);
                if (!link) return false;
                link.click();
                return true;
            }
          """)
        
        for text in path:
            logging.debug("Navigating to %s...", text)
            #Find and click on element with text
            found = self._click_on_text(text)
            if not found:
                raise MarkupError(
                    "Cannot found clickable `{text}` on a page"
                    .format(text=text))
        logging.debug("Succefully reached the path")

    def _click_on_text(self, text):
        """Find a link with the given text and click on it.

        Returns:
            bool, True if the link was found and clicked, False otherwise.
        """
        found = self.driver.execute_script(
            "return window.findAndClick('{text}')"
            .format(text=text.replace("'", "\\'")))
        if found:
            time.sleep(5)

        return found


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



def print_table(table, teams):
    """Pretty print results table for selected teams.

    Args:
        table (dict): source => team => score mapping
        teams (list): teams to print.
    """
    # Print header
    sources = sorted(table.keys())
    dt = datetime.now()
    print()
    print("Information is actual on {}".format(dt.strftime('%A, %d. %B %Y %I:%M%p')))
    print()
    print("{:40} ".format("Team"), end='')
    for source in sources:
        print("{:20} ".format(source), end='')
    print()
    print("-" * 60)

    # Print body
    for team in teams:
        print("{:40} ".format(team), end='')
        for source in sources:
            scores = table[source].get(team, 'NA')
            print("{:20} ".format(scores), end='')
        print()

    # Print footer
    print()
    print()
     
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-interval', 
                        default=5*60,
                        type=int,
                        help="Odds updating interval in secodns, default is %(default)s is"
                        )
    parser.add_argument('--team-names', 
                        default=['Germany', 'Iceland', 'Brazil', 'Saudi Arabia', 
                                 'Australia', 'Senegal', 'Poland', 'Iran', 
                                 'Morocco', 'Colombia', 'Peru', 'Portugal', 
                                 'Denmark', 'Russia', 'Sweden', 'Switzerland', 
                                 'Costa Rica', 'England', 'Japan', 'Egypt', 
                                 'Spain', 'Panama', 'Argentina', 'South Korea', 
                                 'Belgium', 'France', 'Uruguay', 'Mexico', 
                                 'Croatia', 'Nigeria', 'Serbia', 'Tunisia'],
                        type=list,
                        help="Team names, default is %(default)s"
                        )
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    crawlers = {
        "SkyBet": SkyBetCrawler(),
        "WilliamHill": WillIamHillCrawler(),
        "PaddyPower": PaddyPowerCrawler()
    }
    
    #Repeatedly crawl and parse sites, output data. 
    while True:
        table = {}
        all_teams = set()
        for source, c in crawlers.items():
            try:
                scores = c.scrape()
                table[source] = scores
                all_teams |= set(scores.keys())
            except Exception as e:
                logging.warning("Error collecting data from %s: %s", source, e)
                scores = {}

        teams = args.team_names or sorted(all_teams)
        print_table(table, teams)
        time.sleep(args.update_interval)
    
    