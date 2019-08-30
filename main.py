from sanic import Sanic, response
import asyncio
import uvloop
import json
from logger import logger, timeit, clearLog
import helperModule as HM
import intents as INTENT
import DB
import time

app = Sanic()

@app.route("/")
async def test(request):
    return response.json({"hello": "world"})

@app.route("/testdb")
async def testdb(request):
    try:
        dataConfig = await HM.getConfig('config')
        dataKey = dataConfig['keys']["data-key"]
        if(request.args.get('key')==dataKey):
            start=time.time()
            conn = await DB.openConnection("sandpit")
            await DB.closeConnection(conn)
            return response.text("Time: "+str(time.time()-start))
        else:
            return response.text("Request Unauthorised")
    except Exception as ex:
        return response.text("Error occured: "+str(ex))
    

@app.route("/DownloadLogs")
async def DownloadLogs(request):
    try:
        dataConfig = await HM.getConfig('config')
        dataKey = dataConfig['keys']["data-key"]
        if(request.args.get('key')==dataKey):
            return await response.file('ApplicationLogs.log')
        else:
            return response.text("Request Unauthorised")
    except Exception as ex:
        return response.text("Error occured: "+str(ex))

@app.route("/ClearLogs")
async def ClearLogs(request):
    try:
        dataConfig = await HM.getConfig('config')
        dataKey = dataConfig['keys']["data-key"]
        if(request.args.get('key')==dataKey):
            clearLog()
            return response.text("Logs Cleared")
        else:
            return response.text("Request Unauthorised")
    except Exception as ex:
        return response.text("Error occured: "+str(ex))

@app.route("/feedback", methods=['GET', 'POST'])
async def feedback(request):
    #logger("Feedback Triggered")
    dataConfig = await HM.getConfig('config')
    dataKey = dataConfig['keys']["data-key"]
    apiKey = request.headers.get('data-key')
    client = request.headers.get('client')    

    if(apiKey == None):
        return response.text("data-key not present")
    else:
        if(apiKey!=dataKey):
            return response.text("data-key not valid")
        else:
            #logger("Key matched")
            data_request = request.body.decode('utf-8')
            if(data_request==''):
                return response.text('data object not found in request')
            dataObj = json.loads(data_request)
            cid = dataConfig['database'][client]['cid']
            dataObj['cid']=cid
            await DB.saveFeedbackToDB(dataObj)
            return response.text('Success')

@app.route("/intentController/<intent:string>/", methods=['GET', 'POST'])
#@timeit
async def intentController(request,intent):
    # loop = asyncio.get_event_loop()

    dataConfig = await HM.getConfig('config')
    dataKey = dataConfig['keys']["data-key"]

    # Intent - function mapping
    IFP = {
        "GetProjectListByEntity":INTENT.GetProjectListByEntity,
        "GetProjectByDivision":INTENT.GetProjectListByEntity,
        "GetProjectByRisk":INTENT.GetProjectListByEntity,
        "GetProjectByIssue":INTENT.GetProjectListByEntity,
        "GetProjectByReportStatus":INTENT.GetProjectListByEntity, 
        "GetProjectByProgram": INTENT.GetProjectListByEntity,

        "GetBudgetHistory": INTENT.GetBudgetHistory,
        "GetBudgetFromReport":INTENT.GetBudgetFromReport,
        
        "GetPrograms":INTENT.GetPrograms,
        "GetDivisions":INTENT.GetDivisions,

        "GetIssueByProject":INTENT.GetIssueByProject,
        "GetRiskByProject":INTENT.GetRiskByProject,
        "GetProductByProject":INTENT.GetProductByProject,
        "GetDependencyByProject": INTENT.GetDependencyByProject,

        "GetCount":INTENT.GetCount
    }

    apiKey = request.headers.get('data-key')
    client = request.headers.get('client')

    if(apiKey == None):
        return response.text("data-key not present")
    else:
        if(apiKey!=dataKey):
            return response.text("data-key not valid")
        else:
            if(intent=="ping"):
                conn = await DB.openConnection(client)
                await DB.closeConnection(conn)
                return response.text("Success")
            conditions = await HM.getConfig('queries')
            data_request = request.body.decode('utf-8')
            if(data_request=='' or data_request==None):
                return response.text('data object not found in request')
            dataObj = json.loads(data_request)
            conn = await DB.openConnection(client)
            intentResp = await IFP[intent](dataObj,conn,conditions['conditionsForSQL'],intent)     
            await DB.closeConnection(conn)    
            return response.text(intentResp)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app.run(host="0.0.0.0", port=80, debug=False, access_log=False, log_config=None)