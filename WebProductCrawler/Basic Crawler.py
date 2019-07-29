#!/usr/bin/env python
# coding: utf-8

import os, sys
module_dir = os.path.abspath(__file__,)
if module_dir not in sys.path:
    sys.path.append(module_dir)
from bs4 import BeautifulSoup as bs

from urllib.parse import urlparse

from PageDump import PageDump


def html_to_bs(f):
    try:
        with open(f,'r',encoding="utf8") as f:
            src = f.read()
            return bs(src, "lxml").body
    except:
        print('No such file')
        quit()


#init info and user vars

url = input('Website URL = ')

src = PageDump().GetSRC(url)
src = bs(src,'lxml').body

sample = input('Product URL = ')


#get all the urls

class BasicCrawl:
    def __init__(self,sample,opt=''):
        self.sample = sample
        self.opt  = opt
        self.src = src

        if self.opt == 'img':
            self.all_urls_block = src.find_all('img')
        else:
            self.all_urls_block = src.find_all('a')


    def get_target_url_block(self,src,sample):
        #Confirming the existing of the Sample and returning the result[]
        sample_block_list = src.find_all('a',href=sample)
        parsed = urlparse(sample)
        if len(sample_block_list) == 0 and parsed[2] == sample:
                print('We can''find the Product url: {url}'.format(url=sample))
                quit()
                
        elif len(sample_block_list) == 0:
                sample = urlparse(sample)[2]
                return self.get_target_url_block(src,sample)
        #Duplicated result
        if len(sample_block_list) > 1:
            print('Warning : the page contains duplicated url so the result can differ ')
        #returning the first element for testing purpose
        #todo: run through next link if the user want to
        return sample_block_list[0]



    def get_available_attrs(self,target_url_block,opt=''):
        if opt=='key':
            #return list of the available attr names []
            return list(target_url_block.attrs.keys())
        elif opt=='':
            #return list of the available attr names,values [()]
            attrs_dict = target_url_block.attrs
            return [(k,attrs_dict[k]) for k in attrs_dict ]
        else:
            raise ValueError('invalid option value (enter "key" to show available keys or leave it).')
    # print(get_available_attrs(target_url_block,''))
     
    #get all the urls (attr related)
    def filter_by_attr(self,url_list,target_url_block,wanted_attr_dict={}):
        #grap valid urls
        #pop duplicated
        #target_attrs: type = dict_keys
        target_attrs = target_url_block.attrs
        result = set()
        for url in url_list:
            #nested loop to check attrs value match compared to the dicts (it shouldn't be done like that but whatever)
            attr_value_match = True
            if wanted_attr_dict != {} :
                for key in wanted_attr_dict :
                    try:
                        if  wanted_attr_dict[key] != url.attrs[key]:
                            attr_value_match = False
                    except:
                        attr_value_match = False
                        pass
    #                 print('check {key} in {url_attrs} = {check}'.format(key=key,url_attrs=url.attrs,check=key in url.attrs))
    #                 if not(key in url.attrs.keys()):
    #                     attr_value_match = False
    #                     break
    #                 elif wanted_attr_dict[key] != target_attrs[key]:
    #                     attr_value_match = False
    #                     break
    #                 else:
    #                     continue
            if url.attrs.keys() == target_attrs.keys() and attr_value_match:
                result.add(url.get('href'))
        
        return result

    def main(self,wanted_attr_dict={}):
        target_url_block = self.get_target_url_block(self.src,self.sample)
        filtered_urls = self.filter_by_attr(self.all_urls_block,target_url_block,wanted_attr_dict)
        for url in filtered_urls:
            print(url)

        return filtered_urls



#Part 2

#search the most repeatable attr value
def suggested_attrs(target_url_block):
    attr_value_count = {}
    for attr in target_url_block.attrs:
        attr_value  =target_url_block.attrs[attr]
        if isinstance(attr_value,list):
            attr_value = ' '.join(attr_value)
        attr_value_count[attr] = len(src.find_all('a',attrs={attr:attr_value}))
    #print(attr_value_count)
    #sorted_d = sorted([(v,k) for k,v in attr_value_count.items()], reverse=True)

    #get the max value of the repeated attr 
    max_freq = max(attr_value_count.values())

    #suggested attrs with the max value
    sugg_attrs = [attr for attr in attr_value_count if attr_value_count[attr]==max_freq]
    return sugg_attrs

#Advanced mod: user select unique attributes after the automated failure
def get_wanted_attrs_values(target_url_block):
    #todo: extension add recommended key to select
    # recommended key = its value repeated avg time comapred to the rest
    target_attrs = target_url_block.attrs
    adv_attr_dict = {}

    sugg_attrs = suggested_attrs(target_url_block)
    print('available attrs:')
    for attr in BasicCrawl(sample).get_available_attrs(target_url_block,'key'):
        #if href is selected the result will be only the sample url
        if attr != 'href':
            print('{attr}{sugg}'.format(attr=attr,sugg='*' if attr in sugg_attrs else ''))
        
    
    wanted_attr = input('select wanted attrs (split by , ) = ')
    wanted_attr = wanted_attr.replace(' ','').split(',')
    
    if len(wanted_attr[0]) == 0 or len(wanted_attr) == 0 :
        print('you didn''t enter a filter attrs this will execute the general case')
        return {}
    else:
        try:
            for key in wanted_attr:
                adv_attr_dict[key] = target_attrs[key]
        except:
            print('invalid attr / not found try again (this will use general case)')
            return {}

    return adv_attr_dict

#Simlple function to run the advanced mode


#filter urls by selected attrs values
def save_result(url,filtered_urls):
    fname = '{website}_result.txt'.format(website=urlparse(url)[1])
    with open(fname,'w+') as f:
        for url in (filtered_urls):
            f.write('{url} \n'.format(url=url))
        f.close()
    print('{length} url found \n you can see the results in \n {path}'
          .format(length=len(filtered_urls),path=os.getcwd()+'\\'+fname))


def advanced_mode():
    target_url_block = BasicCrawl(sample).get_target_url_block(src,sample)
    wanted_attr_dict = get_wanted_attrs_values(target_url_block)
    filtered_urls = BasicCrawl(sample).main(wanted_attr_dict)
    return filtered_urls

filtered_urls = BasicCrawl(sample).main()
print('\n \n \n what do you think?')
print('1 to run advanced')
print('2 to quit')
opt = input(' =  ')

if opt == '1':
    clear = lambda: os.system('cls')
    try:
        clear()
    except:
        pass
    advanced_mode()
    save_result(url,filtered_urls)
    programPause = input("Press the <ENTER> key to exit...")

else:
    save_result(url,filtered_urls)
    quit()

#todo add filter by image 
#choices = [('Filter urls by attributes (advanced)',advanced_mode()),
#           'Add product image url',
#           'Save',
#           'Discard
