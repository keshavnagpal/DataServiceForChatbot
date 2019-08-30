import pandas as pd
import json
import time
from logger import logger, timeit
import asyncio

import DB
import helperModule as HM
import responseBuilder as RB
import visualisations as VIS


'''
Response Mapping
0 : User Not Found
1 : Project Not Found

'''

async def GetPrograms(dataObj,c,conditions, intent):
    if dataObj["fullList"]==0:
        projectCount = await HM.getConfig('config')
        projectCount = projectCount["projectcount"]
    else:
        projectCount = ""
    cond = dataObj["condition"]
    return await getResponse(cond,c,intent,projectCount,-1, "is null")

async def GetBudgetHistory(dataObj,c,conditions,intent):
    df = await DB.getBudgetHistory(c,dataObj["projectid"])
    cond = conditions['GetProjectByID'].format(PROJECTIDLIST=str(dataObj["projectid"]))
    projectCount="top 1"
    project = await DB.getProjectByCondition(cond,c,projectCount,"is null")
    project = project.to_dict('records')
    return await VIS.getBudgetHistoryChart(project[0],df)

async def GetIssueByProject(dataObj,c,conditions,intent):
    cond = conditions['GetProjectByID'].format(PROJECTIDLIST=str(dataObj["projectid"]))
    projectCount="top 1"
    
    projectTable = await DB.getProjectByCondition(cond,c,projectCount,"is null")
    if(len(projectTable)<1):
        return 1
    pidlist = list(projectTable.projectid)
    projectString = str(pidlist)[1:-1]

    issueTable = await DB.getIssuesByProjectList(projectString,c)
    if(len(issueTable)<1):
        return 1
    return json.dumps(await RB.ResponseForIssue(issueTable,projectTable.iloc[0]))

async def GetRiskByProject(dataObj,c,conditions,intent):
    cond = conditions['GetProjectByID'].format(PROJECTIDLIST=str(dataObj["projectid"]))
    projectCount="top 1"
    
    projectTable = await DB.getProjectByCondition(cond,c,projectCount,"is null")
    if(len(projectTable)<1):
        return 1
    pidlist = list(projectTable.projectid)
    projectString = str(pidlist)[1:-1]

    riskTable = await DB.getRisksByProjectList(projectString,c)
    if(len(riskTable)<1):
        return 1
    return json.dumps(await RB.ResponseForRisk(riskTable,projectTable.iloc[0]))

async def GetProductByProject(dataObj,c,conditions,intent):
    cond = conditions['GetProjectByID'].format(PROJECTIDLIST=str(dataObj["projectid"]))
    projectCount="top 1"
    
    projectTable = await DB.getProjectByCondition(cond,c,projectCount,"is null")
    if(len(projectTable)<1):
        return 1
    pidlist = list(projectTable.projectid)
    projectString = str(pidlist)[1:-1]

    productTable = await DB.getProductsByProjectList(projectString,c)
    if(len(productTable)<1):
        return 1
    return json.dumps(await RB.ResponseForProduct(productTable,projectTable.iloc[0]))


async def GetBudgetFromReport(dataObj,c,conditions,intent):
    cond = conditions['GetProjectByID'].format(PROJECTIDLIST=str(dataObj["projectid"]))
    projectCount="top 1"
    project = await DB.getProjectByCondition(cond,c,projectCount,"is null")
    return await VIS.getBudgetFromReport(project)

async def GetProjectListByEntity(dataObj,c,conditions,intent):
    if dataObj["fullList"]==0:
        projectCount = await HM.getConfig('config')
        projectCount = projectCount["projectcount"]
    else:
        projectCount = ""
    cond = dataObj["condition"]
    if("p.stage" not in cond):
        cond+=" and (closureworkflowstatus is null or closureworkflowstatus!=4)"
    return await getResponse(cond,c,intent,projectCount,-1,"is null")

async def GetDivisions(dataObj,c,conditions,intent):
    return await getDivisionResponse(dataObj,c,intent)

async def GetDependencyByProject(dataObj,c,conditions,intent):
    # projectCount = await HM.getConfig('config')
    # projectCount = projectCount['projectcount'] if dataObj["fullList"]==0 else ""
    projectCount=""
    cond = dataObj["condition"]
    pid = " = " + dataObj["projectid"]
    return await getResponse(cond,c,intent,projectCount,-1,pid)

async def GetCount(dataObj,c,conditions,intent):
    cond = dataObj["condition"]
    if("p.stage" not in cond):
        cond+="and (closureworkflowstatus is null or closureworkflowstatus!=4)"
    metadata = await DB.getCount(cond,c,-1)
    if(metadata['count']=='0'):
        return "1"
    return json.dumps(metadata)

async def getResponse(cond,c,intent,projectCount,uid,pid):
    # projects,reports = await DB.getStandardProjectInfo(cond,c,projectCount,pid)
    projects = await DB.getStandardProjectInfo(cond,c,projectCount,pid)

    if(type(projects)==type(1)):
        if(projects==1):
            return "1"
    
    # metadata = DB.getCount(cond,c,uid)
    if(intent=="GetDependencyByProject"):
        projects = await DB.getDependentProjectsByID(c,projectCount,pid)
        # dependencyMappingIdString = str(list(projects.dependencymappingid))[1:-1]
        # products = DB.getProductsByMappingID(dependencyMappingIdString,c)
        response = await RB.ResponseBuilderForDependentProject(c,projects,intent)
        return json.dumps(response)

    if(intent=='GetPrograms'):
        projects = projects.sort_values(['projectinprogramcount'],ascending=[False])
    elif(intent=="GetProjectByRisk"):
        projects = projects.sort_values(['riskcount'],ascending=[False])
    elif(intent=="GetProjectByIssue"):
        projects = projects.sort_values(['issuecount'],ascending=[False])
        
    # Don't know from where these columns are coming, already removed from sql queries
    # try:
    #     if("reportid" in reports.columns or "programname" in reports.columns):
    #         reports = reports.drop("reportid",1)
    #         reports = reports.drop("programname",1)
    # except:
    #     pass
    # ProjectAndReport = pd.merge(left=projects, right=reports, on='projectid', how='left')

    response = await RB.ResponseBuilderForProject(c,projects,intent)
    
    return json.dumps(response)

async def getDivisionResponse(dataObj,conn,intent):
    divisions = await DB.getDivisions(conn)
    if(type(divisions)==type(1)):
        if(divisions==1):
            return "1"
    divisions = divisions.fillna("Not Available")
    metadata={}
    metadata["count"] = len(divisions.divisionid)
    if(dataObj["fullList"]==0 and metadata["count"]>10):
        divisions = divisions.head(10)
    response = {"DivisionList": divisions.to_dict('records'), "metadata":metadata}
    return json.dumps(response)