from logger import logger, timeit
import asyncio
import functools
import visualisations as VIS
import pandas as pd
import helperModule as HM
import DB

async def ResponseBuilderForProject(c,projects,intent):
	ProjectList = []
	projects.start_date = projects.start_date.apply(HM.getDateString)
	projects.end_date = projects.end_date.apply(HM.getDateString)
	projects.actual_start_date = projects.actual_start_date.apply(HM.getDateString)
	projects.actual_end_date = projects.actual_end_date.apply(HM.getDateString)
	projects.forecast_start_date = projects.forecast_start_date.apply(HM.getDateString)
	projects.forecast_end_date = projects.forecast_end_date.apply(HM.getDateString)
	projects.intervalstartdate = projects.intervalstartdate.apply(HM.getDateString)
	projects.intervalenddate = projects.intervalenddate.apply(HM.getDateString)

	projects.reportduedate = projects.reportduedate.apply(HM.getDateString)

	
	projects = projects.fillna("Not Available")

	projects.budget = projects.budget.apply(str)
	projects.actualbudget = projects.actualbudget.apply(str)
	projects.ytdbudget = projects.ytdbudget.apply(str)

	projects.financestatussummary = projects.financestatussummary.apply(HM.strip_tags)
	projects.issuestatussummary = projects.issuestatussummary.apply(HM.strip_tags)
	projects.overallstatussummary = projects.overallstatussummary.apply(HM.strip_tags)
	projects.resourcestatussummary = projects.resourcestatussummary.apply(HM.strip_tags)
	projects.riskstatussummary = projects.riskstatussummary.apply(HM.strip_tags)
	projects.schedulestatussummary = projects.schedulestatussummary.apply(HM.strip_tags)
	projects.scopestatussummary = projects.scopestatussummary.apply(HM.strip_tags)
	
	projects.problemstatement = projects.problemstatement.apply(HM.strip_tags)
	projects.scopedetail = projects.scopedetail.apply(HM.strip_tags)
	projects.driverforchange = projects.driverforchange.apply(HM.strip_tags)
	projects.previousreportingachievements = projects.previousreportingachievements.apply(HM.strip_tags)
	projects.nextactivityplanned = projects.nextactivityplanned.apply(HM.strip_tags)

	projects = projects.to_dict('records')

	for project in projects:
		Basic = {
				'name':project['projectname'],
				'description':project['description'],
				'problemStatement':project['problemstatement'],
				'scopeDetail':project['scopedetail'],
				'driverForChange':project['driverforchange'],
				'previousReportingAchievements':project['previousreportingachievements'],
				'nextActivityPlanned':project['nextactivityplanned'],
				'stage':project['stage'],
				'stageNumber':project['stagenumber'],
				'closureWorkflowStatus':project['closureworkflowstatus'],
				'programName':project['programname'],				
				'totalFTE':project['totalftecount'],
				'projectBackground':project['projectbackground'],
				'branch':project['branch'],
				'division':project['division'],
				'section':project['section'],
				'tier':project['tier'],
				'nextMilestone':project['nextmilestone'],
				'nextMilestoneDueDate': project['nextmilestoneduedate'],			
		}
		User = {
				'projectManager':project['projectmanager'],
				'projectPMO':project['projectpmo'],
				'projectOwner':project['projectowner'],
				'programManager':project['programmanagername'],
				'benefitsManager':project['benefitsmanager'],
				'projectDirector':project['projectdirector'],

				'projectManagerEmail':project['projectmanageremail'],
				'projectPMOEmail':project['projectpmoemail'],
				'projectOwnerEmail':project['projectowneremail'],
				'benefitsManagerEmail':project['benefitsmanageremail'],
				'projectDirectorEmail':project['projectdirectoremail'],

				'manager_id':project['manager_id'],
				'owner_id':project['owner_id'],
				'PMO_id': project['pmoresponsibleid'],
				'benefitsManager_id': project['benefitsmanagerid'],
				'projectDirector_id': project['projectdirector']
		}
		Budget = {
				'baseline':project['budget'],
				'actualBudget':project['actualbudget'],
				'ytdBudget':project['ytdbudget'],
		}
		Schedule = {
				'startDate':project['start_date'],
				'endDate':project['end_date'],
				'actualStartDate':project['actual_start_date'],
				'actualEndDate':project['actual_end_date'],
				'forecaseStartDate':project['forecast_start_date'],
				'forecastEndDate':project['forecast_end_date'],
				'intervalStartDate':project['intervalstartdate'],
				'intervalEndDate':project['intervalenddate'],
				'reportDueDate':project['reportduedate'],
				'dueDaysForReport':project['duedaysforreport']
		}
		Status = {
				'overallStatus':project['overallstatus'],
				'overallStatusSummary':project['overallstatussummary'],
				'financeStatus':project['financestatus'],
				'financeStatusSummary':project['financestatussummary'],
				'scheduleStatus':project['schedulestatus'],
				'scheduleStatusSummary':project['schedulestatussummary'],
				'scopeStatus':project['scopestatus'],
				'scopeStatusSummary':project['scopestatussummary'],
				'resourceStatus':project['resourcestatus'],
				'resourceStatusSummary':project['resourcestatussummary'],
				'riskStatus':project['riskstatus'],
				'riskStatusSummary':project['riskstatussummary'],
				'issueStatus':project['issuestatus'],
				'issueStatusSummary':project['issuestatussummary'],
				'reportStatus':project['reportstatus'],
				'projectStatus':project['projectstatus']
		}
		
		project = {
			'id':project['projectid'],
			'programid':project['projectboardid'],
			'Basic':Basic,
			'User':User,
			'Status':Status,
			'Budget':Budget,
			'Schedule':Schedule,
			'dependentProjectCount':project['dependentprojectcount'],
			'projectinProgramCount':project['projectinprogramcount'],
			'RiskCount':project['riskcount'],'HighRisks':project['highriskcount'],'LowRisks':project['lowriskcount'],'MediumRisks':project['mediumriskcount'],'ExtremeRisks':project['extremeriskcount'],
			'IssueCount':project['issuecount'],
			'ProductCount':project['productcount'], 'CompletedProductCount':project['completedproductcount']
			}
		ProjectList.append(project)
	statusChart = ""
	stageChart = ""
	# if(intent=="GetProjectListByEntity"):
	#	projectDF.fillna(0)
	# 	statusChart = await VIS.getProjectsGroupedByStatusChartBar(projectDF)
	# 	stageChart = await VIS.getProjectsGroupedByStageChartBar(projectDF)


	# metadata["ProjectIdWithMaxRisks"]=ProjectIdWithMaxRisks
	fullResp = {"ProjectList": ProjectList,"charts":{"statusChart":statusChart,"stageChart":stageChart}}

	return fullResp

async def ResponseForIssue(issues,project):
	issues.duedate = issues.duedate.apply(HM.getDateString)
	Issues=None
	notEmptyIssue = True
	if(len(issues[issues.projectid==project['projectid']])==1):
		if(int((issues[issues.projectid==project['projectid']]).issueregisterid)==0):
			notEmptyIssue=False
			Issues = pd.DataFrame(columns=list(issues))
		
	if(notEmptyIssue):
		Issues = issues[issues.projectid==project['projectid']]
	Issues = Issues.fillna("Not Available")
	
	return Issues.to_dict('records')

async def ResponseForRisk(risks,project):
	risks.duedate = risks.duedate.apply(HM.getDateString)
	Risks=None
	notEmptyRisk = True
	if(len(risks[risks.projectid==project['projectid']])==1):
		if(int((risks[risks.projectid==project['projectid']]).riskregisterid)==0):
			notEmptyRisk=False
			Risks = pd.DataFrame(columns=list(risks))
		
	if(notEmptyRisk):
		Risks = risks[risks.projectid==project['projectid']]
	Risks = Risks.fillna("Not Available")

	return Risks.to_dict('records')

async def ResponseForProduct(products,project):
	products.start_date = products.start_date.apply(HM.getDateString)
	products.end_date = products.end_date.apply(HM.getDateString)

	Products = products[products.projectid==project['projectid']]
	Products = Products.fillna("Not Available")

	return Products.to_dict('records')

async def ResponseBuilderForDependentProject(c,projects,intent):
	projects.start_date = projects.start_date.apply(HM.getDateString)
	projects.end_date = projects.end_date.apply(HM.getDateString)
	
	projects=projects.fillna("Not Available")

	projects.budget = projects.budget.apply(str)
	projects.actualbudget = projects.actualbudget.apply(str)

	# products.start_date = products.start_date.apply(HM.getDateString)
	# products.end_date = products.end_date.apply(HM.getDateString)

	return {'ProjectList': projects.to_dict('records')}
