import json
from datetime import datetime

from service.coe_analysis.crawler.getDoc import get_tag, getCoeJson
from service.coe_analysis.search_coe_result_item import search_all_chain
from utils import logger
from service.lang_chain_utils.lion_client import client as lion
from service.coe_analysis.coe_store_service import search_coe
from llmcore_sdk.utils.wiki_utils import WikiDocument, wiki_maker
import re


def get_additional_information(documents: list, coe_id: str):
    # 初始化信息字典
    additional_information = {
        "todo_information": '',
        "cause_information": '',
        "time_information": '',
        "qa_test_information": '',
        "fault_discovery_information": '',
        "risk_assistant_information": ''
    }
    for document in documents:
        desc = document.metadata.get('desc')
        category = document.metadata.get('category')
        page_content = document.page_content

        if desc in ['[正确做法]', '[经验教训]']:
            additional_information["todo_information"] += page_content
        elif desc == '[原因分析信息]':
            if category == '分析故障根因':
                additional_information["cause_information"] += page_content
            elif category == '分析测试流程':
                additional_information["qa_test_information"] += page_content
            elif category == '分析故障发现':
                additional_information["fault_discovery_information"] += page_content
        elif desc == '[时间线信息]':
            additional_information["time_information"] += page_content
    # 风险助手Agent需要APPKEY
    coe_info = getCoeJson('', coe_id)
    additional_information["risk_assistant_information"] = "appKey:" + coe_info['incident'].get('appkey', '')

    return additional_information


def make_wiki_for_general(task_id, type_list, task_name: str):
    '''
    生成wiki1
    作用：AI分析结果的通用性输出
    '''
    agent_name_mapping = lion.config.get(f'{lion.app_name}.agent_name_mapping')
    type_mapping = json.loads(agent_name_mapping)
    result_list, _ = search_all_chain(task_id)
    doc = WikiDocument.make_root_doc()
    doc.append_title(title=task_name)
    tb = doc.append_table()
    hed = tb.append_table_row()
    # 创建每一列  共计8
    hed.append_table_item('table_header', text=' ', colwidth=[50])
    hed.append_table_item('table_header', text='团队', colwidth=[150])
    hed.append_table_item('table_header', text='COE描述', colwidth=[150])
    hed.append_table_item('table_header', text='等级', colwidth=[100])
    hed.append_table_item('table_header', text='类型', colwidth=[100])
    hed.append_table_item('table_header', text='负责人', colwidth=[100])
    hed.append_table_item('table_header', text='变更来源系统', colwidth=[100])
    hed.append_table_item('table_header', text='发现方式', colwidth=[100])
    hed.append_table_item('table_header', text='原因分类', colwidth=[200])
    hed.append_table_item('table_header', text='原因下钻问题关键字', colwidth=[150])

    # 分析结果写入Wiki
    for analysis_type in type_list:
        hed.append_table_item('table_header', text=f'{type_mapping[analysis_type]}', colwidth=[400])  # 处理这个字段

    analysis_result_dict = merge_agent_answer(task_id)
    for coe in analysis_result_dict:
        coe_info, _id = search_coe(coe)
        coe_tags = get_tag(coe)
        row = tb.append_table_row()  # 为每个coe添加一行，用于存储该 COE 的详细信息。
        row.append_table_item(type='table_cell', numCell=True, text=' ', colwidth=[50])  # 在当前行中添加一个单元格，作为序号列。
        row.append_table_item(type='table_cell', text=f'{coe_info.org_path}', colwidth=[150])  # 团队
        item = row.append_table_item(type='table_cell', colwidth=[150])
        pg = item.append_paragraph()
        pg.append_link(href=f'https://coe.mws.sankuai.com/detail/{coe}', text=coe_info.brief)  # COE描述
        if coe_info.level is None:
            coe_info.level = "待定级"
        if coe_info.level == 'E':
            coe_info.level = "事件"
        row.append_table_item(type='table_cell', text=f'{coe_info.level}', colwidth=[100])  # 等级
        row.append_table_item(type='table_cell', text=f'{coe_info.category}', colwidth=[100])  # 类型
        row.append_table_item(type='table_cell', text=f'{coe_info.create_by}', colwidth=[100])  # 负责人

        row.append_table_item(type='table_cell', text=f'{coe_tags.get("变更来源系统")}', colwidth=[100])  # 变更来源系统
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题发现方式")}', colwidth=[100])  # 发现方式
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题原因分类")}', colwidth=[200])  # 原因分类
        item = row.append_table_item(type='table_cell', colwidth=[150])  # 原因下钻问题关键字
        pg = item.append_paragraph()
        pg.append_status(text=f'{coe_tags.get("二级标签")}', pattern=" ")
        # 填写AI分析结果
        for analysis_type in type_list:
            analysis_type_ans = analysis_result_dict[coe][analysis_type]
            if len(analysis_type_ans) > 3:
                ai_res = analysis_type_ans[3].content
            else:
                ai_res = ''
            row.append_table_item(type='table_cell', text=f'{ai_res}', colwidth=[400])  # 改动模块

    parentId = lion.config[f'{lion.app_name}.coe.tonotto.parentId']
    res = wiki_maker(content=doc.to_json_dict(), title=task_name, parentId=parentId)
    response = res.json()
    logger.info(response)
    _id = None
    if response['status'] == 200:
        _id = response['data']
        lnk = f'https://km.sankuai.com/collabpage/{_id}'
        logger.info(f"报告链接: {lnk}")
        return lnk
    raise Exception('没有完成报告')


def make_wiki_for_report(task_id, task_name: str):
    '''
    生成wiki2
    作用：组织下COE月报--每个月需要定时产生报告
    '''
    doc = WikiDocument.make_root_doc()
    doc.append_title(title=task_name)
    tb = doc.append_table()
    hed = tb.append_table_row()
    # 创建每一列
    hed.append_table_item('table_header', text=' ', colwidth=[50])
    hed.append_table_item('table_header', text='方向', colwidth=[100])
    hed.append_table_item('table_header', text='团队', colwidth=[150])
    hed.append_table_item('table_header', text='COE描述', colwidth=[150])
    hed.append_table_item('table_header', text='等级', colwidth=[100])
    hed.append_table_item('table_header', text='类型', colwidth=[100])
    hed.append_table_item('table_header', text='负责人', colwidth=[100])
    hed.append_table_item('table_header', text='变更来源系统', colwidth=[100])
    hed.append_table_item('table_header', text='发现方式', colwidth=[100])
    hed.append_table_item('table_header', text='原因分类', colwidth=[200])
    hed.append_table_item('table_header', text='原因下钻问题关键字', colwidth=[150])
    hed.append_table_item('table_header', text='AI问题归因', colwidth=[250])  # 处理这个字段
    hed.append_table_item('table_header', text='AI分析关联技术债', colwidth=[400])  # 处理这个字段
    hed.append_table_item('table_header', text='影响业务线', colwidth=[100])
    hed.append_table_item('table_header', text='触发条件', colwidth=[150])
    hed.append_table_item('table_header', text='资损金额', colwidth=[100])
    hed.append_table_item('table_header', text='发现时长', colwidth=[100])
    hed.append_table_item('table_header', text='响应处理时长', colwidth=[100])
    hed.append_table_item('table_header', text='修复时长', colwidth=[100])
    hed.append_table_item('table_header', text='影响时长', colwidth=[100])
    hed.append_table_item('table_header', text='影响消除时长', colwidth=[100])
    hed.append_table_item('table_header', text='创建时间', colwidth=[100])
    hed.append_table_item('table_header', text='发生时间', colwidth=[100])
    hed.append_table_item('table_header', text='发现时间', colwidth=[100])
    hed.append_table_item('table_header', text='处理完成时间', colwidth=[100])
    hed.append_table_item('table_header', text='影响消除时间', colwidth=[100])
    hed.append_table_item('table_header', text='AI分析总结（根因和优化TO DO）', colwidth=[500])  # 处理这个字段
    hed.append_table_item('table_header', text='COE待办事项', colwidth=[500])  # 处理这个字段

    analysis_result_dict = merge_agent_answer(task_id)
    sorted_data = dict(sorted(analysis_result_dict.items(), key=lambda x: x[1]['org_path']))
    for coe in sorted_data:
        coe_info, _id = search_coe(coe)
        coe_tags = get_tag(coe)
        coe_timelines = extract_time_labels(coe)
        coe_todo_analysis = analysis_result_dict[coe]["todo_analysis"]
        coe_debt_label = analysis_result_dict[coe]["debt_label"]
        coe_cause_analysis = analysis_result_dict[coe]["cause_analysis"]
        coe_path = coe_info.org_path.split('/')
        x2_path = ''
        x1_path = coe_info.org_path
        if len(coe_path) >= 4:
            x3_path = coe_path[2]
            x2_path = '/'.join(coe_path[3:-1])
            x1_path = coe_path[-1]
        #  写入基本信息
        row = tb.append_table_row()  # 为每个coe添加一行，用于存储该 COE 的详细信息。
        row.append_table_item(type='table_cell', numCell=True, text=' ', colwidth=[50])  # 在当前行中添加一个单元格，作为序号列。
        row.append_table_item(type='table_cell', text=f'{x2_path}', colwidth=[100])  # 方向
        row.append_table_item(type='table_cell', text=f'{x1_path}', colwidth=[150])  # 团队
        item = row.append_table_item(type='table_cell', colwidth=[150])
        pg = item.append_paragraph()
        pg.append_link(href=f'https://coe.mws.sankuai.com/detail/{coe}', text=coe_info.brief)  # COE描述

        if coe_info.level is None:
            coe_info.level = "待定级"
        if coe_info.level == 'E':
            coe_info.level = "事件"
        row.append_table_item(type='table_cell', text=f'{coe_info.level}', colwidth=[100])  # 等级
        row.append_table_item(type='table_cell', text=f'{coe_info.category}', colwidth=[100])  # 类型
        row.append_table_item(type='table_cell', text=f'{coe_info.create_by}', colwidth=[100])  # 负责人
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("变更来源系统")}', colwidth=[100])  # 变更来源系统
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题发现方式")}', colwidth=[100])  # 发现方式

        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题原因分类")}', colwidth=[200])  # 原因分类
        item = row.append_table_item(type='table_cell', colwidth=[150])  # 原因下钻问题关键字
        pg = item.append_paragraph()
        pg.append_status(text=f'{coe_tags.get("二级标签")}', pattern=" ")

        # 写入AI原因分析
        coe_cause_text = "COE信息不足"
        if len(coe_cause_analysis) > 3:
            coe_cause_json = json.loads(remove_str(coe_cause_analysis[3].content))
            coe_cause_text = '\n'.join([
                f'【问题发生阶段】: {coe_cause_json.get("问题发生阶段")}',
                f'【一级分类】: {coe_cause_json.get("一级分类")}',
                f'【分类原因】: {coe_cause_json.get("分类原因")}',
                f'【二级分类】: {coe_cause_json.get("二级分类")}',
                f'【分类原因】: {coe_cause_json.get("分类原因")}'
            ])
        row.append_table_item(type='table_cell', text=f'{coe_cause_text}', colwidth=[250])  # AI问题归因

        # 写入技术债务分析
        debt_label_text = "COE信息不足"
        if len(coe_debt_label) > 3:
            debt_label = json.loads(remove_str(coe_debt_label[3].content))
            debtTagList = debt_label.get("debtTagList")
            values = [value for item in debtTagList for value in item.values()]

            labels = ["一级标签", "分类原因", "二级标签", "分类原因", "三级标签", "分类原因"]

            debt_label_text = '\n'.join([
                f'【{label}】: {values[i]}' if i < len(values) else f'【{label}】: 未提供'
                for i, label in enumerate(labels)
            ])
        row.append_table_item(type='table_cell', text=f'{debt_label_text}', colwidth=[400])  # AI分析关联技术债

        row.append_table_item(type='table_cell', text=f'{coe_tags.get("业务线")}', colwidth=[100])  # 影响业务线
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题触发条件")}', colwidth=[150])  # 触发条件
        loss_money = coe_tags.get("实际资损金额（元）")
        if loss_money is None:
            loss_money = 0
        if loss_money == 'None':
            loss_money = "待填写"
        row.append_table_item(type='table_cell', text=f'{loss_money}', colwidth=[100])  # 资损金额

        create_time = coe_timelines.get("创建时间")
        occur_time = coe_timelines.get("发生时间")
        find_time = coe_timelines.get("发现时间")
        solved_time = coe_timelines.get("处理完成时间")
        clear_time = coe_timelines.get("影响消除时间")
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, find_time)}',
                              colwidth=[100])  # 发现时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(find_time, solved_time)}',
                              colwidth=[100])  # 响应处理时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, solved_time)}',
                              colwidth=[100])  # 修复时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, clear_time)}',
                              colwidth=[100])  # 影响时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(solved_time, clear_time)}',
                              colwidth=[100])  # 影响消除时长
        row.append_table_item(type='table_cell', text=f'{create_time}', colwidth=[100])  # 创建时间
        row.append_table_item(type='table_cell', text=f'{occur_time}', colwidth=[100])  # 发生时间
        row.append_table_item(type='table_cell', text=f'{find_time}', colwidth=[100])  # 发现时间
        row.append_table_item(type='table_cell', text=f'{solved_time}', colwidth=[100])  # 处理完成时间
        row.append_table_item(type='table_cell', text=f'{clear_time}', colwidth=[100])  # 影响消除时间

        #  写入todo分析
        coe_todo_analysis_text = "COE信息不足"
        if len(coe_todo_analysis) > 3:
            coe_todo_analysis_res = json.loads(remove_str(coe_todo_analysis[3].content)).get('AI分析TODO')
            coe_todo_analysis_text = ''
            for item in coe_todo_analysis_res:
                coe_todo_analysis_text += f"阶段: {item['阶段']}\n"
                coe_todo_analysis_text += f"TODO: {item['todo']}\n\n"
        row.append_table_item(type='table_cell', text=f'{coe_todo_analysis_text}',
                              colwidth=[500])  # AI分析总结（根因和优化TO DO）

        coe_todo_list = get_todo_text(coe)
        result_str = ""
        for category, texts in coe_todo_list.items():
            result_str += f"Category: {category}\n"
            for text in texts:
                result_str += f"  {text}\n"
            result_str += "\n"  # 每个分类之间添加空行
        row.append_table_item(type='table_cell', text=f'{result_str}',
                              colwidth=[500])  # AI分析总结（根因和优化TO DO）

    parentId = lion.config[f'{lion.app_name}.coe.tonotto.parentId']
    res = wiki_maker(content=doc.to_json_dict(), title=task_name, parentId=parentId)
    response = res.json()
    logger.info(response)
    _id = None
    if response['status'] == 200:
        _id = response['data']
        lnk = f'https://km.sankuai.com/collabpage/{_id}'
        logger.info(f"报告链接: {lnk}")
        return lnk
    raise Exception('没有完成报告')


def make_wiki_for_report_V2(task_id, task_name: str):
    '''
    生成wiki3
    作用：兼容历史COE模版、字段
    '''
    doc = WikiDocument.make_root_doc()
    doc.append_title(title=task_name)
    tb = doc.append_table()
    hed = tb.append_table_row()
    # 创建每一列
    hed.append_table_item('table_header', text=' ', colwidth=[50])
    hed.append_table_item('table_header', text='X3团队', colwidth=[150])
    hed.append_table_item('table_header', text='X2团队', colwidth=[150])
    hed.append_table_item('table_header', text='X1团队', colwidth=[150])
    hed.append_table_item('table_header', text='COE描述', colwidth=[150])
    hed.append_table_item('table_header', text='等级', colwidth=[100])
    hed.append_table_item('table_header', text='类型', colwidth=[100])
    hed.append_table_item('table_header', text='负责人', colwidth=[100])
    hed.append_table_item('table_header', text='变更来源系统', colwidth=[100])
    hed.append_table_item('table_header', text='发现方式', colwidth=[100])
    hed.append_table_item('table_header', text='原因分类', colwidth=[200])
    hed.append_table_item('table_header', text='原因下钻问题关键字', colwidth=[150])
    hed.append_table_item('table_header', text='AI一级分类', colwidth=[150])
    hed.append_table_item('table_header', text='AI二级分类', colwidth=[150])
    hed.append_table_item('table_header', text='AI问题归因', colwidth=[250])  # 处理这个字段
    hed.append_table_item('table_header', text='AI分析关联技术债', colwidth=[400])  # 处理这个字段
    hed.append_table_item('table_header', text='影响业务线', colwidth=[100])
    hed.append_table_item('table_header', text='触发条件', colwidth=[150])
    hed.append_table_item('table_header', text='资损金额', colwidth=[100])
    hed.append_table_item('table_header', text='发现时长', colwidth=[100])
    hed.append_table_item('table_header', text='响应处理时长', colwidth=[100])
    hed.append_table_item('table_header', text='修复时长', colwidth=[100])
    hed.append_table_item('table_header', text='影响时长', colwidth=[100])
    hed.append_table_item('table_header', text='影响消除时长', colwidth=[100])
    hed.append_table_item('table_header', text='创建时间', colwidth=[100])
    hed.append_table_item('table_header', text='发生时间', colwidth=[100])
    hed.append_table_item('table_header', text='发现时间', colwidth=[100])
    hed.append_table_item('table_header', text='处理完成时间', colwidth=[100])
    hed.append_table_item('table_header', text='影响消除时间', colwidth=[100])
    hed.append_table_item('table_header', text='AI分析总结（根因和优化TO DO）', colwidth=[500])  # 处理这个字段
    hed.append_table_item('table_header', text='COE已有todo', colwidth=[500])  # 处理这个字段

    analysis_result_dict = merge_agent_answer(task_id)
    sorted_data = dict(sorted(analysis_result_dict.items(), key=lambda x: x[1]['org_path']))
    for coe in sorted_data:
        coe_info, _id = search_coe(coe)
        if coe_info is None:
            coe_info = getCoeJson('', coe).get('incident')  # 兼容老模版
            parts = coe_info.get('org_path').split('/')
            coe_level = coe_info.get('level')
            coe_category = coe_info.get('category')
            coe_create_by = coe_info.get('create_by')
            coe_brief = coe_info.get('brief')
        else:
            parts = coe_info.org_path.split('/')
            coe_level = coe_info.level
            coe_category = coe_info.category
            coe_create_by = coe_info.create_by
            coe_brief = coe_info.brief
        coe_tags = get_tag(coe)
        coe_timelines = extract_time_labels(coe)
        coe_todo_analysis = analysis_result_dict[coe]["todo_analysis"]
        coe_debt_label = analysis_result_dict[coe]["debt_label"]
        coe_cause_analysis = analysis_result_dict[coe]["cause_analysis"]

        # 写入基本信息
        row = tb.append_table_row()  # 为每个coe添加一行，用于存储该 COE 的详细信息。
        row.append_table_item(type='table_cell', numCell=True, text=' ', colwidth=[50])  # 在当前行中添加一个单元格，作为序号列。
        x3_path, x2_path, x1_path = '', '', ''
        if len(parts) >= 4:
            x3_path = parts[2]
            x2_path = '/'.join(parts[3:-1])
            x1_path = parts[-1]
        row.append_table_item(type='table_cell', text=f'{x3_path}', colwidth=[150])  # 团队
        row.append_table_item(type='table_cell', text=f'{x2_path}', colwidth=[150])  # 团队
        row.append_table_item(type='table_cell', text=f'{x1_path}', colwidth=[150])  # 团队
        item = row.append_table_item(type='table_cell', colwidth=[150])
        pg = item.append_paragraph()
        pg.append_link(href=f'https://coe.mws.sankuai.com/detail/{coe}', text=coe_brief)  # COE描述

        if coe_level is None:
            coe_level = "待定级"
        if coe_level == 'E':
            coe_level = "事件"
        row.append_table_item(type='table_cell', text=f'{coe_level}', colwidth=[100])  # 等级
        row.append_table_item(type='table_cell', text=f'{coe_category}', colwidth=[100])  # 类型
        row.append_table_item(type='table_cell', text=f'{coe_create_by}', colwidth=[100])  # 负责人
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("变更来源系统")}', colwidth=[100])  # 变更来源系统

        # 发现方式
        if coe_tags.get("线上问题发现方式") is None:
            A = getCoeJson('', coe)  # 获取根因服务
            level_standard = A['incident'].get('level_standard', None)
            if level_standard is None or level_standard == '':
                row.append_table_item(type='table_cell', text=f'{"主动发现"}', colwidth=[100])  # 发现方式
            else:
                level_standard1 = A['incident'].get('level_standard', None).get('name', '')
                if "商" in level_standard1:
                    row.append_table_item(type='table_cell', text=f'{"商诉"}', colwidth=[100])  # 发现方式
                elif "客" in level_standard1:
                    row.append_table_item(type='table_cell', text=f'{"客诉"}', colwidth=[100])  # 发现方式
                else:
                    row.append_table_item(type='table_cell', text=f'{"主动发现"}', colwidth=[100])  # 发现方式
        else:
            row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题发现方式")}', colwidth=[100])  # 发现方式

        # 兼容不同的模版类型-原因分类
        coe_cause_types = getCoeJson('types', coe)
        if len(coe_cause_types['types']) == 0:
            row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题原因分类")}', colwidth=[200])  # 原因分类
            item = row.append_table_item(type='table_cell', colwidth=[150])  # 原因下钻问题关键字
            pg = item.append_paragraph()
            pg.append_status(text=f'{coe_tags.get("二级标签")}', pattern=" ")
        else:
            coe_cause_types = getCoeJson('types', coe)
            parent = coe_cause_types['types'][0]['parent']
            child = coe_cause_types['types'][0]['child']
            row.append_table_item(type='table_cell', text=f'{parent}', colwidth=[200])  # 原因分类
            item = row.append_table_item(type='table_cell', colwidth=[150])  # 原因下钻问题关键字
            pg = item.append_paragraph()
            pg.append_status(text=f'{child}', pattern=" ")

        # 写入AI原因分析
        coe_cause_text = "COE信息不足"
        coe_ai_type1 = ''
        coe_ai_type2 = ''
        if len(coe_cause_analysis) > 3:
            coe_cause_json = json.loads(remove_str(coe_cause_analysis[3].content))
            coe_cause_text = '\n'.join([
                f'【问题发生阶段】: {coe_cause_json.get("问题发生阶段")}',
                f'【一级分类】: {coe_cause_json.get("一级分类")}',
                f'【分类原因】: {coe_cause_json.get("分类原因")}',
                f'【二级分类】: {coe_cause_json.get("二级分类")}',
                f'【分类原因】: {coe_cause_json.get("分类原因")}'
            ])
            coe_ai_type1 = coe_cause_json.get("一级分类")
            coe_ai_type2 = coe_cause_json.get("一级分类")
        row.append_table_item(type='table_cell', text=f'{coe_ai_type1}', colwidth=[250])  # AI一级分类
        row.append_table_item(type='table_cell', text=f'{coe_ai_type2}', colwidth=[250])  # AI二级分类
        row.append_table_item(type='table_cell', text=f'{coe_cause_text}', colwidth=[250])  # AI问题归因

        # 写入技术债务分析
        debt_label_text = "COE信息不足"
        if len(coe_debt_label) > 3:
            debt_label = json.loads(remove_str(coe_debt_label[3].content))
            debtTagList = debt_label.get("debtTagList")
            values = [value for item in debtTagList for value in item.values()]

            labels = ["一级标签", "分类原因", "二级标签", "分类原因", "三级标签", "分类原因"]

            debt_label_text = '\n'.join([
                f'【{label}】: {values[i]}' if i < len(values) else f'【{label}】: 未提供'
                for i, label in enumerate(labels)
            ])
        row.append_table_item(type='table_cell', text=f'{debt_label_text}', colwidth=[400])  # AI分析关联技术债

        row.append_table_item(type='table_cell', text=f'{coe_tags.get("业务线")}', colwidth=[100])  # 影响业务线
        row.append_table_item(type='table_cell', text=f'{coe_tags.get("线上问题触发条件")}', colwidth=[150])  # 触发条件
        loss_money = coe_tags.get("实际资损金额（元）")
        if loss_money is None:
            loss_money = 0
        if loss_money == 'None':
            loss_money = "待填写"
        row.append_table_item(type='table_cell', text=f'{loss_money}', colwidth=[100])  # 资损金额

        create_time = coe_timelines.get("创建时间")
        occur_time = coe_timelines.get("发生时间")
        find_time = coe_timelines.get("发现时间")
        solved_time = coe_timelines.get("处理完成时间")
        clear_time = coe_timelines.get("影响消除时间")
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, find_time)}',
                              colwidth=[100])  # 发现时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(find_time, solved_time)}',
                              colwidth=[100])  # 响应处理时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, solved_time)}',
                              colwidth=[100])  # 修复时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(occur_time, clear_time)}',
                              colwidth=[100])  # 影响时长
        row.append_table_item(type='table_cell', text=f'{calculate_time_difference(solved_time, clear_time)}',
                              colwidth=[100])  # 影响消除时长
        row.append_table_item(type='table_cell', text=f'{create_time}', colwidth=[100])  # 创建时间
        row.append_table_item(type='table_cell', text=f'{occur_time}', colwidth=[100])  # 发生时间
        row.append_table_item(type='table_cell', text=f'{find_time}', colwidth=[100])  # 发现时间
        row.append_table_item(type='table_cell', text=f'{solved_time}', colwidth=[100])  # 处理完成时间
        row.append_table_item(type='table_cell', text=f'{clear_time}', colwidth=[100])  # 影响消除时间

        #  写入todo分析
        coe_todo_analysis_text = "COE信息不足"
        if len(coe_todo_analysis) > 3:
            coe_todo_analysis_res = json.loads(remove_str(coe_todo_analysis[3].content)).get('AI分析TODO')
            coe_todo_analysis_text = ''
            for item in coe_todo_analysis_res:
                coe_todo_analysis_text += f"阶段: {item['阶段']}\n"
                coe_todo_analysis_text += f"TODO: {item['todo']}\n\n"
        row.append_table_item(type='table_cell', text=f'{coe_todo_analysis_text}',
                              colwidth=[500])  # AI分析总结（根因和优化TO DO）

        coe_todo_list = get_todo_text(coe)
        result_str = ""
        for category, texts in coe_todo_list.items():
            result_str += f"Category: {category}\n"
            for text in texts:
                result_str += f"  {text}\n"
            result_str += "\n"  # 每个分类之间添加空行
        row.append_table_item(type='table_cell', text=f'{result_str}',
                              colwidth=[500])  # AI分析总结（根因和优化TO DO）

    parentId = lion.config[f'{lion.app_name}.coe.tonotto.parentId']
    res = wiki_maker(content=doc.to_json_dict(), title=task_name, parentId=parentId)
    response = res.json()
    logger.info(response)
    _id = None
    if response['status'] == 200:
        _id = response['data']
        lnk = f'https://km.sankuai.com/collabpage/{_id}'
        logger.info(f"报告链接: {lnk}")
        return lnk
    raise Exception('没有完成报告')


def make_wiki_for_report_text(task_id, task_name: str):
    '''
    生成wiki4
    作用：生成文字版本COE内容，便于输入分析
    '''
    doc = WikiDocument.make_root_doc()
    doc.append_title(title=task_name)

    analysis_result_dict = merge_agent_answer(task_id)
    sorted_data = dict(sorted(analysis_result_dict.items(), key=lambda x: x[1]['org_path']))
    j = 0
    for coe in sorted_data:
        print("现在开始的COE" + str(coe))
        if coe in ('63442', "63154"):
            continue
        coe_info, _id = search_coe(coe)
        if coe_info is None:
            coe_info = getCoeJson('', coe).get('incident')  # 兼容老模版
            parts = coe_info.get('org_path')
            coe_level = coe_info.get('level')
            coe_category = coe_info.get('category')
            coe_create_by = coe_info.get('create_by')
            coe_brief = coe_info.get('brief')
        else:
            parts = coe_info.org_path
            coe_level = coe_info.level
            coe_brief = coe_info.brief
        coe_tags = get_tag(coe)
        coe_timelines = extract_time_labels(coe)
        coe_todo_analysis = analysis_result_dict[coe]["todo_analysis"]
        coe_cause_analysis = analysis_result_dict[coe]["cause_analysis"]
        coe_cause_json = json.loads(remove_str(coe_cause_analysis[3].content))

        #  原因分类进行聚合
        # if coe_cause_json.get("一级分类")  in ("基础组件使用问题"):
        #     j += 1
        #  组织维度进行聚合coe_cause_json.get("一级分类") == "代码发布问题"
        if "交易结算平台" in parts and coe_cause_json.get("一级分类") == "技术方案设计考虑不周":
            j += 1
            til = f"线上问题{str(j)}:{coe_brief} "
            doc.append_heading(til, 1)

            # 线上问题发现方式----------------------
            find_ways = ''
            if coe_tags.get("线上问题发现方式") is None:
                A = getCoeJson('', coe)  # 获取根因服务
                level_standard = A['incident'].get('level_standard', None)
                if level_standard is None or level_standard == '':
                    find_ways = "主动发现"
                else:
                    level_standard1 = A['incident'].get('level_standard', None).get('name', '')
                    if "商" in level_standard1:
                        find_ways = "商诉"
                    elif "客" in level_standard1:
                        find_ways = "客诉"
                    else:
                        find_ways = "主动发现"
            else:
                find_ways = coe_tags.get("线上问题发现方式")
            # 团队信息----------------------
            if len(parts.split('/')) >= 4:
                x3_path = parts[2]
                x2_path = '/'.join(parts[3:-1])
                x1_path = parts[-1]

            # 创建时间----------------------
            create_time = coe_timelines.get("创建时间")
            formatted_date = get_quarter(create_time)

            # 等级----------------------coe_level

            # 兼容不同的模版类型-COE原因分类-RD填写----------------------
            cause_type1 = ''
            cause_type2 = ''
            cause_type = ''
            coe_cause_types = getCoeJson('types', coe)
            if len(coe_cause_types['types']) == 0:
                cause_type = coe_tags.get("线上问题原因分类")
                cause_type2 = coe_tags.get("二级标签")
            else:
                coe_cause_types = getCoeJson('types', coe)
                parent = coe_cause_types['types'][0]['parent']
                child = coe_cause_types['types'][0]['child']
                cause_type = parent
                cause_type2 = child

            # 写入AI原因分析----------------------
            coe_cause_text = '\n'.join([
                f'【问题发生阶段】: {coe_cause_json.get("问题发生阶段")}',
                f'【一级分类】: {coe_cause_json.get("一级分类")}',
                f'【二级分类】: {coe_cause_json.get("二级分类")}',
            ])

            #  写入todo分析----------------------
            coe_todo_analysis_res = json.loads(remove_str(coe_todo_analysis[3].content)).get('AI分析TODO')
            coe_todo_analysis_text = ''
            i = 0
            for item in coe_todo_analysis_res:
                i += 1
                coe_todo_analysis_text += f"{i}.{item['todo']} "

            #  写入原有todo----------------------
            coe_todo_list = get_todo_textV2(coe)
            result_str = ""
            no = 0
            for category, texts in coe_todo_list.items():
                no += 1
                result_str += f"分类{no}: {category}\n"
                for text in texts:
                    result_str += f" {text}\n"
                # result_str += "\n"  # 每个分类之间添加空行

            total_text = (
                    "【发现方式】" + find_ways + "\n" +
                    "【创建时间】" + formatted_date + "\n" +
                    "【团队】" + x2_path + "\n" +
                    "【问题发生阶段】" + coe_cause_json.get("问题发生阶段") + "\n" +
                    "【一级原因分类】" + coe_cause_json.get("一级分类") + "\n" +
                    "【二级原因分类】" + coe_cause_json.get("二级分类") + "\n" +
                    "【AI分析改进措施】" + coe_todo_analysis_text + "\n" +
                    "【已经完成todo事项】" + result_str)
            doc.append_paragraph(total_text)
    parentId = lion.config[f'{lion.app_name}.coe.tonotto.parentId']
    res = wiki_maker(content=doc.to_json_dict(), title=task_name, parentId=parentId)
    response = res.json()
    logger.info(response)
    _id = None
    if response['status'] == 200:
        _id = response['data']
        lnk = f'https://km.sankuai.com/collabpage/{_id}'
        logger.info(f"报告链接: {lnk}")
        return lnk
    raise Exception('没有完成报告')


def get_quarter(date_str):
    """
    根据日期字符串判断是第几季度
    :param date_str: 日期字符串，格式为 "YYYY-MM-DD HH:mm:ss"
    :return: 字符串，格式为 "YYYY年QX"
    """
    from datetime import datetime

    # 转换为日期对象
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    year = date_obj.year
    month = date_obj.month

    # 判断季度
    if 1 <= month <= 3:
        quarter = "Q1"
    elif 4 <= month <= 6:
        quarter = "Q2"
    elif 7 <= month <= 9:
        quarter = "Q3"
    else:
        quarter = "Q4"

    return f"{year}年{quarter}"


# ========start_wiki生成过程处理函数===========
# 获取各分析维度的结果，返回字典{'279259': {'type1': {'message': 'ai分析'}, 'type2': {'message':'ai分析'} }
def merge_agent_answer(task_id):
    result_list, _ = search_all_chain(task_id)
    analysis_result_dict = {}

    for item in result_list:
        coe_id = item.coe_id
        coe_info, _id = search_coe(coe_id)
        coe_path = ''
        if coe_info is not None:
            coe_path = coe_info.org_path
        type_value = item.type
        message = item.message
        coe_timelines = extract_time_labels(coe_id)
        create_time_1 = coe_timelines.get("创建时间")
        create_time = (create_time_1)

        # 初始化字典结构并添加数据
        if coe_id not in analysis_result_dict:
            analysis_result_dict[coe_id] = {}
        analysis_result_dict[coe_id][type_value] = message
        analysis_result_dict[coe_id]["org_path"] = coe_path
        analysis_result_dict[coe_id]["create_time"] = create_time

    return analysis_result_dict


def remove_str(text):
    if text.startswith("```json") or text.endswith("```"):
        cleaned_data = text.strip("```json").strip("```")
    else:
        cleaned_data = text  # 保持原样
    return cleaned_data


def get_todo_text(coe_id):
    toDoJson = getCoeJson('improvements', coe_id)
    todo_list = []
    if len(toDoJson['improvements']) > 0:
        for ind, item in enumerate(toDoJson['improvements']):
            brief = item['brief']
            status = item['status']
            category = item['category']
            text = f'待办事项: {brief}——处理状态为:{status}'
            todo_list.append({"category": category, "text": text})
    category_dict = {}
    for item in todo_list:
        category = item['category']
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append(item['text'])
    return category_dict


def get_todo_textV2(coe_id):
    toDoJson = getCoeJson('improvements', coe_id)
    todo_list = []
    if len(toDoJson['improvements']) > 0:
        for ind, item in enumerate(toDoJson['improvements']):
            brief = item['brief']
            status = item['status']
            category = item['category']
            text = brief
            if status == 'DONE':
                todo_list.append({"category": category, "text": text})
    category_dict = {}
    for item in todo_list:
        category = item['category']
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append(item['text'])
    return category_dict


# 提取时间线的关键时间点
def extract_time_labels(coe_id):
    timeLineJson = getCoeJson('time_lines', coe_id)
    # 定义需要提取的标签
    required_tags = ['create_at', 'occur_time', 'find_time', 'solved_time', 'clear_time']
    # 提取字段
    result = {}
    for item in timeLineJson['time_line']:
        # 提取创建时间
        if 'create_at' in item:
            result['创建时间'] = item['create_at']
        # 提取其他时间字段
        for tag in item.get('tags', []):
            if tag['key'] in required_tags:
                result[tag['label']] = item['time']
    return result


# 计算时间之差(单位h)--计算发现时长、影响时长之类
def calculate_time_difference(start_time: str, end_time: str):
    """
    计算两个时间字符串之间的时间差（单位：小时）

    :param start_time: 开始时间，格式为 'YYYY-MM-DD HH:MM:SS'
    :param end_time: 结束时间，格式为 'YYYY-MM-DD HH:MM:SS'
    :return: 时间差，单位为小时，返回浮点数
    """
    # 转换为 datetime 对象
    if start_time is None or end_time is None:
        return None
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    # 计算时间差（秒）
    time_difference = (end - start).total_seconds()
    # 转换为小时并返回
    return round(time_difference / 3600, 2)


# 提取字符串中[]中的内容，并按照 ----- 切分返回列表。
def extract_brackets_and_split(input_string: str) -> dict:
    """
    提取字符串中 [] 中的内容，并按照 ----- 切分返回列表。
    :param input_string: 输入的多行字符串
    :return: 包含提取的 [] 内容和切分后的列表的字典
    """
    # 提取 [] 中的内容
    bracket_content = None
    if "[" in input_string and "]" in input_string:
        bracket_content = input_string.split("[")[1].split("]")[0].strip()

    # 按 ----- 切分字符串
    split_content = input_string.split("-----")
    split_content = [section.strip() for section in split_content if section.strip()]  # 去除空白部分

    return {
        "bracket_content": bracket_content,
        "split_content": split_content
    }


# 去除文本的前端样式标签
def clean_text(text):
    # 去除HTML标签
    clean = re.sub(r'<[^>]+>', '', text)
    # 去除方括号中的内容（如[标题], [现象]等）
    clean = re.sub(r'\[[^\]]+\]', '', clean)
    # 去除多余的空行
    clean = re.sub(r'\n\s*\n', '\n\n', clean)
    # 去除行首的空白字符
    clean = re.sub(r'^\s+', '', clean, flags=re.MULTILINE)
    return clean.strip()
