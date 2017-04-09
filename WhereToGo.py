#WhereToGo.py

import requests
from bs4 import BeautifulSoup
import re
import time
from statistics import *
from pypinyin import lazy_pinyin

def getHTMLText(url,code='utf-8'):
    try:
        r=requests.get(url,timeout=120)
        r.raise_for_status
        r.encoding=code    
        return r.text
    except:
        print('爬取页面失败')

def weatherSpider(html):
    try:
        soup=BeautifulSoup(html,'html.parser')
        weather=soup.select('div.tqtongji > p')[0].text[0:-15]
        wind=soup.select('div.tqtongji > ul')[1].text.replace('\n',' ')
        print('\n',weather,'\n\n'+'风力情况为：\n\n',wind,'\n\n')
    except:
        print('提取页面失败')
        

def parseJob(salaryMinList,salaryMaxList,html):
    try:
        soup=BeautifulSoup(html,'html.parser')
        salaryRangeList=soup.select('.zwyx')
        for i in salaryRangeList:
            salary=i.text
            if salary.find('-')+1:  #没找到返回-1
                salaryMinList.append(int(salary[:salary.find('-')]))
                salaryMaxList.append(int(salary[salary.find('-')+1:]))
    except:
        print('提取页面失败')

def printJob(city,job,job_num,salaryMinList,salaryMaxList,html):
    average_min = round(mean(salaryMinList))
    average_max = round(mean(salaryMaxList))
    median_min = round(median(salaryMinList))
    median_max = round(median(salaryMaxList))
    print('在{},关键词为{}的工作共有{}份，平均工资为{}-{}，中位数工资为{}-{}\n\n'
          .format(city_input,job,job_num,average_min,average_max,median_min,median_max))
                
def parseCityRent(cityRentList,html):
    try:
        soup=BeautifulSoup(html,'html.parser')
        priceInfoList=soup.find_all(class_='dd-item info')
        rentPriceList=[]
        for price in priceInfoList:
            rentPriceList.append(price.text.split('元')[0][1:])
        #print(rentPriceList[:10])  #debug
        
        areaInfoList=re.findall(r'data-area="\d*?㎡"',html)
        rentAreaList=[]
        for area in areaInfoList:
            rentAreaList.append(area[11:-2])
        #print(rentAreaList[:10])   #debug

        for i, j in zip(rentPriceList,rentAreaList):     
            try:
                cityRentList.append(round(int(i)/int(j)))
            except:
                continue
        #print(len(cityRentList))   #debug        
    except:
        print('提取页面失败')

def parseCityBuy(cityBuyList,html):
    try:
        soup = BeautifulSoup(html,'html.parser')
        buyInfoList=soup.find_all(text=re.compile(('元/㎡')))
        #print(len(buyInfoList))    #debug
        for price in buyInfoList:
            try:
                cityBuyList.append(int(price[:price.find('元')]))
            except:
                continue
        #print(len(cityBuyList))   #debug 
    except:
        print('提取页面失败')

def printCityHouse(city_input,cityRentList,cityBuyList):
    rent_price=round(mean(cityRentList))
    buy_price=round(mean(cityBuyList))
    print('{}的租房平均价格为{}元/平方米/月，二手房平均价格为{}元/平方米\n'
          .format(city_input,rent_price,buy_price))
                                              
if __name__=='__main__':
    city_input=input('请输入城市：')
    city=''.join(lazy_pinyin(city_input))
    job=input('请输入职位关键词：')    
    
    weather_url='http://lishi.tianqi.com/{}/index.html'.format(city)
    html=getHTMLText(weather_url,'gbk')
    weatherSpider(html)
    
    job_url='http://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}'\
            .format(city_input,job)
    html=getHTMLText(job_url)
    soup=BeautifulSoup(html,'html.parser')
    job_num=soup.select('div.seach_yx > span > em')[0].text
    job_depth=int(job_num)//60+1
    if job_depth>90:
        job_depth=90
        
    salaryMinList=[]
    salaryMaxList=[]
    for i in range(job_depth):
        url=job_url+'&p={}'+str(i+1)
        html=getHTMLText(url)
        parseJob(salaryMinList,salaryMaxList,html)
    printJob(city_input,job,job_num,salaryMinList,salaryMaxList,html)    
    
    city_rent_url='http://{}.ganji.com/fang1/o'.format(city)
    city_buy_url='http://{}.ganji.com/fang5/o'.format(city)
    cityRentList=[]
    cityBuyList=[]
    city_depth=2
    for i in range(city_depth):
        url=city_rent_url+str(i+1)
        html=getHTMLText(url)
        parseCityRent(cityRentList,html)
        time.sleep(2)
            
        url=city_buy_url+str(i+1)
        html=getHTMLText(url)
        parseCityBuy(cityBuyList,html)
        time.sleep(2)

    printCityHouse(city_input,cityRentList,cityBuyList)
