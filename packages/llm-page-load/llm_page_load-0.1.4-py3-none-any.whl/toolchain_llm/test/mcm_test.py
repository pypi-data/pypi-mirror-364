from tools.oceanus_auth import get_oceanus_auth_header
from utils import logger, appkey
import requests
from kms_sdk.kms import Kms


class MCMPlanCreator:
    def __init__(self, mis=None, uid=None, name=None, orgId=None, orgName=None, orgPath=None, orgNamePath=None, avatarUrl=None, jobStatusId=None, isMaoyan=None, **kargs):  # noqa
        self.mis = mis
        self.uid = uid
        self.name = name
        self.orgId = orgId
        self.orgName = orgName
        self.orgPath = orgPath
        self.orgNamePath = orgNamePath
        self.avatarUrl = avatarUrl
        self.jobStatusId = jobStatusId
        self.isMaoyan = isMaoyan


class MCMPlanContent:
    def __init__(self, appkey=None, description=None, effect=None, rollbackPlan=None, testReport=None, onesLink=None, domain=None, gitAddr=None, verify=None, checklist=None, sop=None, grayPlan=None, observationIndicators=None, changeServiceDetailList=None, **kargs):  # noqa
        self.appkey = appkey
        self.description = description
        self.effect = effect
        self.rollbackPlan = rollbackPlan
        self.testReport = testReport
        self.onesLink = onesLink
        self.domain = domain
        self.gitAddr = gitAddr
        self.verify = verify
        self.checklist = checklist
        self.sop = sop
        self.grayPlan = grayPlan
        self.observationIndicators = observationIndicators
        self.changeServiceDetailList = changeServiceDetailList


class MCMPlanApprove:
    def __init__(self, user=None, level=None, status=None, remark=None, type=None, operateTime=None, **kargs):
        self.user = user
        self.level = level
        self.status = status
        self.remark = remark
        self.type = type
        self.operateTime = operateTime


class MCMPlanStep:
    def __init__(self, id=None, title=None, tool=None, action=None, allowedOperator=None, operator=None, status=None, remark=None, estimateStartTime=None, estimateEndTime=None, actualStartTime=None, actualEndTime=None, **kargs):  # noqa
        self.id = id
        self.title = title
        self.tool = tool
        self.action = action
        self.allowedOperator = allowedOperator
        self.operator = operator
        self.status = status
        self.remark = remark
        self.estimateStartTime = estimateStartTime
        self.estimateEndTime = estimateEndTime
        self.actualStartTime = actualStartTime
        self.actualEndTime = actualEndTime


class MCMPlanStepChange:
    def __init__(self, planId=None, stepId=None, env=None, tool=None, type=None, resource=None, appKey=None, operator=None, status=None, changeDetails=None, estimateStartTime=None, actualStartTime=None, actualEndTime=None, createTime=None, updateTime=None, deployGroups=None, **kargs):  # noqa
        self.planId = planId
        self.stepId = stepId
        self.env = env
        self.tool = tool
        self.type = type
        self.resource = resource
        self.appKey = appKey
        self.operator = operator
        self.status = status
        self.changeDetails = changeDetails
        self.estimateStartTime = estimateStartTime
        self.actualStartTime = actualStartTime
        self.actualEndTime = actualEndTime
        self.createTime = createTime
        self.updateTime = updateTime
        self.deployGroups = deployGroups


class MCMPlanNotice:
    def __init__(self, groups=None, content=None, handleGroup=None, **kargs):
        self.groups = groups
        self.content = content
        self.handleGroup = handleGroup


class MCMPlanBase:
    def __init__(self, env=None, changeType=None, riskLevel=None, scene=None, background=None, **kargs):
        self.env = env
        self.changeType = changeType
        self.riskLevel = riskLevel
        self.scene = scene
        self.background = background


class MCMPlan:
    def __init__(self, id=None, name=None, orgPath=None, creator={}, approveLevel=None, status=None, templateId=None, planBase={}, planContent={}, planApproves=[], planNotice={}, planSteps=[], planStepChanges=[], planStartTime=None, planEndTime=None, createTime=None, updateTime=None, timestamp=None, error=None, message=None, path=None, **kargs):  # noqa
        self.id = id
        self.name = name
        self.orgPath = orgPath
        self.creator = MCMPlanCreator(**creator)
        self.approveLevel = approveLevel
        self.status = status
        self.templateId = templateId
        self.planBase = MCMPlanBase(**planBase)
        self.planContent = MCMPlanContent(**planContent)
        self.planApproves = [MCMPlanApprove(**i) for i in planApproves]
        self.planNotice = MCMPlanNotice(**planNotice)
        self.planSteps = [MCMPlanStep(**i) for i in planSteps]
        self.planStepChanges = [MCMPlanStepChange(**i) for i in planStepChanges]
        self.planStartTime = planStartTime
        self.planEndTime = planEndTime
        self.createTime = createTime
        self.updateTime = updateTime
        self.timestamp = timestamp
        self.error = error
        self.message = message
        self.path = path


def mcm_plan(plan_id, env='prod'):
    token = Kms.get_by_name(appkey, f"sankuai.cf.plan.server.{env}")
    url = f'http://mcm.tbd.test.sankuai.com/open/api/v1/cf/plan/{plan_id}'
    if env == 'prod':
        url = f'http://mcm.vip.sankuai.com/open/api/v1/cf/plan/{plan_id}'
    auth = get_oceanus_auth_header("com.sankuai.cf.plan.server", appkey, token=token)
    headers = {'Content-Type': 'application/json'}
    headers.update(auth)
    response = requests.get(url, headers=headers)
    return MCMPlan(**response.json()['data'])


if __name__ == '__main__':
    plan = mcm_plan('220824', env='test')
    print(plan.planNotice.content)
    plan = mcm_plan('428302')
    print(plan.planNotice.content)
