from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
#add path to chromedriver
driver=webdriver.Chrome('/usr/bin/chromedriver')
driver.get('https://www.ishares.com/de/privatanleger/de/produkte/251769/?switchLocale=y&siteEntryPassthrough=true#/')
time.sleep(5)
#close the accept cookies window
driver.find_element_by_xpath('//a[@class="optanon-allow-all"]').click()

#clickable area for auss and histo
clickables=driver.find_elements_by_class_name('performance-modal')
clickables[1].click()
time.sleep(5)
#auss
popup=driver.find_element_by_xpath('//div[@aria-describedby="distributionsDialog"]')
driver.execute_script("arguments[0].scrollTop = arguments[1];",popup,100)
output=dict()
temp={}
while 1:
    page=BeautifulSoup(driver.page_source,'lxml')
    table=page.find(id='distroTable')
    for row in table.find_all('tr'):
        if not(len(row.find_all('td'))==0):
            first_column=row.find_all('td')[0].get_text()
            second_column=row.find_all('td')[1].get_text()
            temp[first_column]=second_column
        else:
            continue
    if len(page.find(id='distroTable_next')['class'])==3:
        output['Ausschüttungen']=temp
        break
    driver.execute_script("document.querySelector('#distroTable_next').click()")
driver.find_element_by_xpath('//button[@title="Close"]').click()
#histo
clickables[2].click()
time.sleep(1)
popup2=driver.find_element_by_xpath('//div[@aria-describedby="taxFiguresDialog"]')
driver.execute_script("arguments[0].scrollTop = arguments[1];",popup2,100)
time.sleep(5)
output['Historische Steuerdaten']=list()
while 1:
    page=BeautifulSoup(driver.page_source,'lxml')
    table=page.find(id="taxFiguresTable")
    for row in table.find_all('tr'):
        if not(len(row.find_all('td'))==0):
            output['Historische Steuerdaten'].append([col.get_text() for col in row.find_all('td')])
        else:
            continue
    if len(page.find(id='taxFiguresTable_next')['class'])==3:
        break  
    driver.execute_script("document.querySelector('#taxFiguresTable_next').click()")

driver.refresh()
page=BeautifulSoup(driver.page_source,'lxml')
#scraper function for such element in which tables and pop-ups and buttons are not available
def easy_scrape(div_name,key_name):
    temp=[]
    for d in div_name.find_all('div'):
        if d.find('span',{'class':'caption'}) and d.find('span',{'class':'data'}):
            caption=d.find('span',{'class':'caption'}).get_text()
            data=d.find('span',{'class':'data'}).get_text()
            temp.append({str(caption):str(data)})
    output[key_name]=temp
#selecting div 
eckdaten=page.find(id='keyFundFacts')
#calling function for following div
easy_scrape(eckdaten,'Eckdaten')
portfoliomerkmale=page.find(id='fundamentalsAndRisk')
easy_scrape(portfoliomerkmale,'Portfoliomerkmale')

nachhal=page.find(id='esgAnalytics')
easy_scrape(nachhal,'Nachhaltigkeitseigenschaften')

gesch=page.find(id='productInvolvement')
easy_scrape(gesch,'Geschäftliche Beteiligung')

registeredCountries=page.find(id='registeredCountries')
output['Zum Vertrieb Zugelassen In']=[p.get_text() for p in registeredCountries.find_all('p')]
driver.execute_script('window.scrollTo(0,5470)')

#positionen
temp6=[]

driver.find_element_by_xpath('//a[@data-target="tabsAll"]').click()
time.sleep(3)
driver.execute_script("document.querySelector('html body#emea-ishares-v2.blkPage.page-class-overview-v3.blk-responsive.de_DE div.ls-canvas.content-page-wide-12 div#bodyWrapper.ls-row.body-background div.ls-col div#siteWrapper.ls-row.row0 div.ls-col div.ls-row.row2 div#mainWrapper.ls-area div#w1478358465952.ls-cmp-wrap div#c1478358465952.iw_component div.mobile-collapse div#holdings.fund-component.fund-component-parent.ppv3 div#holdingsTabs div#tabsAll.component-tabs-panel.active div#allHoldingsTab.fund-component.fund-tab.table-loaded div#allHoldingsTable_wrapper.dataTables_wrapper.no-footer div.datatables-utilities.ui-helper-clearfix div.show-all a.toggle-records').click()")
time.sleep(2)
page1=BeautifulSoup(driver.page_source,'lxml')
for row in page1.find(id="allHoldingsTable").find_all('tr'):
    t=[col.get_text() for col in row.find_all('td')]
    if not len(t)==0:
        temp6.append(t)
    
output['Positionen']=temp6
temp7=[]

#portfolio allokation
#geography
for row in page1.find(id='subTabsCountriesDataTable').find_all('tr'):
    t=[col.get_text() for col in row.find_all('td')]
    if not len(t)== 0:
        temp7.append({t[0]:t[1]})
driver.find_element_by_xpath('//a[@data-link-event="portfolio:exposure breakdowns:long-short:Sektor"]').click()
page2=BeautifulSoup(driver.page_source,'lxml')


#sektor
temp8=[]
for row in page2.find(id='tabsSectorDataTable').find_all('tr'):
    t=[col.get_text() for col in row.find_all('td')]
    if not len(t)== 0:
        temp8.append({t[0]:t[1]})
output['Portfolioallokation']={'geography':temp7,'sektor':temp8}


#borsenhandel
temp9=[]
for row in page2.find(id='listingsTable').find_all('tr'):
    t=[col.get_text().replace('\n','') for col in row.find_all('td')]
    if not len(t)==0:
        temp9.append(t)
output['Börsenhandel']=temp9


#make jsonfile
with open('scraped_data.json','w') as jsonfile:
    json.dump(output,jsonfile,indent=6)
    jsonfile.close()

#print full json output
print(output)

driver.close()