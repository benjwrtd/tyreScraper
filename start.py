from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector
import csv,sys,re

# 1) Width – 205, Aspect Ratio – 55, Rim Size - 16
# 2) Width – 225, Aspect Ratio – 50, Rim Size - 16
# 3) Width – 185, Aspect Ratio – 16, Rim Size – 14
testDataArr = [[205,55,16],[225,50,16],[185,16,14]]


tyrescraperDB = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
)

cursor = tyrescraperDB.cursor()
def dexelScrape():
    try:
        with open('dexelOutput.csv','w') as f:
            writer = csv.writer(f)
            writer.writerow(['tyreManufacturer', 'tyrePattern', 'tyreSize','tyrePrice','tyreSeason'])
            
            for testData in testDataArr:
                sleep(2)    
                driver.get(f"http://www.dexel.co.uk/shopping/tyre-results?width={testData[0]}&profile={testData[1]}&rim={testData[2]}&speed=.")
                allTyres = driver.execute_script('return allRecommended')
                for tyreObject in allTyres:
                    if None not in tyreObject.values():
                        tyreManufacturer = tyreObject['manufacturer'].upper()
                        tyrePattern = 'N/A' if tyreObject['pattern_name'] == '' else tyreObject['pattern_name']
                        tyreSize = tyreObject['width']+'/'+tyreObject['profile']+' R'+tyreObject['rim']+' '+tyreObject['load']+tyreObject['speed']
                        tyrePrice = tyreObject['price']
                        tyreSeason = 'Summer' if tyreObject['summer'] == '1' else 'Winter'
                        writer.writerow([tyreManufacturer,tyrePattern,tyreSize,tyrePrice,tyreSeason])
                        insertDataIntoSQL('dexelscrapedata_tbl',(tyreManufacturer,tyrePattern,tyreSize,tyrePrice,tyreSeason))
    except Exception as e:
        print(f'Error has occured: {e}')
        
def nationalScrape():
    try:
        with open('nationalOutput.csv','w') as f:
            writer = csv.writer(f)
            writer.writerow(['tyreManufacturer', 'tyrePattern', 'tyreSize','tyrePrice','tyreSeason'])     
            for testData in testDataArr:
                sleep(2)  
                driver.get(f'https://www.national.co.uk/tyres-search?width={testData[0]}&profile={testData[1]}&diameter={testData[2]}')
                soup = BeautifulSoup(driver.page_source,'html.parser')
                allTyres = soup.find_all('div',class_='col-md-6 tyreDisplay')
                for tyresObject in allTyres: 
                    tyreManufacturer= tyresObject.get('data-brand').upper()
                    tyrePattern = tyresObject.find('a',class_='pattern_link').text
                    tyreSize = tyresObject.find("p",text=re.compile(str(testData[0]))).getText().strip()
                    tyrePrice= tyresObject.get('data-sort')
                    tyreSeason= tyresObject.get('data-tyre-season')
                    writer.writerow([tyreManufacturer,tyrePattern,tyreSize,tyrePrice,tyreSeason])
                    insertDataIntoSQL('nationalscrapedata_tbl',(tyreManufacturer,tyrePattern,tyreSize,tyrePrice,tyreSeason))
    except Exception as e:
        print(f'Error has occured: {e}')            
            

def insertDataIntoSQL(table,values):
    try:
        if len(values) != 0:
            sql = f'INSERT INTO {table} (tyreManufacturer,tyrePattern,tyreSize,tyrePrice,tyreSeason) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql,values)
            tyrescraperDB.commit()
    except Exception as e:
        print(f'Error has occured: {e}') 


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("-disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options, executable_path=r"chromedriver.exe")
    if len(sys.argv) > 1:
        if sys.argv[1] == 'dexelScrape':
            print('Running dexelScrape')
            dexelScrape()
        elif sys.argv[1] == 'nationalScrape':
            print('Running nationalScrape')
            nationalScrape()
        elif sys.argv[1] == 'help':
            print(f'''
Commands:
    nationalScrape - Scrapes www.national.co.uk for tyre information, inserts into mysqlDB and exports to nationalOutput.csv
    dexelScrape - Scrapes www.dexel.co.uk for tyre information, inserts into mysqlDB and exports to dexelOutput.csv
    help - Shows this.
              ''')
    else:
        print(f'''
No command given
Commands:
    nationalScrape - Scrapes www.national.co.uk for tyre information, inserts into mysqlDB and exports to nationalOutput.csv
    dexelScrape - Scrapes www.dexel.co.uk for tyre information, inserts into mysqlDB and exports to dexelOutput.csv
    help - Shows this.
              ''')
        



driver.quit()

