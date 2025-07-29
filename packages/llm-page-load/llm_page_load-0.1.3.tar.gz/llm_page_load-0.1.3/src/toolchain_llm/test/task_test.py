from service.coe_analysis.coe_task_service import create_task_sync


def main():
    id = create_task_sync(coe_list=[{'_id': '276415', 'brief': 'POI详情页底部购物车条与底Bar遮挡问题'}],
                          name='单独测试', source='手工',
                          type_list=['fund_judgement'],
                          submitter='liyilun02')
    print(id)


if __name__ == '__main__':
    main()
