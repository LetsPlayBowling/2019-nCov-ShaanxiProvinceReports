# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 19:59:14 2020

ShaanXi（陕西） Province reported 2019-nCoV Cases

Information source: 
Health Commission of Shaanxi Province, official website:
http://sxwjw.shaanxi.gov.cn/col/col9/index.html


@author: RAY
"""

import requests
import re
import datetime
import os

def getTodayDate():    
    # get date as a string, like "20200203"
    today = datetime.date.today() 
    if today.month < 10:
        strTodayMonth = '0'+ str(today.month)
    else:
        strTodayMonth = str(today.month)   
    if today.day < 10:
        strTodayDay = '0'+ str(today.day)
    else:
        strTodayDay = str(today.day)
    strTodayDate = str(today.year) + strTodayMonth + strTodayDay
    return strTodayDate

def getTodayNewsTitles():
    # get webpage raw content from the "卫健要闻" in the website
    # including news titles and their urls
    print(">>>> Requesting the website...")
    url = 'http://sxwjw.shaanxi.gov.cn/col/col9/index.html' # '卫健要闻' address
    print(">>>> Requesting the website: " + url + " ...")
    try:
        res = requests.get(url)
    except IOError:
        print(">>>> Connection Error ")
    else:
        res.encoding = 'utf-8'
        MainPageTxt = re.search('(<recordset>\s+)(.*)(\s+</recordset>)',
                            res.text, re.S).group(2)
        strTodayDate = getTodayDate()
    
        # save this page valid content in a record text file 
        file = open('RawPage_'+ strTodayDate + '.txt','w')
        file.write(MainPageTxt)
        file.close()
    
def getRelatedNewsUrls():
    strTodayDate = getTodayDate()
    file = open('RawPage_'+ strTodayDate + '.txt','r+');
    MainPageTxt = file.read()
    MainPageItems = re.findall(r'<record>(.*?)</record>',
                            MainPageTxt,re.S)
    keyWord_1 = '陕西新增'
    keyWord_2 = '我省确认'
    rootUrl = "http://sxwjw.shaanxi.gov.cn"
    file_new = open('卫健要闻_items_'+ strTodayDate + '.txt','w')
    for tempStr in MainPageItems:
        if (keyWord_1 in tempStr) | (keyWord_2 in tempStr):
            tempDate = re.search('(</a><span>)(.*)(</span></li>)',
                            tempStr, re.I).group(2)
            tempTitle = re.search('(target="_blank">)(.*)(</a><span>)',
                            tempStr, re.I).group(2)
            tempUrl = rootUrl + re.search('(<a href=")(.*)(" target="_blank">)',
                            tempStr, re.I).group(2)
            file_new.write(tempDate+'\t' +tempTitle + '\t\t\t' + tempUrl + '\n')        
    file_new.close()
    file.close()
    os.remove('RawPage_'+ strTodayDate + '.txt')
    
def getTodaysReport():
    # (1) get todays report url 
    strTodayDate = getTodayDate()
    file = open('卫健要闻_items_'+ strTodayDate + '.txt','r')
    lines = file.readlines()
    firstLine = lines[0] # the first line is for today
    temp_url = re.search(r'http.*html',firstLine)
    today_page_url = temp_url[0]
    file.close()
    
    # (2) record the web page 
    print(">>>> Requesting the website: " + today_page_url + '...')
    try:
        res = requests.get(today_page_url)    
    except IOError:
        print(">>>> Connection Error ")
    else:
        res.encoding = 'utf-8'
        ReportPageTxt = re.search(r'(信息内容)(.*)(信息内容)',
                           res.text,re.S).group(2)
        ReportPageTxt = re.sub("<.*?>", "", ReportPageTxt)
        ReportPageTxt = re.sub("(begin)", "", ReportPageTxt)
        ReportPageTxt = re.sub("[\[\]\<\>\-\!\$]", "", ReportPageTxt)
        ReportPageTxt = re.sub("(。患者)", "。\n患者", ReportPageTxt)
        # print(ReportPageTxt)
        file = open('Report_content_'+ strTodayDate + '.txt','w')
        file.write(ReportPageTxt)
        file.close()
        
def getHistoryReports():
    '''
    since this code is written in 20200203, 
    the history reports need to be collected 
    ''' 
    strTodayDate = getTodayDate()
    file = open('卫健要闻_items_'+ strTodayDate + '.txt','r')
    lines = file.readlines()
    for line in lines:
        temp_date = line[0:4] + line[5:7] + line[8:10]
        temp_url = re.search(r'http.*html',line)
        temp_page_url = temp_url[0]
    
        print(">>>> Requesting the website: " + temp_page_url + '...')
    
        try:
            res = requests.get(temp_page_url)    
        except IOError:
                print(">>>> Connection Error ")
        else:
            res.encoding = 'utf-8'
            ReportPageTxt = re.search(r'(信息内容)(.*)(信息内容)',
                                      res.text,re.S).group(2)
            ReportPageTxt = re.sub("<.*?>", "", ReportPageTxt)
            ReportPageTxt = re.sub("(begin)", "", ReportPageTxt)
            ReportPageTxt = re.sub("[\[\]\<\>\-\!\$]", "", ReportPageTxt)
            ReportPageTxt = re.sub("(。患者)", "。\n患者", ReportPageTxt)
            # print(ReportPageTxt)
            file_new = open('Report_content_'+ temp_date + '.txt','w')
            file_new.write(ReportPageTxt)
            file_new.close()
       
    file.close()

def sortDaysCasesInfo(report_file_name): 
    # TODO: unfinished code: 
    # 陕西省公布的病例，流行病调查内容相对详细，
    # 可进一步使用多维特征来概括每个病例的流行病特征
    '''
    Note:
    The input parameter ’report_file_name‘ is a string corresponding to a txt file.
    In that file, every patient's description is in a seperated paragraph.
    '''
    file = open(report_file_name,'r')
    content = file.readlines()
    for prgrf in content:
        if prgrf[0:2] == '患者':
            print(prgrf)
            # print(prgrf)
            # (1) patient id number = date_number
            temp1 = re.findall(r"\d\d*",report_file_name)
            temp2 = re.findall(r"\d\d*",prgrf)
            patient_num = temp1[0] + '_' + temp2[0] 
            print(patient_num)
            # (2) patient gender 
            temp = prgrf[0:15] # 15 is a important limitation, it needs to be changed once incidence becomes very high
            if '男' in temp:
                patient_sex = 'male'
            elif '女' in temp:  
                patient_sex = 'female'
            print(patient_sex)    
            # (3) patient age 
            temp = re.findall(r"\d+\.?\d*",prgrf)
            patient_age = temp[1]
            print(patient_age)
            # (4) patient 籍贯/居住地
            JiGuan = re.search('岁，(.*?)人[\，\。]',prgrf,re.S)
            if not JiGuan is None:
                JiGuan = re.search('岁，(.*?)人[\，\。]',prgrf,re.S).group(1)
                if '，' in JiGuan: # 取后半句
                    JiGuan = re.sub('(.*?)，','',JiGuan)
                JiGuan = '籍贯，' + JiGuan
                print(JiGuan)
            elif not re.search('现居(.*?)[\，\。]',prgrf,re.S) is None:
                JiGuan = '现居，'+ re.search('现居(.*?)[\，\。]',prgrf,re.S).group(1)
                print(JiGuan)
            else:
                print('籍贯/居住地 unknown')
            # (5) 长期居住地
            try:
                live_in = re.search('长期在(.*?)居住',prgrf,re.S).group(1)  
            except:
                 print("长期居住地: not mentioned")
            else:
                print('长期居住地： ' + live_in)    
            # (6) 旅行史
            try:
                trip_time = re.search('。(.*?)[从]',prgrf,re.S).group(1)
                trip_from = re.search('从(.*?)到',prgrf,re.S).group(1)
                trip_to = re.search('到(.*?)，',prgrf,re.S).group(1)    
            except:
                 print("旅行史：unknown")
            else:
                print('旅行史：' + '\t' + trip_time + ' 从 ' + trip_from
                      + ' 到 ' + trip_to)
           # (7) 症状时间
            try:
                sick_time = re.search('[。](.*?)[\出症状\出现症状]',prgrf,re.S).group(1) 
                if '，' in sick_time:
                    #print(sick_time)
                    sick_time = re.search('(.*?)[月]',sick_time,re.S).group(1) + '月' + re.search('[。，](.*?)[日]',sick_time,re.S).group(1) + '日'     
                elif '。' in sick_time:
                    sick_time = re.search('[。](.*?日)',sick_time,re.S).group(2)
                    if '。' in sick_time:
                        print(prgrf)
                        sick_time = re.search('(.*?)[月]',sick_time,re.S).group(2) + '月' + re.search('[。](.*?日)',sick_time,re.S).group(1) + '日'     
            except:
                print("出现症状时间：unknown")
            else:
                print('出现症状时间：' + '\t' + sick_time)
        
        
        print('\n')   
            
        
    file.close()
    

    
def main():
    
    # (1) get news titles in the news release page (’卫健要闻‘)
    getTodayNewsTitles()
    
    # (2) extract Url links of 2019-nCoV case related news
    getRelatedNewsUrls()
    
    # OPTIONAL： get history reports (for the first-time run) 
    getHistoryReports()
    
    # (3) get today's report 
    getTodaysReport()
    
    

if __name__ == "__main__":
    main()