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

f = open('data/politicians.json', 'r', encoding="utf-8")
data = json.load(f)
f.close()
first_time_cookie = True
politicans_wealth_Id = 0
politicans_wealth = []
politicans_spouses_wealth_Id = 0
politicans_spouces_wealth = []
politicans_spouses_Id = 0
politicans_spouces = []
for politician in data:
    print(politician["name_surname"])
    driver.get(url)

    time.sleep(10)

    if first_time_cookie:
        driver.find_element(By.ID, "_CookiePolicy_agreeBtn").click()
        first_time_cookie = False

    driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))

    nameList = politician['name_surname'].split(" ")

    sbox = driver.find_element(By.ID, "tbVardas")
    sbox.send_keys(nameList[0])

    sbox = driver.find_element(By.ID, "tbPavarde")
    sbox.send_keys(nameList[len(nameList)-1])

    dbox = driver.find_element(By.ID, "butIeskoti")
    dbox.click()

    time.sleep(20)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    note = ""
    divRasta = soup.find("div", id="divRasta")
    rastaNumber = re.findall(r'\d+', divRasta.text.strip())
    if int(rastaNumber[0]) != 1:
        note = politician["name_surname"] + \
            " turi " + rastaNumber[0] + " atitikmenų."
        driver.get(url)

        time.sleep(10)

        driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))

        sbox = driver.find_element(By.ID, "tbVardas")
        sbox.send_keys(nameList[0])

        sbox = driver.find_element(By.ID, "tbPavarde")
        sbox.send_keys(nameList[len(nameList)-1])

        select_element = driver.find_element(By.NAME, 'ddPareigGr')
        select = Select(select_element)
        select.select_by_value("506")

        dbox = driver.find_element(By.ID, "butIeskoti")
        dbox.click()

        time.sleep(20)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

    bs = soup.find_all("b")
    years_declared = set()
    for b in bs:
        for f in re.findall(r'\b\d+\b', b.text.strip()):
            years_declared.add(int(f))
    years_declared = sorted(years_declared, reverse=True)
    years_Id = 0

    tables = soup.find_all("table", class_="lentele")
    foundSpouse = False
    foundSpouseFirstTime = True

    for table in tables:
        if foundSpouse:
            foundSpouse = False
            continue

        politicans_wealth_description = []
        politicans_wealth_number = []
        politicans_wealth_Id = politicans_wealth_Id + 1
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
                    if foundSpouseFirstTime:
                        politicans_spouses_Id = politicans_spouses_Id + 1
                        spouseName = text.split("\n")[0]
                        politicans_spouces.append(json.dumps({
                            "id": politicans_spouses_Id,
                            "name_surname": spouseName,
                            "politican_id":  politician['id']
                        }, ensure_ascii=False))
                        foundSpouseFirstTime = False
                    break
                if text.isnumeric():
                    politicans_wealth_number.append(int(text))
                    continue
                politicans_wealth_description.append(text)
            if foundSpouse:
                break
        year_data = json.loads(json.dumps({
            "id": politicans_wealth_Id,
            "year_declared": years_declared[years_Id-1],
            "politican_id": politician['id'],
            "note": note,
            'descriptions': politicans_wealth_description,
            'numbers': politicans_wealth_number
        }, ensure_ascii=False))
        politicans_wealth.append(json.dumps(year_data, ensure_ascii=False))
    driver.switch_to.default_content()
    # break
driver.close()

# dataFolder = "data_test"
dataFolder = "data"

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

first_item = True
with open(dataFolder + '/spouses.json', 'w', encoding="utf-8") as out:
    out.write('[')
    for item in politicans_spouces:
        if first_item:
            out.write(item)
            first_item = False
        else:
            out.write("," + item)
    out.write("]")
