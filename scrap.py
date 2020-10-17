import re
import time
import csv
import random
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen, Request
from urllib.error import URLError


BASE_URL = 'https://www.futwiz.com'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                          (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
           'Accept-Encoding': 'utf-8'
          }


def get_BS_obj(url, headers):
    request = Request(url, headers=headers)
    futwiz_html = urlopen(request)
    bs = BS(futwiz_html, 'html.parser')
    return bs 


def get_player_info(url):
    bs = get_BS_obj(url, HEADERS)
    stats_list = []

    try:
        name = bs.find('', {'class': 'playerprofile-hbar-ttl'}).h1.get_text()
        print(name)
        details = bs.find('', {'class': 'playerprofile-hbar-ttl'}).div.get_text()
        details = details.split(' |')
        nation = details[0].strip()
        club = details[1].strip()
        print(nation, club)
    except AttributeError:    
        name = '-'
    
    try:
        stats = bs.findAll('', {'class': 'ppdb-d'})
        age = stats[0].text
        height = stats[1].text
        weight = stats[2].text
        foot = stats[4].text
        wage = bs.find('', {'class': 'cprofile-inforbar-stat wagevalue'}).text
        value = bs.find('', {'class': 'cprofile-inforbar-stat career-value'}).text
        print(age, wage)
    except AttributeError:
        age = '-'


    try:
        position = bs.find('', {'class': 'cprofile-infobarmargin'}).text
        print(position)  
    except AttributeError:    
        position = '-'
 
    try:
        rating = bs.find('', {'class': 'cprofstat'}).text
        print(rating)
    except AttributeError:
        rating = '-'
    
    try:
        potential = bs.find('', {'class': 'cplayerprofile-pot'}).p.text.strip()
        print('potential: ',potential)
    except AttributeError:
        potential = '-'

    stats_list.append(name)
    stats_list.append(club)    
    stats_list.append(nation)
    stats_list.append(age)
    stats_list.append(height)
    stats_list.append(weight)
    stats_list.append(foot)
    stats_list.append(wage)
    stats_list.append(value)
    stats_list.append(position)
    stats_list.append(rating)
    stats_list.append(potential)
   
    stats_groups = bs.find('', {'class': 'row stats'}).findAll('', {'class': 'col-2'})
    for stats_set in stats_groups:
        for stat in stats_set.findAll('', {'class': 'individual-stat-bar-stat'}):
            try:
                token = stat.get_text()
            except AttributeError:
                token = '-'
            stats_list.append(token)
        
    return stats_list     


def write_to_scv(data, filepath):
    with open(filepath, 'a') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for row in data:
            writer.writerow(row)


def init_csv_file():
    with open('fieldnames.txt', 'r') as f:
        field_names = f.read().strip().split('\n')
    with open('./data/fifa20.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(field_names)


def scraper():
    page_num = 0
    while 1:
        time.sleep(random.choice([0,1,2]))
        
        # https://www.futwiz.com/en/fifa19/career-mode/players/?page=859
        url = BASE_URL+'/en/fifa20/career-mode/players?page='+str(page_num)
        
        try:
            bs = get_BS_obj(url, HEADERS)
        except URLError:
            print('Error!!! Wrong page url.')
            return
        
        players_table = bs.find('table', {'class': 'table results playersearchresults'})

        if players_table.find('tr', {'class': 'table-row'}) is None:
            # There are no more players.
            print('The processing of FIFA20 data has been completed.\n'+'-'*10) 
            return
        
        print ('page: '+str(page_num))

        data = []
        for player in players_table.tr.next_siblings:       
            if player.find('a') != -1:
                player_url = player.find('a')['href']
                try:
                    player_info = get_player_info(BASE_URL+player_url)
                    data.append(player_info)
                except Exception:
                    print('Something is missing here')
                    pass

        write_to_scv(data, './data/fifa20.csv')
        page_num+=1 


if __name__ == '__main__':
    init_csv_file()
    scraper()
        

