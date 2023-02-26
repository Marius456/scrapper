import json
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

url = "https://www.vmi.lt/evmi/metines-gyventojo-seimos-turto-deklaracijos-duomenu-israsai"

driver = webdriver.Chrome('./chromedriver')

f = open('data/spouses.json', 'r', encoding="utf-8")
data = json.load(f)
f.close()
first_time_cookie = True
spouses_wealth_Id = 0
spouses_wealth = []
for politician_spouse in data:
    print(politician_spouse["name_surname"])
    driver.get(url)

    time.sleep(10)

    if first_time_cookie:
        driver.find_element(By.ID, "_CookiePolicy_agreeBtn").click()
        first_time_cookie = False

    driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))

    nameList = politician_spouse['name_surname'].split(" ")

    sbox = driver.find_element(By.ID, "tbVardas")
    sbox.send_keys(nameList[0])

    sbox = driver.find_element(By.ID, "tbPavarde")
    sbox.send_keys(nameList[len(nameList)-1])

    dbox = driver.find_element(By.ID, "butIeskoti")
    dbox.click()

    time.sleep(20)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    divRasta = soup.find("div", id="divRasta")
    rastaNumber = re.findall(r'\d+', divRasta.text.strip())
    if int(rastaNumber[0]) != 1:
        print(politician_spouse["name_surname"] +
              " turi " + rastaNumber[0] + " atitikmenų.")
        continue

    bs = soup.find_all("b")
    years_declared = set()
    for b in bs:
        for f in re.findall(r'\b\d+\b', b.text.strip()):
            years_declared.add(int(f))
    years_declared = sorted(years_declared, reverse=True)
    years_Id = 0

    tables = soup.find_all("table", class_="lentele")
    foundSpouse = False

    for table in tables:
        if foundSpouse:
            foundSpouse = False
            continue

        spouses_wealth_description = []
        spouses_wealth_number = []
        spouses_wealth_Id = spouses_wealth_Id + 1
        years_Id = years_Id + 1
        trs = table.find_all("tr")
        for tr in trs:
            for td in tr.find_all('td'):
                text = td.text.strip()
                for input in td.find_all('input', value="Rodyti/slėpti sutuoktinio duomenis"):
                    if 'sutuoktinio' in input['value']:
                        foundSpouse = True
                        break
                if foundSpouse:
                    break
                if text.isnumeric():
                    spouses_wealth_number.append(int(text))
                    continue
                spouses_wealth_description.append(text)
            if foundSpouse:
                break
        spouses_wealth.append(json.dumps({
            "id": spouses_wealth_Id,
            "year_declared": years_declared[years_Id-1],
            "politician_spouse_id": politician_spouse['id'],
            'descriptions': spouses_wealth_description,
            'numbers': spouses_wealth_number
        }, ensure_ascii=False))
    driver.switch_to.default_content()
    # break
driver.close()

# dataFolder = "data_test"
dataFolder = "data"

first_item = True
with open(dataFolder + '/spouses_wealth.json', 'w', encoding="utf-8") as out:
    out.write('[')
    for item in spouses_wealth:
        if first_item:
            out.write(item)
            first_item = False
        else:
            out.write("," + item)
    out.write("]")
