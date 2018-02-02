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

## Sample output:

```
$ ./main.py

Team                                     SkyBet               PaddyPower           WilliamHill
------------------------------------------------------------  
Argentina                                15/2                 4/1                  4/7   
Australia                                750/1                125/1                20/1  
Belgium                                  11/1                 9/2                  4/7   
Brazil                                   5/1                  13/5                 1/2   
Colombia                                 40/1                 13/1                 15/8  
Costa Rica                               500/1                175/1                16/1  
Croatia                                  40/1                 12/1                 9/4   
Denmark                                  80/1                 30/1                 4/1   
Egypt                                    200/1                125/1                9/1   
England                                  16/1                 6/1                  8/11  
France                                   11/2                 3/1                  1/2   
Germany                                  9/2                  13/5                 1/2   
Iceland                                  250/1                90/1                 11/1  
Iran                                     500/1                125/1                20/1  
Japan                                    200/1                100/1                7/1   
Mexico                                   100/1                25/1                 9/2   
Morocco                                  500/1                125/1                14/1  
Nigeria                                  250/1                55/1                 12/1  
Panama                                   2000/1               300/1                25/1  
Peru                                     250/1                55/1                 9/1   
Poland                                   50/1                 17/1                 11/4  
Portugal                                 25/1                 17/2                 8/11  
Russia                                   40/1                 14/1                 9/4   
Saudi Arabia                             2000/1               425/1                40/1  
Senegal                                  200/1                55/1                 9/1   
Serbia                                   200/1                55/1                 7/1   
South Korea                              500/1                175/1                16/1  
Spain                                    6/1                  16/5                 1/2   
Sweden                                   100/1                30/1                 11/2  
Switzerland                              100/1                25/1                 7/2   
Tunisia                                  750/1                325/1                14/1  
Uruguay                                  28/1                 11/1                 15/8 
```

