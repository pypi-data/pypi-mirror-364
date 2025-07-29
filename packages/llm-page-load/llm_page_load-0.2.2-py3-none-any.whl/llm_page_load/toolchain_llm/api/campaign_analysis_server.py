from flask import jsonify
from flask import request
from flask import Blueprint
from service.campaign_activity_analysis.chat import get_chat_prompt
from service.campaign_activity_analysis.config_reader import NameSpace
from service.campaign_activity_analysis.datastruct import ChangeLog, TestCaseTreeNode, CampaignRule
from service.campaign_activity_analysis.entity_server \
    import find_all_entity, find_entity_by_name, search_or_create_entity
from service.campaign_activity_analysis.es_client \
    import TreeNodeIndex, es_client, client, headers, ActivityRuleIndex
from service.campaign_activity_analysis.rule_server \
    import create_rule, find_all_rule, find_rule_by_entities, update_rule_info
from service.campaign_activity_analysis.runner import retrive_once, run_task_by_info_dict
from service.campaign_activity_analysis.task_server \
    import add_task_change_log, find_all_task, get_task_deep, task_metricx
from service.campaign_activity_analysis.tree_node_server \
    import create_node, find_node, get_node_deep, mark_node, remove_node_from_tree, search_all_marked, update_node
from utils import logger
import json
import urllib.parse
from service.lang_chain_utils.embedding import embed

campaign = Blueprint(NameSpace, __name__)


@campaign.before_request
def before():
    '''访问控制,只要传入了ssoid,就认为登陆了,userLogin例如liyilun02,暂时不对登陆与否进行卡空'''
    try:
        if (request.method not in ['GET', 'POST']):
            return
        info = request.environ.get('HTTP_USERINFO')
        info = urllib.parse.unquote(info)
        user_info = json.loads(info)
        logger.info(f'[登陆信息] {user_info}')
        ssoid = user_info['ssoId']
        if ssoid is None or len(ssoid) == 0:
            logger.info('[无效登陆信息]')
            request.environ.update({'HTTP_USERINFO': user_info})
            request.environ.update({'USER': user_info['userLogin']})
            # return jsonify({'error':'无效登陆信息'})
        else:
            request.environ.update({'USER': ''})
    except Exception as e:
        logger.exception(e.args)
        request.environ.update({'USER': ''})
        pass


@campaign.route('task/start', methods=['POST'])
def start_task():
    '''
    例子
    payload=
    {
      "activity_name":"团购联合立减",
      "activity_stack_rule_map": {
          "平台立减":"​两个活动的优惠无法叠加",
          "平台券": "在建立团购联合立减时​可以配置是否与平台券叠加",
          "商家立减": "在建立团购联合立减时​可以配置是否与商家立减叠加",
          "商家券": "在建立团购联合立减时​可以配置是否与商家券叠加"
      }
    }
    '''
    try:
        logger.info(f'[task/start] 开始分析任务 request={request.json}')
        payload = request.json
        task = run_task_by_info_dict(payload, username=request.environ.get('USER'))
        return jsonify({"task": task.to_json_dict()})
    except Exception as e:
        logger.exception('[task/start] 分析任务失败' + str(e))


@campaign.route('task/result', methods=['GET'])
def get_task_result():
    '''获取思维导图,是以树的形式呈现'''
    try:
        logger.info(f'[task/result] 开始获取结果 request={request.args}')
        task_id = request.args.get('task_id')
        task = get_task_deep(task_id)
        return jsonify({"task": task.to_json_dict()})
    except Exception as e:
        logger.exception('[task/result] 获取失败' + str(e))


@campaign.route('entity/get', methods=['GET'])
def get_entity_list():
    '''查找所有的活动实体
    TODO:分页
    '''
    try:
        logger.info('[entity/get] 开始')
        entity_list = find_all_entity()
        return jsonify({'entity': entity_list})
    except Exception as e:
        logger.exception('[task/result] 获取失败' + str(e))


@campaign.route('task/findall', methods=['GET'])
def get_all_task_list_():
    '''
    获取所有任务列表
    TODO:分页
    '''
    try:
        logger.info('[task/findall] 开始')
        task_list = find_all_task()
        return jsonify({'task_list': task_list})
    except Exception as e:
        logger.exception('[task/findall] 失败', e.args)


@campaign.route('rule/findall', methods=['GET'])
def get_all_rule_list_():
    '''
    获取所有规则的列表
    TODO:分页
    '''
    try:
        logger.info('[rule/findall] 开始')
        rule_list = find_all_rule()
        return jsonify({'rule_list': rule_list})
    except Exception as e:
        logger.exception('[rule/findall] 失败', e.args)


@campaign.route('chat/node/prompt', methods=['GET'])
def get_node_prompt():
    '''
    对于某个节点而言，需要在其上进行提问，这个时候必须能够获取到提问的模板
    '''
    try:
        node_id = request.args.get('node_id')
        type = request.args.get('type')
        template = request.args.get('template')
        logger.info(f'[chat/node/prompt] {node_id}-{type}-{template}')
        prompt, vars = get_chat_prompt(
            node_id=node_id, type=type, template=template)
        return jsonify({'prompt': prompt, 'vars': vars})
    except Exception as e:
        logger.exception('[chat/node/prompt] 获取失败' + str(e))


@campaign.route('rule/find_by_entities', methods=['POST'])
def find_rule_by_entities_():
    '''
    通过活动查找规则的方法，目前智能查找叠加规则，排序是最新最优先
    多活动规则暂时没有查询
    '''
    try:
        logger.info(f'[rule/find_by_entities] request={request.json}')
        payload = request.json
        entity_item_list = []
        for entity_name in payload['entities']:
            entity = find_entity_by_name(entity_name=entity_name)
            if (entity):
                entity_item_list.append(entity)
        rules = find_rule_by_entities(entity_item_list=entity_item_list)
        if (len(rules) > 0):
            rule_list = [rule.to_json_dict() for rule in rules]
            return jsonify({'rule': rules[0].rule, 'item': rules[0].to_json_dict(), 'rule_list': rule_list})
        else:
            return jsonify({'rule': ''})
    except Exception as e:
        logger.exception('[chat/node/prompt] 获取失败' + str(e))


@campaign.route('node/remove', methods=['GET'])
def do_remove_node():
    '''
    此处的remove并不会真的删除节点，而是将其索引移除
    '''
    try:
        node_id = request.args.get('node_id')
        logger.info(f'[node/remove] node_id={node_id}')
        parent, changelog = remove_node_from_tree(node_id=node_id)
        add_task_change_log(parent.task_id, changelog)
        return jsonify({'remove': 'ok'})
    except Exception as e:
        logger.exception('[node/remove] 失败' + str(e))


@campaign.route('node/mark', methods=['GET'])
def mark_node_():
    '''
    标记与反标记这个节点
    '''
    try:
        node_id = request.args.get('node_id')
        is_marked = request.args.get('is_marked').lower() == 'true'
        logger.info(f'[node/mark] node_id={node_id}')
        node, changelog = mark_node(node_id=node_id, is_marked=is_marked)
        add_task_change_log(node.task_id, changelog)
        return jsonify({'remove': 'ok'})
    except Exception as e:
        logger.exception('[node/remove] 失败' + str(e))


@campaign.route('node/experiences', methods=['GET'])
def get_experiences_():
    '''
    获取经验知识列表，这里需要保证存在embedding和children_id，并且已经marked，而且还是query提问类型
    TODO:分页
    '''
    try:
        logger.info('[node/experiences] 获取')
        exps = search_all_marked()
        return jsonify({'experiences': exps})
    except Exception as e:
        logger.exception('[node/remove] 失败' + str(e))


@campaign.route('entity/create', methods=['POST'])
def create_entity_():
    '''
    创建一个新的活动，如果已有，那么就不会创建
    '''
    try:
        payload = request.json
        logger.info(f'[entity/create] {payload}')
        entity = search_or_create_entity(payload['entity_name'])
        return jsonify(entity.to_json_dict())
    except Exception as e:
        logger.exception('[entity/create] 失败' + str(e))


@campaign.route('node/get_deep_node', methods=['GET'])
def get_deep_node_():
    '''用于局部更新某个节点后的所有内容'''
    try:
        node_id = request.args.get('node_id')
        logger.info('[node/get_deep_node] node_id='+node_id)
        data = get_node_deep(node_id)
        return jsonify({'tree_node': data})
    except Exception as e:
        logger.exception('[node/get_deep_node] 获取失败' + str(e))


@campaign.route('node/add_answer_node', methods=['POST'])
def add_answer_node_():
    '''
    直接加入回答节点
    '''
    try:
        payload = request.json
        logger.info(f'[node/add_answer_node] {payload}')
        node: TestCaseTreeNode = create_node(**payload)
        parent, _id = find_node(node.parent_id)
        changelog = ChangeLog(
            ref_node_id=parent.id,
            type='ADD_ANSWER_NODE',
            weight=1,
            old_children=parent.children_id,
            new_children=parent.children_id+[node.id]
        )
        parent.children_id.append(node.id)
        parent.change_log.append(changelog)
        data = {
            "doc": parent.to_json_dict()
        }
        client.update(TreeNodeIndex, id=_id, body=data, headers=headers)
        es_client.refresh(TreeNodeIndex)
        add_task_change_log(parent.task_id, changelog)
        return jsonify({'answer': 'ok'})
    except Exception as e:
        logger.exception('[node/add_answer_node] 创建失败' + str(e))


@campaign.route('node/update_answer_node', methods=['POST'])
def update_answer_node_():
    '''
    更新回答节点
    '''
    try:
        payload = request.json
        node = TestCaseTreeNode.from_json(payload)
        node_old, _id = find_node(node.id)
        logger.info(f'[node/update_answer_node] {payload}')
        changelog = ChangeLog(
            ref_node_id=node.id,
            type="UPDATE_ANSWER_NODE",
            weight=1,
            old_content=node_old.content,
            new_content=node.content
        )
        update_node(node, changelog)
        es_client.refresh(TreeNodeIndex)
        add_task_change_log(node_old.task_id, changelog)
        return jsonify({'answer': 'ok'})
    except Exception as e:
        logger.exception('[node/update_answer_node] 创建失败' + str(e))


@campaign.route('node/update_query_node', methods=['POST'])
def update_query_node_():
    '''
    废弃
    更新提问节点
    TODO: changelog
    '''
    try:
        payload = request.json
        node = TestCaseTreeNode.from_json(payload)
        logger.info(f'[node/update_query_node] {payload}')
        node.embedding = embed.embed_query(node.content)
        update_node(node)
        es_client.refresh(TreeNodeIndex)
        return jsonify({'answer': 'ok'})
    except Exception as e:
        logger.exception('[node/update_answer_node] 创建失败' + str(e))


@campaign.route('node/update_rule', methods=['POST'])
def update_rule():
    '''
    更新规则
    传入的应当是规则实体
    '''
    try:
        payload = request.json
        rule = CampaignRule.from_json(payload)
        logger.info(f'[node/update_rule] {payload}')
        update_rule_info(rule)
        es_client.refresh(ActivityRuleIndex)
        return jsonify({'answer': 'ok'})
    except Exception as e:
        logger.exception('[node/update_rule] 创建失败' + str(e))


@campaign.route('node/create_rule', methods=['POST'])
def create_rule_():
    '''
    创建规则
    rule
    entities: List[str] 活动名称
    short_name
    type
    '''
    try:
        payload = request.json
        rule = payload['rule']
        entities = payload['entities']
        short_name = payload['short_name']
        type = payload['type']
        logger.info(f'[node/create_rule] {payload}')
        entity_item_list = []
        for entity_name in entities:
            entity = search_or_create_entity(entity_name)
            entity_item_list.append(entity)
        create_rule(rule=rule, entity_item_list=entity_item_list, short_name=short_name, type=type)
        es_client.refresh(ActivityRuleIndex)
        return jsonify({'answer': 'ok'})
    except Exception as e:
        logger.exception('[node/create_rule] 创建失败' + str(e))


@campaign.route('embedding/retrive', methods=['POST'])
def embedding_retrive():
    '''
    根据 text 获取其相对应的embedding
    '''
    try:
        payload = request.json
        text = payload['text']
        rule_type = payload.get('rule_type', None)
        ans = retrive_once(query=text, rule_type=rule_type, k=3)
        return jsonify({'answer': [msg.content for msg in ans]})
    except Exception as e:
        logger.exception('[embedding/retrive] 获取失败' + str(e))


@campaign.route('task/metricx', methods=['GET'])
def get_task_metricx():
    '''
    获取task对应的测评数据
    host/task/metricx?task_id=...
    '''
    task_id = request.args.get('task_id')
    try:
        deny_ratio, result_edit_distance, ans_edit_distance = task_metricx(task_id)
        return jsonify({
            '拒绝比': deny_ratio,
            '结果修改率': result_edit_distance,
            '中间过程修改率': ans_edit_distance
        })
    except Exception as e:
        logger.exception(f'[task/metricx] task_id={task_id} 获取失败' + str(e))
