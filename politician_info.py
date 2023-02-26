import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import json
import re
  
url = "https://www.lrs.lt/sip/portal.show?p_r=35299&p_k=1"
  
driver = webdriver.Chrome('./chromedriver') 
driver.get(url) 
  
time.sleep(5) 
  
html = driver.page_source
  
soup = BeautifulSoup(html, "html.parser")

all_divs = soup.find_all('div', class_="smn-big-photo")

first_time_cookie = True
politicans_Id = 0
politicans = []
politicans_wealth_Id = 0
politicans_wealth = []
advisors_Id = 0
advisors = []
business_trips_Id = 0
business_trips = []
factions_Id = 0
factions = []
for div in all_divs:
     birthday = ""
     faction_name = ""
     faction_color = ""

     element = div.find("a", class_="link")
     name_surname = element["title"]
     link_url = element["href"]
     element = div.find("img", class_="border-default")
     image_link = element["src"]

     politicans_Id = politicans_Id + 1

     driver.get(link_url) 

     time.sleep(5) 

     html = driver.page_source

     soup = BeautifulSoup(html, "html.parser")
# Find politician faction
     faction_div = soup.find('div', class_="frakcija")
     if faction_div:
          faction_name = faction_div.find('a')["title"]
# Find politician sitting place
     sitting_place = ""
     
     sitting_place_div = soup.find('div', class_="sn_narys_sale")
     sitting_place = sitting_place_div.find('script')
     text = sitting_place.text.strip().split("'")
     sitting_position = 0
     for t in text:
          if t == "#E3E8EC":
               sitting_position = sitting_position + 1
          elif '#' in t:
               faction_color = t
               break
# Find politician birthday
     life_data = soup.find('div', id="sn_vidines_biografija")
     biografy = life_data.find_all('p')
     for bio in biografy:
          if '1' in bio.text.strip():
               text = bio.text.strip()
               birthday = text[text.find("1"):]
               birthday_numbers = re.findall(r'\d+', birthday)
               birthday_chops = birthday.split(" ")
               for bchop in birthday_chops:
                    if bchop == "sausio":
                         birthday = birthday_numbers[0] + "-01-" + birthday_numbers[1]
                         break
                    elif bchop == "vasario":
                         birthday = birthday_numbers[0] + "-02-" + birthday_numbers[1]
                         break
                    elif bchop == "kovo":
                         birthday = birthday_numbers[0] + "-03-" + birthday_numbers[1]
                         break
                    elif bchop == "balandžio":
                         birthday = birthday_numbers[0] + "-04-" + birthday_numbers[1]
                         break
                    elif bchop == "gegužės":
                         birthday = birthday_numbers[0] + "-05-" + birthday_numbers[1]
                         break
                    elif bchop == "birželio":
                         birthday = birthday_numbers[0] + "-06-" + birthday_numbers[1]
                         break
                    elif bchop == "liepos":
                         birthday = birthday_numbers[0] + "-07-" + birthday_numbers[1]
                         break
                    elif bchop == "rugpjūčio":
                         birthday = birthday_numbers[0] + "-08-" + birthday_numbers[1]
                         break
                    elif bchop == "rugsėjo":
                         birthday = birthday_numbers[0] + "-09-" + birthday_numbers[1]
                         break
                    elif bchop == "spalio":
                         birthday = birthday_numbers[0] + "-10-" + birthday_numbers[1]
                         break
                    elif bchop == "lapkričio":
                         birthday = birthday_numbers[0] + "-11-" + birthday_numbers[1]
                         break
                    elif bchop == "gruodžio":
                         birthday = birthday_numbers[0] + "-12-" + birthday_numbers[1]
                         break
               break
# Find politician career years
     tenures_list = []
     tenures_div = soup.find('div', class_="kadencija")
     text = tenures_div.text.strip()
     tenures_list.extend(re.findall(r'\b\d+\b', text))
     tenures_div = soup.find('div', class_="kadencijos")
     tenures = tenures_div.find_all('a')
     for tenure in tenures:
          text = tenure.text.strip()
          tenures_list.extend(re.findall(r'\b\d+\b', text))
     tenures_list.sort()
# Find politician bussiness trips
     bussiness_trips_div = soup.find('table', id="smn-dabar-komandiruotes")
     if bussiness_trips_div:
          bussiness_trips = bussiness_trips_div.find_all('tr')

          for bussiness_trip in bussiness_trips:
               tds = bussiness_trip.find_all('td')
               text = tds[0].text.strip().split(" - ")
               start_date = text[0]
               end_date = text[1]
               text = tds[1].text.strip()
               description = text
               business_trips_Id = business_trips_Id + 1
               business_trips.append(json.dumps({
                    "id": business_trips_Id, 
                    "politican_id": politicans_Id, 
                    "start_date": start_date, 
                    "end_date": end_date, 
                    "description": tds[1].text.strip()
                    }, ensure_ascii=False))

# Find politician advisors
     abc = soup.find('div', class_="papidlomos_rubrikos")
     link = abc.find('a')["href"]
     driver.get(link) 

     time.sleep(5) 

     html = driver.page_source

     soup = BeautifulSoup(html, "html.parser")

# Save advisors data
     tds = soup.find_all('td', class_="asm-name")
     for td in tds:
          advisors_Id = advisors_Id + 1
          advisors.append(json.dumps({
               "id": advisors_Id, 
               "politican_id": politicans_Id, 
               "name_surname": td.text.strip()
               }, ensure_ascii=False))
# Save politician data
     politicans.append(json.dumps({
          "id": politicans_Id, 
          "name_surname": name_surname, 
          "faction": faction_name, 
          "faction_color": faction_color,
          "image_link": image_link, 
          "birthday": birthday, 
          "sitting_position": sitting_position,
          "tenures": tenures_list, 
          "advisors": len(tds), 
          "link": link_url
          }, ensure_ascii=False))
     # break
driver.close()

# dataFolder = "data_test"
dataFolder = "data"

first_item = True
with open(dataFolder + '/politicians.json', 'w', encoding="utf-8") as out:
     out.write('[')
     for item in politicans:
          if first_item:
               out.write(item)
               first_item = False
          else:
               out.write("," + item)
     out.write("]")

first_item = True
with open(dataFolder + '/advisors.json', 'w', encoding="utf-8") as out:
     out.write('[')
     for item in advisors:
          if first_item:
               out.write(item)
               first_item = False
          else:
               out.write("," + item)
     out.write("]")

first_item = True
with open(dataFolder + '/factions.json', 'w', encoding="utf-8") as out:
     out.write('[')
     for item in factions:
          if first_item:
               out.write(item)
               first_item = False
          else:
               out.write("," + item)
     out.write("]")

first_item = True
with open(dataFolder + '/business_trips.json', 'w', encoding="utf-8") as out:
     out.write('[')
     for item in business_trips:
          if first_item:
               out.write(item)
               first_item = False
          else:
               out.write("," + item)
     out.write("]")

first_item = True
with open(dataFolder + '/wealth.json', 'w', encoding="utf-8") as out:
     out.write('[')
     for item in politicans_wealth:
          if first_item:
               out.write(item)
               first_item = False
          else:
               out.write("," + item)
     out.write("]")