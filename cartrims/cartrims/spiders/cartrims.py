# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 07:49:16 2019

@author: Sam
"""

from scrapy import Spider
from cartrims.items import CartrimsItem
from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from urllib import request
from scrapy.selector import Selector


class Carsreview(Spider):
    name = 'cartrims'
    url = 'https://www.cars.com/research/'
    response_ = get(url)
    page_html = BeautifulSoup(response_.text,'html.parser')
    page_title = page_html.find('title').text
    
    try:
        main_left = page_html.find('script', attrs = {'id':'REDUX_STATE'})
    except:
        None    
        
    data=re.split('{|}',main_left.get_text())
    data=[i for i in data if re.search(r'makeId', i)]
    data=[','.join(i.split(':')) for i in data]   
    cars=pd.DataFrame()
    cars['id']=[i.split(',')[1] if len(i.split(',')[1])>3 else '' for i in data]
    cars['model']=[i.split(',')[3]  if i.split(',')[3]!='"0"' else '' for i in data]
    cars['model_pass']=[i.split(',')[5].split('-')[1].split('"')[0] if re.search('-',i.split(',')[5] ) else '' for i in data]
    cars['brand']=[i.split(',')[5].split('-')[0].split('"')[1] if re.search('-',i.split(',')[5] ) else '' for i in data]
    cars['makeId']=[i.split(',')[7] if len(i.split(','))>=7 else '' for i in data]
    cars['years']=[i[i.find('years')+8:-1].split(',') for i in data]
    cars=cars[cars['brand']!='']
    cars.reset_index(inplace=True)
    print('Shape of Cars Dataframe: {}'.format(cars.shape))

    cars_review =  pd.DataFrame({'id':np.repeat(cars['id'], cars['years'].str.len()),
                        'model':np.repeat(cars['model'], cars['years'].str.len()),
                        'model_pass':np.repeat(cars['model_pass'], cars['years'].str.len()),
                        'brand':np.repeat(cars['brand'], cars['years'].str.len()),
                        'makeId':np.repeat(cars['makeId'], cars['years'].str.len()),
                        'years': np.concatenate(cars['years'])})
    cars_review.drop_duplicates(inplace=True)

    cars_review.to_csv('data/cars_list_by_year.csv')    
    urllst2 = []

    for brand in cars['brand']:
        car_brand=cars[cars['brand']==brand]
        for model in car_brand['model_pass']:
            
            car_model=car_brand[car_brand['model_pass']==model]
            for yearlst in car_model['years']:
                for year in yearlst:
                        urllst2.append('https://www.cars.com/research/{}-{}-{}/trims'.format(brand, model, year))

    urllst2=list(set(urllst2))                    
    print('list of URLs {}'.format(len(urllst2)))                    
    ##obtain spec overview page url for each trim               

    
    trimurls=[]

    def get_trim_url(url):
        trimurl=[]
        models=[]
        try:
            data = request.urlopen(url)
            response=Selector(text=data.read())
            trim=response.xpath('.//script[@type="application/ld+json"]/text()').getall()
            for i in range(1, len(trim)):
                model=trim[i].split('"name":')[1].split('"model":')[0].split('"')[1]
                #print('Model{}: {} \n URL: {}'.format(i, model, url))
                models.append(model)
                trimurl_tmp=trim[i].split('@id":"')[1].split('"')[0]
                trimurl.append(trimurl_tmp)
        except:
            pass
        
    
        return trimurl
    
    
    for url in urllst2:
        trimurls.append(get_trim_url(url))
    
    trimurls=[i[:-11] for sub in trimurls for i in sub]                


    start_urls =list(set(trimurls))
    print('Start crawling')

    
    def parse(self, response):

        trim_ = response.xpath('//span[@class="specs-photo__desc"]/text()').extract_first()
        print('parse')
        trim = trim_[12:]
        year = trim_[0:4]
        make = trim_.split(' ')[1]
        price=  response.xpath('//span[@class="specs-price__value"]/text()').extract_first()
        seats = response.xpath('//td[@id="seats"]/text()').extract_first()
        doorCount =response.xpath('//td[@id="doorCount"]/text()').extract_first()
        engine =response.xpath('//td[@id="engine"]/text()').extract_first()
        drivetrain =response.xpath('//td[@id="drivetrain"]/text()').extract_first()
        mpg =response.xpath('//td[@id="mpg"]/text()').extract_first()
        warranty =response.xpath('//td[@id="warranty"]/text()').extract_first()
        
        item = CartrimsItem()
        item['trim'] = trim  #add these later after correct way to loop through urls is
        item['year'] = year
        item['make'] = make
        item['price'] = price
        item['seats'] = seats
        item['doorCount'] = doorCount
        item['engine'] = engine
        item['drivetrain'] = drivetrain
        item['mpg'] = mpg
        item['warranty'] = warranty
        yield item
