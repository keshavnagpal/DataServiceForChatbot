import json
import pandas as pd
from html.parser import HTMLParser
import datetime as dt
from logger import timeit
import asyncio
import functools

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
	s = MLStripper()
	if(html==None or type(html)==type(1)):
		return "Not Available"
	else:
		s.feed(html)
		return s.get_data()

async def getConfig(file):
	loop = asyncio.get_event_loop()
	with open('%s.json' % file) as f:
		data = await loop.run_in_executor(None,json.load,f)
	return data

def writeConfig(file,data):
    with open('%s.json' % file, 'w') as f:
        json.dump(data, f,indent=4, sort_keys=True)

# def addColumnHeaders(df,c):
# 	try:
# 		df.columns = [col[0] for col in c.description]
# 	except Exception as ex:
# 		print("Exception f(addColumnHeaders): ",str(ex))
# 	return df

# @timeit
# def ConvertToStr(df):
# 	for key in df:
# 		df[key].apply(str)
# 	return df

async def getEmptyDataFrame(table,pidlist):
	lenOfProjects = len(pidlist)
	NA=["Not Available"]*lenOfProjects
	if(table=='report'):
		data = {
			'projectid':pidlist,
			'reportid':[0]*lenOfProjects,
			'intervalstartdate':NA,
			'intervalenddate':NA,
			'projectmanagername':NA, 
			'projectownername':NA, 
			'projectpmoname':NA,
			'programname':NA, 
			'programmanagername':NA, 
			'nextactivityplanned':NA, 
			'previousreportingachievements':NA, 
			'overallstatus':NA, 
			'overallstatussummary':NA, 
			'financestatus':NA, 
			'financestatussummary':NA, 
			'schedulestatus':NA, 
			'schedulestatussummary':NA, 
			'scopestatus':NA, 
			'scopestatussummary':NA, 
			'resourcestatus':NA,
			'resourcestatussummary':NA, 
			'riskstatus':NA, 
			'riskstatussummary':NA, 
			'issuestatus':NA, 
			'issuestatussummary':NA, 
			'reportstatus':NA,
			'reportduedate':NA, 
			'duedaysforreport':NA
		}
		return pd.DataFrame(data=data)

		
	elif(table=='risks'):
		data = {
			'projectid':pidlist,
			'riskregisterid':[0]*lenOfProjects,
			'risk':NA,
			'treatment':NA,
			'duedate':NA,
			'riskowner':NA,
			'actualconsequence':NA,
			'actuallevel':NA,
			'actuallikelihood':NA,
			'residualconsequence':NA,
			'residuallevel':NA,
			'residuallikelihood':NA
		}
		return pd.DataFrame(data=data)
	
	elif(table=='issue'):
		data = {
			'projectid':pidlist,
			'issueregisterid':[0]*lenOfProjects,
			'issuename':NA,
			'duedate':NA,
			'priority':NA,
			'action':NA,
			'issuetype':NA
		}
		return pd.DataFrame(data=data)


	elif(table=='product'):
		data = {
			'projectid':pidlist,
			'productid':[0]*lenOfProjects,
			'productname':NA,
			'producttype':NA,
			'start_date':NA,
			'end_date':NA,
			'budgetcapex':NA,
			'budgetopex':NA,
			'percentage':NA,
			'capabilitylinked':NA
		}
		return pd.DataFrame(data=data)
	
	return 0

def getDateString(dateValue):
	try:
		return dateValue.strftime("%d %b %Y")
	except:
		# if(dateValue==None):
		return "Not Available"
		# return str(dateValue)

def ToKMB(num):
	if(num == None):
		return num
	
	elif(num=='Not Available'):
		return num

	elif (float(num) > 999999999 or float(num) < -999999999):
		return "${0:.2f}B".format((float(num)/1000000000))
	
	elif(float(num) > 999999 or float(num) < -999999):
		return "${0:.2f}M".format((float(num)/1000000))
	
	elif(float(num) > 999 or float(num) < -999):
		return "${0:.2f}K".format((float(num)/1000))

	else:
		return "$%s" % str(num)