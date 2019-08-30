import datetime as dt
import pyodbc
from logger import logger, timeit
import pandas as pd
import asyncio

import helperModule as HM
db_cid=""

# @timeit
async def openConnection(client):
	global db_cid 
	loop = asyncio.get_event_loop()
	dataConfig = await HM.getConfig('config')
	dataConfig = dataConfig['database']
	db_host = dataConfig[client]['server']
	db_name = dataConfig[client]['db']
	db_user = dataConfig[client]['user']
	db_pass = dataConfig[client]['password']	
	db_cid = dataConfig[client]['cid']
	connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server='+db_host+';Database='+db_name+';UID='+db_user+';PWD='+db_pass+';'
	#logger("db connection starting...")
	return await loop.run_in_executor(None,pyodbc.connect,connection_string)
	#logger("connected to {db_name}".format(db_name=db_name))

async def closeConnection(conn):
	loop = asyncio.get_event_loop()
	await loop.run_in_executor(None,conn.close)
	#logger("DB connection closed")

async def getReportsByProjectList(reportString,c):
	#logger("Getting Report Info")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['report'].format(LASTUPATEDREPORTIDLIST=reportString)
	return await loop.run_in_executor(None,pd.read_sql,select,c)
	

async def getRisksByProjectList(projectString,c):
	#logger("Getting Risk Info")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['risk'].format(PROJECTIDLIST=projectString)
	return await loop.run_in_executor(None,pd.read_sql,select,c)
	

async def getProductsByProjectList(projectID,c):
	#logger("Getting Products")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	cond = queries["conditionsForSQL"]["GetProductByProject"].format(PROJECTIDLIST=projectID, CID=db_cid)
	queries = queries['queries']
	select = queries['product'].format(CONDITION=cond, CID=db_cid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getProductsByMappingID(mappingID,c):
	#logger("Getting Outputs")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	cond = queries["conditionsForSQL"]["GetProductByMappingID"].format(MAPPINGIDLIST=mappingID, CID=db_cid)
	queries = queries['queries']
	select = queries['product'].format(CONDITION=cond, CID=db_cid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getIssuesByProjectList(projectString,c):
	#logger("Getting Products")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['issue'].format(PROJECTIDLIST=projectString)
	return await loop.run_in_executor(None,pd.read_sql,select,c)
	

async def getCapabilitiesByProject(projectID,c):
	#logger("Getting Products")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['capability'].format(PROJECTID=projectID)
	return await loop.run_in_executor(None,pd.read_sql,select,c)
	

async def getDependentProjectsByID(c,projectCount,pid):
	#logger("getting project by id")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['dependentProjects'].format(CID=db_cid,LISTCOUNT=projectCount,PID=pid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)


async def getProjectByCondition(cond,c,projectCount,pid):
	#logger("getting project by condition")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['project'].format(CID=db_cid,CONDITION=cond,LISTCOUNT=projectCount,PID=pid)
	# print("\n",select,"\n")
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getProjectAndReportByCondition(cond,c,projectCount,pid):
	# logger("getting project by condition")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['projectAndReport'].format(CID=db_cid,CONDITION=cond,LISTCOUNT=projectCount,PID=pid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getDivisions(c):
	#logger("getting divisions")
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['divisions'].format(CID=db_cid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

#@timeit
async def getCount(conditionForProject,c,uid):
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	count = queries['count'].format(CID=db_cid,CONDITION=conditionForProject,USERID=uid)
	df = await loop.run_in_executor(None,pd.read_sql,count,c)
	df = df.astype(str)
	return df.to_dict('records')[0]

# @timeit
async def getStandardProjectInfo(conditionForProject,c,projectCount,pid):
	projectTable = await getProjectAndReportByCondition(conditionForProject,c,projectCount,pid)
	if(len(projectTable)<1):
		return 1,1
	return projectTable
	# pidlist = list(projectTable.projectid)

	# pidlist = list(projectTable.projectid)

	# reportids = list(projectTable[pd.notnull(projectTable['reportid'])].reportid)
	# if(len(reportids)<1):
	# 	reportTable = await HM.getEmptyDataFrame('report',pidlist)
	# else:
	# 	reportString = str(reportids)[1:-1]
	# 	reportTable = await getReportsByProjectList(reportString,c)

	# return projectTable,reportTable

async def GetUserIDByUserName(cond,c):
	loop = asyncio.get_event_loop()
	#logger("Getting user id by username")
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select =  queries['userid'].format(CID=db_cid,CONDITION=cond)
	#logger("\nUSERID QUERY ",select)
	df = await loop.run_in_executor(None,pd.read_sql,select,c)
	if(len(df.userid)>0):
		return df.userid[0]
	return 0

async def getBudgetHistory(c,projectid):
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['budgetHistory'].format(CID=db_cid,PROJECTID=projectid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getStatusHistory(c,projectid):
	loop = asyncio.get_event_loop()
	queries = await HM.getConfig('queries')
	queries = queries['queries']
	select = queries['statusHistory'].format(CID=db_cid,PROJECTID=projectid)
	return await loop.run_in_executor(None,pd.read_sql,select,c)

async def getFeedbackRow(dataObj):
	userid = dataObj['userInfo']['SDZUserID']
	username = dataObj['userInfo']['SDZUserName']
	userrole = dataObj['userInfo']['SDZRoleID']
	clientName = dataObj['userInfo']['Client']
	isSatisfied = dataObj['satisfied']
	query = dataObj['query']
	intent = dataObj['intent']
	priority = dataObj['priority']
	comment = dataObj['comment']	
	cid=dataObj['cid']
	return (clientName,cid, userid,userrole,username,isSatisfied,query,intent,priority,comment,1)

async def saveFeedbackToDB(dataObj):
	#logger("Saving feedback to db")
	loop = asyncio.get_event_loop()
	conn = await openConnection("botstate")
	c = conn.cursor()

	data_row = await getFeedbackRow(dataObj)
	placeHolder = "?,"*len(data_row)
	placeHolder = placeHolder[0:-1]	

	insert = "insert into UserFeedback(client_name, companyID, userID, userRoleID, userName, is_satisfied, query, intent, priority, UserComment,status) values({placeHolder})".format(placeHolder=placeHolder)
	
	await loop.run_in_executor(None,c.execute,insert,data_row)
	await loop.run_in_executor(None,conn.commit)
	#logger("Feedback added")
	await closeConnection(conn)

async def runQuery(query,c):
	loop = asyncio.get_event_loop()
	return await loop.run_in_executor(None,pd.read_sql,query,c)