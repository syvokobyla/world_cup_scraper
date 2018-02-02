# Task

Task is to write a BOT, which can extract odds/probability for all the teams in World Cup 2018 Win Outright market from links give below and generate a real-time matrix from it. Code should either print matrix to screen or save it in file, which should update at given interval (by default every 5 minutes). Preferably use text processing/analysis to navigate to correct match link from home URL instead of hardcoding the start URL. Team names can also be used as parameter(expected given) to locate correct odds elements on page.

1. http://sports.williamhill.com/bet/en-gb/betting/e/1644903/World+Cup+2018+-+Outright.html
2. https://mobile.bet365.com/#type=Coupon;key=1-172-1-26326924-2-0-0-0-2-0-0-0-0-0-1-0-0-0-0-0-0;ip=0;lng=1;anim=1
3. http://www.paddypower.com/football/international-football/world-cup-2018?ev_oc_grp_ids=1828129
4.  https://www.skybet.com/football/world-cup-2018/event/16742642



## Prerequisites

Python requirements:

     $ pip install beautifulsoup4 selenium
     
Firefox and [geckodriver](https://github.com/mozilla/geckodriver) are required for scraping sites rendered in Javascript. Firefox will be started in headless mode.
    

## Workflow notes
1. Navigation to correct match link is made by text processing/analysis. The chain of words for navigation have to be provided. Example for SkyBet: ['Football', 'Competitions', 'World Cup 2018', 'Outrights', 'World Cup 2018 Winner']. At the moment list of that words are hardcoded. In the future it can be configured if necessary.

## Warnings
1. At the moment part of work for https://mobile.bet365.com/ is not finished.
2. The world cup outright page from williamhill.com is not valid anymore. So for demo data is collecting for "World Cup 2018 - To Reach The Quarter Finals".



