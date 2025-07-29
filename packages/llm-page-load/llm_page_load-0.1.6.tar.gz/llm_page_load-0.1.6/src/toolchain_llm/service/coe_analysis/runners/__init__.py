import json

from service.coe_analysis.runners.base import COEBaseRunner
from service.coe_analysis.runners.cause import COESummaryRunner, COETopicAnalysisRunner
from service.coe_analysis.runners.fund import COEFundProblemRunner, COEFundJudgementRunner, COEFundAggregrateClassifyRunner  # noqa
from service.coe_analysis.runners.loaders import COELoader, COESpliter, get_COE_6to2not_Spliter, dispatch_COE_Spliter
from service.coe_analysis.runners.retriver import COEChainRetriver, COETopicRetriver
from service.coe_analysis.data_structure import COEResult, Experience
from service.coe_analysis.runners.tagconsist import COETagConsistantRunner
from service.coe_analysis.runners.tonotto import (
    COE6to2notRunner, COEReportTimeRunner, COE6to2notMutiAskRunner,
    COE6to2notMCMRunner, COE6to2notS9Runner
)
from service.coe_analysis.runners.determinate_search import DeterminateSearchRunner
from service.lang_chain_utils.lion_client import client as lion
lion.fetch_config()
post_xgpt_agent = lion.config.get(f'{lion.app_name}.post_xgpt_agent')
post_xgpt_agent_dict = json.loads(post_xgpt_agent)


def get_runner_by_type(result_item: COEResult, _id: str, type: str, extra_args= []):

    """
    runner工厂方法
    """
    if type in {'cause'} or type in post_xgpt_agent_dict:
        return COESummaryRunner(result_item=result_item, _id=_id)
    elif type == 'determinate_search':
        runner = DeterminateSearchRunner(result_item=result_item, _id=_id, args=extra_args)
        return runner
    elif type in COE6to2notMCMRunner.valid_type_list:
        runner = COE6to2notMCMRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    elif type in ['not_to_delay']:
        runner = COEReportTimeRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    elif type in COE6to2notRunner.valid_type_list:
        runner = COE6to2notRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    elif type in COETagConsistantRunner.valid_type_list:
        runner = COETagConsistantRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    elif type in COEFundProblemRunner.valid_type_list:
        runner = COEFundProblemRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    elif type in COEFundJudgementRunner.valid_type_list:
        runner = COEFundJudgementRunner(result_item=result_item, _id=_id)
        return runner
    elif type in COEFundAggregrateClassifyRunner.valid_type_list:
        runner = COEFundAggregrateClassifyRunner(result_item=result_item, _id=_id)
        runner.init_prompt(type)
        return runner
    else:
        raise NotImplementedError(f"项目{type}没有实现")


__all__ = ['COEBaseRunner', 'COESummaryRunner', 'COETopicAnalysisRunner', 'COEFundProblemRunner', 'COELoader',
           'COESpliter', 'get_COE_6to2not_Spliter', 'dispatch_COE_Spliter', 'COEChainRetriver', 'COETopicRetriver',
           'COEResult', 'Experience', 'COETagConsistantRunner', 'COE6to2notRunner', 'COE6to2notS9Runner',
           'get_runner_by_type', 'COE6to2notMutiAskRunner']
