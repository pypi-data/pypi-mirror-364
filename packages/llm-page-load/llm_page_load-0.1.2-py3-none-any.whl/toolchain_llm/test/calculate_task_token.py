from service.coe_analysis.coe_experience_service import get_experience
from service.coe_analysis.coe_task_service import search_task
from service.coe_analysis.search_coe_result_item import search_all_chain
from service.coe_analysis.data_structure import MetaMessage
from service.coe_analysis.runners.tonotto import COE6to2notRunner
from token_count.tokenizer import count_token
from service.coe_analysis.runners.retriver import get_prompt
from utils import write_io


def count_message_token(message: MetaMessage):
    user = 0
    assistant = 0
    if message.role in ['user', 'human', 'Human']:
        user += count_token(message.content)
    elif message.role in ['ai', 'AI', 'assistant']:
        assistant += count_token(message.content)
    return user, assistant


def count_coe_task_token(task_id: str):
    chains, total = search_all_chain(task_id=task_id)
    user = 0
    assistant = 0
    for chain in chains:
        for message in chain.message:
            user_tmp, assistant_tmp = count_message_token(message)
            user += user_tmp
            assistant += assistant_tmp
    return user, assistant


def count_average_embedding_token(type: str):
    exps, total = get_experience(size=1000, from_=0, type=type)
    user = 0
    assistant = 0
    total = len(exps)
    for exp in exps:
        for message in exp.data:
            user_tmp, assistant_tmp = count_message_token(message)
            user += user_tmp
            assistant += assistant_tmp
    return user//total, assistant//total


def count_6to2not_system_token(type: str):
    system_prompt = get_prompt(type, 'system')
    system = 3*count_token(system_prompt.template)
    user, assistant = count_average_embedding_token(type=type)
    cot_num = COE6to2notRunner.valid_k[type]
    for num in cot_num:
        system += num*(user+assistant)
    return system


def count_6to2not(task_id):
    task, _id = search_task(task_id=task_id)
    system = 0
    for type in task.sub_task_type_list:
        system += count_6to2not_system_token(type) * len(task.choosed_coe_list)
    user, assistant = count_coe_task_token(task_id)
    print(f'system={system}\tuser={user}\tassistant={assistant}')
    return system, user, assistant


def count_cause_system_token(type: str = 'cause'):
    system_prompt = get_prompt(type, 'system')
    system = 2*count_token(system_prompt.template)
    user, assistant = count_average_embedding_token(type=type)
    system += 3*(user+assistant)
    return system


def count_cause(task_id):
    task, _id = search_task(task_id=task_id)
    system = count_cause_system_token('cause') * len(task.choosed_coe_list)
    user, assistant = count_coe_task_token(task_id)
    print(f'system={system}\tuser={user}\tassistant={assistant}')
    return system, user, assistant


def count_money(system, user, assistant):
    _inp = 0.03*(system/1000+user/1000)
    _out = 0.06*assistant/1000
    print(f'money : input=${_inp}  output=${_out} total=${_inp+_out}')
    return _inp, _out


def main():
    result = []
    _total = 0
    for task_id in ['279769762081047964678516856588471374114',
                    '40925475018717133271756641305578829794',
                    ]:
        task, _id = search_task(task_id)
        system, user, assistant = count_cause(task_id)
        _inp, _out = count_money(system, user, assistant)
        result.append({'task_name': task.name, 'task_id': task.id, 'system': str(system),
                       'user': str(user), 'assistant': str(assistant),
                       'input': f'${_inp}', 'output': f'${_out}', 'total': f'${_inp+_out}'})
        _total += _inp+_out

    # tasks, total = get_all_task('2023-09-01', '2023-09-14', size=1000, from_=0)
    # for task in tasks:
    #     task: COEAnalysisTask = task
    #     if '资金安全分析' in task.name:
    #         user, assistant = count_coe_task_token(task.id)
    #         _inp, _out = count_money(0, user, assistant)
    #         result.append({'task_name': task.name, 'task_id': task.id, 'system': str(0),
    #                        'user': str(user), 'assistant': str(assistant),
    #                        'input': f'${_inp}', 'output': f'${_out}', 'total': f'${_inp+_out}'})
    #         _total += _inp+_out

    print(_total)
    write_io('test/token-3.xlsx', result)
    return result


if __name__ == '__main__':
    main()
