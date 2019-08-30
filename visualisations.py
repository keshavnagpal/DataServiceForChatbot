import pygal
from pygal.style import Style
import datetime as dt
import helperModule as HM
from logger import logger,timeit
import math
import functools
import asyncio

percent_formatter = lambda x: '{:.0f}%'.format(x)
money_formatter = lambda y: "${:,.0f}".format(y)
date_formatter = lambda dt: dt.strftime("%b'%y")

#@timeit
async def getBudgetHistoryChart(project,df):
    if(len(df)>0):
        if((df.actual>1).any() or (df.planned>1).any() or (df.forecast>1).any()):
            return await budgetLineChart(project,df)
    return await budgetKPIChart(project,df)
    

async def budgetLineChart(project,df):
    cstyle = Style(
        major_label_font_size = 22,
        label_font_size = 22,
        legend_font_size = 23,
        value_font_size=22,
        title_font_size = 22,
        colors=('#DE8F6E','#00AABB','#0000FF'),
        font_family='googlefont: Helvetica'
    )
    dateline_chart = pygal.DateLine(
        width=650,height=600,
        legend_at_bottom=True,legend_at_bottom_columns=3,truncate_label=-1,
        x_labels_major_count=3,show_minor_x_labels=False, x_label_rotation=0,
        margin_right=50,
        x_value_formatter = date_formatter,
        value_formatter = HM.ToKMB, 
        no_data_text='Not Available',
        js=[],
        style=cstyle
    )    
    
    planned = []
    forecast = []
    actual = []
    budgetRows = df.to_dict('records')    
    today = dt.datetime.now().date()
    forecastFlag=False
    budgetDateDate=[]
    i=0
    for budgetRow in budgetRows:
        if not forecastFlag:
            if(budgetRow['budgetdate']<today):
                forecastFlag = True

        budgetDateDate.append(budgetRow['budgetdate'])
        if(i==0):
            actual.append((budgetRow['budgetdate'],budgetRow['actual']))
            planned.append((budgetRow['budgetdate'],budgetRow['planned']))
            forecast.append((budgetRow['budgetdate'],budgetRow['actual']))           
        else:
            actual.append((budgetRow['budgetdate'],budgetRow['actual']+actual[i-1][1]))
            planned.append((budgetRow['budgetdate'],budgetRow['planned']+planned[i-1][1]))

            if(budgetRow['budgetdate']<today):
                forecast.append((budgetRow['budgetdate'],budgetRow['actual']+forecast[i-1][1]))
            else:
                forecast.append((budgetRow['budgetdate'],budgetRow['forecast']+forecast[i-1][1]))
        i+=1

    dateline_chart.x_labels = budgetDateDate
    if(forecastFlag):
        dateline_chart.add(title='Forecast',values=forecast)
        # dateline_chart.add('Forecast',forecast)
    dateline_chart.add(title='Actual',values=actual)
    dateline_chart.add(title='Planned',values=planned)
    # dateline_chart.add('Actual',actual)
    # dateline_chart.add('Planned',planned)

    return  dateline_chart.render_data_uri()

async def budgetKPIChart(project,df):
    # perc=0
    # diff=0
    color='#B0BEC5'
    if (project['budget']!=None):
        if(project['budget']!="Not Available" and project['actualbudget']!="Not Available" and float(project['budget'])!=0.0):
            # perc = (float(project['actualbudget'])/float(project['budget']))* 100
            # diff = abs(float(project['actualbudget']) - float(project['budget']))
            if(float(project['budget'])<float(project['actualbudget'])):
                color = '#FD625E'
            else:
                color = '#01B8AA'
    
    gauge = pygal.SolidGauge(
        width=250, height=250,
        half_pie=True, inner_radius=0.50,        
        legend_at_bottom=True,
        truncate_label=-1,
         truncate_legend=-1,
        human_readable=True,
        print_values=False,
        no_data_text='',
        js=[],
        value_formatter = HM.ToKMB,
        style=pygal.style.styles['default'](
            font_family='googlefont: Helvetica',
            label_font_size = 15,
            major_label_font_size = 15,
            legend_font_size = 10,
            colors=(color,color,color,color,color,color),
            value_font_size=8,
            value_label_font_size=8,        
            title_font_size=10
            )
    )
    acutalB = HM.ToKMB(project['actualbudget'])
    baselineB = HM.ToKMB(project['budget'])
    gauge.title="Monthly budget is not available"
    gauge.add(
        'Actual: {actual}, Baseline: {budget}'.format(budget=acutalB,actual=baselineB), 
        [{'value': project['actualbudget'],'max_value': project['budget']}]
    )
    return gauge.render_data_uri()
    

#@timeit
async def getProjectsGroupedByStageChartBar(projectsDF):
    totalProjects = len(projectsDF)
    if(totalProjects>0):
        cstyle = Style(
            major_label_font_size = 22,
            label_font_size = 22,
            value_font_size=25,
            font_family='googlefont: Helvetica',
            title_font_size = 22,
            colors=('#80c6f9','#cccccc')
        )
        bar_chart = pygal.Bar(
            width=600, height=500,
            show_legend=False,legend_at_bottom=True,include_y_axis=False,show_y_labels=False,
            truncate_label=-1,print_values_position='top',no_data_text='Not Available',           
            print_values=True,
            js=[],
            style=cstyle
        )
        concept = len(projectsDF[projectsDF.stagenumber==1])
        plan = len(projectsDF[projectsDF.stagenumber==2])
        delivery = len(projectsDF[projectsDF.stagenumber==3])
        closed = len(projectsDF[projectsDF.stagenumber==4])
        notAssigned = totalProjects-(concept+plan+delivery+closed)

        bar_chart.y_labels_major=list(range(totalProjects))

        bar_chart.x_labels = ["Concept","Plannning","Delivery","Closed","NA"]
        bar_chart.add('Projects By Stage',[concept,plan,delivery,closed,notAssigned])

        return bar_chart.render_data_uri()   

    return 0

#@timeit
async def getBudgetFromReport(this_project):
    cstyle = Style(
        value_font_size=28,
        title_font_size = 22,
        label_font_size = 30,
        legend_font_size = 25,
        major_label_font_size = 25,
        font_family='googlefont: Helvetica',
        colors=('#80c6f9','#cccccc')
    )
    bar_chart = pygal.Bar(
        width=550, height=600,
        show_legend=False,
        show_y_labels=False,include_y_axis=False,       
        print_values=True,print_values_position='top',no_data_text='Not Available',
        value_formatter = HM.ToKMB,
        js=[],
        # rounded_bars=20,
        style=cstyle
    )

    # this_project = project[project.projectid==pid]
    bar_chart.title = ""

    Baseline = this_project.budget.astype(float).item()
    Forecast = this_project.ytdbudget.astype(float).item()
    Actual = this_project.actualbudget.astype(float).item()

    if math.isnan(Baseline) :
        Baseline=0.0
    if math.isnan(Forecast) :
        Forecast=0.0
    if math.isnan(Actual) :
        Actual=0.0

    bar_chart.x_labels = ["Baseline","Forecast","Actual"]
    bar_chart.add('Budgets',[Baseline,Forecast,Actual])

    return bar_chart.render_data_uri()

#@timeit
async def getProjectsGroupedByStatusChartBar(projectsDF):
    totalProjects = len(projectsDF)
    if(totalProjects>0):
        cstyle = Style(
            major_label_font_size = 22,
            label_font_size = 23,
            legend_font_size = 25,
            value_font_size=25,
            font_family='googlefont: Helvetica',
            title_font_size = 22,
            colors=('#FD625E','#FE9666','#01B8AA','#cccccc')
        )
        bar_chart = pygal.HorizontalBar(
            width=650, height=500,
            legend_at_bottom=True,legend_at_bottom_columns=4,
            truncate_label=-1,show_x_labels=False,           
            print_values=True,
            print_values_position='top',
            no_data_text='Not Available',
            js=[],
            style=cstyle
        )
        statusMapping = await HM.getConfig('config')
        statusMapping = statusMapping['statusMapping']
        offTrack = len(projectsDF.overallstatus[projectsDF.overallstatus.isin(statusMapping['offtrack'])])
        alert = len(projectsDF.overallstatus[projectsDF.overallstatus.isin(statusMapping['alert'])])
        onTrack = len(projectsDF.overallstatus[projectsDF.overallstatus.isin(statusMapping['ontrack'])])
        notAssigned = totalProjects-(offTrack+alert+onTrack)

        bar_chart.add('Off track',offTrack)
        bar_chart.add('Alert',alert)
        bar_chart.add('On track',onTrack)
        bar_chart.add('NA',notAssigned)
        return bar_chart.render_data_uri()
    
    return 0

#def getStatusHistoryPieChart(project,df):
#     cstyle = Style(
#         major_label_font_size = 22,
#         label_font_size = 18,
#         legend_font_size = 18,
#         value_font_size=20,
#         title_font_size = 22,
#         font_family='googlefont: Helvetica',
#         colors=('#FD625E','#FE9666','#01B8AA')
#     )
#     # percent_formatter = lambda x: '{:.10g}%'.format(x)
#     piechart = pygal.Pie(
#         width=700, height=600,
#         legend_at_bottom=True, legend_at_bottom_columns=3,truncate_label=-1,              
#         print_values=True,
#         style=cstyle
#         # value_formatter = percent_formatter
#     )    
    
#     total_reports = len(df)
#     piechart.title = "Number of Reports submitted till date - {count}".format(count = total_reports)
#     statusMapping = HM.getConfig('config')['statusMapping']
#     if(total_reports>0):
#         offTrack = len(df.overallstatus[df.overallstatus.isin(statusMapping['offtrack'])])
#         alert = len(df.overallstatus[df.overallstatus.isin(statusMapping['alert'])])
#         onTrack = len(df.overallstatus[df.overallstatus.isin(statusMapping['ontrack'])])

#         offPerc = (offTrack/total_reports)*100
#         alertPerc = (alert/total_reports)*100
#         onPerc = (onTrack/total_reports)*100

#         piechart.add('Off Track',offPerc)
#         piechart.add('Alert',alertPerc)
#         piechart.add('On Track',onPerc)
#     else:
#         piechart.add('Off Track',0)
#         piechart.add('Alert',0)
#         piechart.add('On Track',0)
    
#     svgData = piechart.render_data_uri()
#     return svgData

# def getProjectsGroupedByStageChartPie(projectsDF):
#     cstyle = Style(
#         major_label_font_size = 22,
#         label_font_size = 20,
#         legend_font_size = 20,
#         value_font_size=20,
#         title_font_size = 22,
#         # transition='100ms ease-in',
#         colors=('#B7A6AD','#BEB2A7','#CAB388','#B5B292','#cccccc')
#     )
#     piechart = pygal.Pie(
#         width=600, height=500,
#         legend_at_bottom=True, legend_at_bottom_columns=5,truncate_label=-1,              
#         print_values=True,
#         style=cstyle
#     ) 
#     totalProjects = len(projectsDF)
#     piechart.title = "Total - {count} Projects".format(count = totalProjects)
#     if(totalProjects>0):
#         concept = len(projectsDF.stage[projectsDF.stage=="Concept Definition"])
#         plan = len(projectsDF.stage[projectsDF.stage=="Initiate/Plan"])
#         delivery = len(projectsDF.stage[projectsDF.stage=="Execute/Delivery"])
#         closed = delivery = len(projectsDF.stage[projectsDF.stage=="Closure"])
#         notAssigned = totalProjects-(concept+plan+delivery+closed)

#         piechart.add('Concept',concept)
#         piechart.add('Planning',plan)
#         piechart.add('Delivery',delivery)  
#         piechart.add('Closed',closed)  
#         piechart.add('NA',notAssigned)    

#         svgData = piechart.render_data_uri()
#         return svgData   
#     else:
#         return 0

# def getProjectsGroupedByStatusChartPie(projectsDF):
#     cstyle = Style(
#         major_label_font_size = 22,
#         label_font_size = 20,
#         legend_font_size = 22,
#         value_font_size=20,
#         title_font_size = 22,
#         # transition='100ms ease-in',
#         colors=('#FD625E','#FE9666','#01B8AA','#cccccc')
#     )
#     piechart = pygal.Pie(
#         width=650, height=500,
#         legend_at_bottom=True, legend_at_bottom_columns=2,truncate_label=-1,              
#         print_values=True,
#         style=cstyle
#     ) 
#     totalProjects = len(projectsDF)
#     piechart.title = "Total - {count} Projects".format(count = totalProjects)

#     if(totalProjects>0):
#         offTrack = len(projectsDF.projectstatus[projectsDF.projectstatus==8])
#         alert = len(projectsDF.projectstatus[projectsDF.projectstatus==9])
#         onTrack = len(projectsDF.projectstatus[projectsDF.projectstatus==10])
#         notAssigned = totalProjects-(offTrack+alert+onTrack)
#         offTrackP = (offTrack/totalProjects)*100
#         onTrackP = (onTrack/totalProjects)*100
#         alertP = (alert/totalProjects)*100
#         NAP = (notAssigned/totalProjects)*100

#         piechart.add('Off Track {p}%'.format(p=offTrackP),offTrack)
#         piechart.add('Alert {p}%'.format(p=alertP),alert)
#         piechart.add('On Track {p}%'.format(p=onTrackP),onTrack)  
#         piechart.add('Not Reported {p}%'.format(p=NAP),notAssigned)    

#         svgData = piechart.render_data_uri()
#         return svgData   
#     else:
#         return 0