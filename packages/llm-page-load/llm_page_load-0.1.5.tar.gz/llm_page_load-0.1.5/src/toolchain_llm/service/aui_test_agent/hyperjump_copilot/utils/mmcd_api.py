import requests
import time
import random
import string


def http_request(method, url, headers=None, data=None):
    """
    通用HTTP请求方法
    """
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=data)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    else:
        raise ValueError("暂不支持该请求方法")
    response.raise_for_status()
    return response.json()

def add_scene(id, name, pageId, priority):
    """
    MMCD添加一条用例

    :param id: 即scene_id，lyrebird建立数据组后传入
    :param name: MMCD用例名称，修改会同步到lyrebird
    :param pageId: MMCD页面ID，用户自定义，int类型
    :param priority: MMCD用例优先级，用户自定义，int类型
    :return: 接口响应内容（json）
    """
    url = 'https://client.hotel.test.sankuai.com/page/scene'

    data = {
        "id": id,
        "name": name,
        "parent": pageId,
        "priority": priority,
        "online": 1,
        "pageId": pageId,
    }
    response = requests.put(url, json=data)
    return response.json()

def set_scene_product(productId, sceneId, implement):
    """
    MMCD上给用例设置产品信息
    :param productId: 产品ID，如美团android为2
    :param sceneId: 用例ID，用户自定义
    :param implement: 产物信息，如MRN
    :return: 接口返回内容（json）
    """
    url = 'https://client.hotel.test.sankuai.com/page/sceneProduct'
    data = {
        "productId": productId,
        "sceneId": sceneId,
        "implement": implement,
        "miniVersion": "",
        "testSupport": ["compatibility"]
    }
    response = requests.put(url, json=data)
    return response.json()

def get_page_object(business, productId, keyword):
    """
    获取MMCD页面对象，并根据keyword筛选name包含该关键字的数据组信息

    :param business: 业务类型，用户自定义，str类型
    :param productId: 产品ID，用户自定义，int类型
    :param keyword: 关键字，用户自定义，str类型
    :return: name包含keyword的数据组信息（list）
    """
    url = 'https://client.hotel.test.sankuai.com/page/getPageObject'
    data = {
        "business": business,
        "productId": productId,
        "priority": [1, 2, 3, 4],
        "testItem": "compatibility"
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()

    # 假设返回数据结构为 [ {...}, {...}, ... ]
    # 根据实际返回结构可调整
    filtered_groups = [group for group in result if keyword in group.get("name", "")]
    return filtered_groups

def create_user_job(app_url, business, category, job_name, user, pages):
    """
    创建hyperjump视觉测试任务

    :param app_url: 应用下载地址，用户自定义，str类型
    :param business: 业务类型，用户自定义，str类型
    :param category: 分类，用户自定义，str类型
    :param job_name: 任务名称，用户自定义，str类型
    :param user: 用户名称，用户自定义，str类型
    :param pages: 页面信息，使用 get_page_object 的结果返回
    :return: 接口响应内容（json）
    """
    url = 'https://client.hotel.test.sankuai.com/client/compatibility/userJob'
    data = {
        "platform": "Android",
        "plat": "Android",
        "job_name": job_name,
        "user": user,
        "business": business,
        "category": category,
        "type": "compatibility",
        "app_url": app_url,
        "pages": pages,
        "mock_data": True,
        "mock_flag": 1,
        "ab_key": "",
        "task_url": "",
        "use_test_devices": False,
        "mrn_bundle": "[{\"bundle_name\":\"\",\"version\":\"\",\"env\":\"\"}]",
        "id": "",
        "env_lock_mrn_bundle": "{\"plat\":\"Android\",\"bundle_list_test_env\":[],\"bundle_list_prod_env\":[{\"bundleName\":\"\",\"version\":\"\"}]}",
        "app_params": "{\"runEngine\":\"Mobile\",\"pageImpl\":\"All\",\"visionComponents\":\"LongWaitTime,ParallelTask\",\"detectShadow\":false,\"appLogin\":\"17344473050/jiulv888\",\"mmp\":\"\",\"clientSwimlane\":\"\",\"serverSwimlane\":\"\",\"ssoLoginUser\":\"\",\"debug_link\":true,\"privacyMode\":false,\"use_testID\":false,\"env_mrnEvaTest\":0,\"robustMode\":\"CHANGE_CUSTOM\",\"robustCustomConfig\":{},\"checkers\":\"\",\"configJson\":[{\"type\":\"signin\",\"info\":{\"htmOffline\":0,\"account\":\"\",\"password\":\"\",\"countryCode\":\"86\"}},{\"type\":\"mmp_package\",\"info\":{\"mmpEnv\":\"prod\",\"mmpVersionId\":\"\",\"mmp_urlScheme\":\"\"}},{\"type\":\"scheme\",\"info\":{\"value\":\"${URL_SCHEME}\"}}],\"product_info\":\"{\\\"appName\\\":\\\"\\\",\\\"authority\\\":\\\"www.meituan.com/\\\",\\\"evaKey\\\":\\\"group\\\",\\\"id\\\":2,\\\"implList\\\":[\\\"Native\\\",\\\"MRN\\\",\\\"Picasso\\\",\\\"H5\\\",\\\"MP\\\"],\\\"isDebugLink\\\":true,\\\"isLyrebird\\\":true,\\\"label\\\":\\\"美团-Android\\\",\\\"name\\\":\\\"meituan\\\",\\\"os\\\":\\\"Android\\\",\\\"perfName\\\":\\\"android_platform_monitor\\\",\\\"scheme\\\":\\\"imeituan\\\",\\\"sigmaId\\\":1,\\\"type\\\":\\\"app\\\"}\",\"taskSchemes\":{\"schemes\":[\"imeituan://www.meituan.com(举例)\",\"\"]},\"action_filter\":{},\"service_env\":[]}"
    }
    response = requests.post(url, json=data)
    return response.json()

def get_available_arm14_device(business, category):
    """
    查找当前空闲可用的ARM14执行机

    :param business: 业务类型，用户自定义，str类型
    :param category: 分类，用户自定义，str类型
    :return: 符合条件的设备sn，str类型
    """
    url = 'https://client.hotel.test.sankuai.com/compatibilityPhone/available'
    params = {
        'business': business,
        'jobType': 'compatibility',
        'platform': 'Android',
        'sourceType': 'Microscope',
        'category': category,
        'filterRule': 'ALL',
        'usePublic': 'true'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()

    # 获取 data-devices 列表
    devices = result.get('data').get('devices')
    if not devices:
        print("没有找到设备列表")
        return None

    # 筛选符合条件的设备
    available_devices = []
    for device in devices:
        # print(f"\n设备信息：{device}")
        if isinstance(device, dict):
            # print(f"model: {device.get('model')}")
            # print(f"status: {device.get('status')}")
            # print(f"sn: {device.get('sn')}")
            
            model = device.get('model')
            status = device.get('status')
            sn = device.get('sn')
            
            if model == 'ARM-Android14' and status == 'Idle' and sn:
                available_devices.append(sn)
                # print(f"✅ 符合条件: {sn}")
        else:
            print(f"设备信息不是字典类型: {type(device)}")

    print(f"符合条件的设备列表: {available_devices}")

    # 随机返回一个设备sn
    if available_devices:
        selected_sn = random.choice(available_devices)
        print(f"\n随机选择的设备sn: {selected_sn}")
        return selected_sn
    else:
        print("\n没有找到符合条件的设备")
        return None

def trigger_hyperjump_job(app_url, business, category, job_name, user, arm14_devices, filtered_pages, scene_id, socket_id,product_id):
    """
    触发 hyperjump 视觉测试任务

    :param app_url: 应用下载地址，用户自定义，str类型
    :param business: 业务类型，用户自定义，str类型
    :param category: 分类，用户自定义，str类型
    :param job_name: 任务名称，用户自定义，str类型
    :param user: 用户名称，用户自定义，str类型
    :param arm14_devices: ARM14设备列表，用户自定义，list类型
    :param filtered_pages: 页面信息，使用 get_page_object 的结果返回，list类型
    :param scene_id: 场景ID，用户自定义，int类型
    :return: 接口响应内容（json）
    """
    url = 'https://compatibility.hotel.test.sankuai.com/trigJob'
    
    # 在 filtered_pages 中添加 scene_id
    for page in filtered_pages:
        page['scene_id'] = scene_id

    data = {
        "plat": "Android",
        "app_plat": "Android",
        "job_type": "compatibility",
        "job_name": job_name,
        "user": user,
        "business": business,
        "category": category,
        "product_id": product_id,
        "devices": "127.1.5.1:21",
        "app_url": app_url,
        "pages": filtered_pages,
        "mock_data": "1",
        "mock_flag": 1,
        "ab_key": f"$socket_id:{socket_id}",
        "env_lock_mrn_bundle": "NA",
        "source_url": "http://qa.sankuai.com/client",
        "source_type": "Microscope",
        "use_test_device": "0",
        "app_params": "{\"runEngine\":\"Mobile\",\"pageImpl\":\"All\",\"visionComponents\":\"CaseAssistedGeneration\",\"detectShadow\":false,\"appLogin\":\"17344473050/jiulv888\",\"mmp\":\"\",\"clientSwimlane\":\"\",\"serverSwimlane\":\"\",\"ssoLoginUser\":\"\",\"debug_link\":true,\"privacyMode\":false,\"use_testID\":false,\"env_mrnEvaTest\":0,\"robustMode\":\"CHANGE_CUSTOM\",\"robustCustomConfig\":{},\"checkers\":\"\",\"configJson\":[{\"type\":\"signin\",\"info\":{\"htmOffline\":0,\"account\":\"\",\"password\":\"\",\"countryCode\":\"86\"}},{\"type\":\"mmp_package\",\"info\":{\"mmpEnv\":\"prod\",\"mmpVersionId\":\"\",\"mmp_urlScheme\":\"\"}},{\"type\":\"scheme\",\"info\":{\"value\":\"${URL_SCHEME}\"}}],\"product_info\":\"{\\\"appName\\\":\\\"\\\",\\\"authority\\\":\\\"www.meituan.com/\\\",\\\"evaKey\\\":\\\"group\\\",\\\"id\\\":2,\\\"implList\\\":[\\\"Native\\\",\\\"MRN\\\",\\\"Picasso\\\",\\\"H5\\\",\\\"MP\\\"],\\\"isDebugLink\\\":true,\\\"isLyrebird\\\":true,\\\"label\\\":\\\"美团-Android\\\",\\\"name\\\":\\\"meituan\\\",\\\"os\\\":\\\"Android\\\",\\\"perfName\\\":\\\"android_platform_monitor\\\",\\\"scheme\\\":\\\"imeituan\\\",\\\"sigmaId\\\":1,\\\"type\\\":\\\"app\\\"}\",\"taskSchemes\":{\"schemes\":[\"imeituan://www.meituan.com(举例)\",\"\"]},\"action_filter\":{},\"service_env\":[]}"
    }
    response = requests.post(url, json=data)
    return response.json()

def generate_random_name(prefix="test"):
    """生成随机测试名称
    格式: prefix_时间戳_随机字符串
    """
    timestamp = time.strftime("%Y%m%d%H%M")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{timestamp}_{random_str}"

def send_put_request(url, payload):
    """
    发送PUT请求到指定URL，并返回响应结果。

    :param url: 接口的URL
    :param payload: 请求的JSON数据
    :return: 响应的JSON数据
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=payload, headers=headers)
    return response.json()

def send_get_request(url, params=None):
    """
    发送GET请求到指定URL，并返回响应结果。

    :param url: 接口的URL
    :param params: 请求的查询参数
    :return: 响应的JSON数据
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def send_delete_request(url, params=None):
    """
    发送DELETE请求到指定URL，并返回响应结果。

    :param url: 接口的URL
    :param params: 请求的查询参数
    :return: 响应的JSON数据
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.delete(url, params=params, headers=headers)
    return response.json()


def remove_mmcd(id:int,name:str,parent:int,priority:int,pageId:int):
    url = "https://client.hotel.test.sankuai.com/page/scene"
    payload = {
        "id": id,
        "name": name,
        "parent": parent,
        "priority": priority,
        "online": 1,
        "pageId": pageId
    }
    response = send_put_request(url, payload)
    print("响应结果:", response)

def delete_mmcd_scene(sceneId:int):
    """
    删除MMCD场景

    :param sceneId: 场景ID
    :return: 响应的JSON数据
    """
    url = "https://client.hotel.test.sankuai.com/page/scene"
    params = {
        "sceneId": sceneId
    }
    response = send_delete_request(url, params)
    print("响应结果:", response)
    return response


def update_pics(pics:str,bu:str,user:str,appVersion:str):
    url = "https://client.hotel.test.sankuai.com/client/compatibility/changePics"
    # 使用当前时间
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    params = {
        "pics": pics,
        "changeTime": current_time,
        "appVersion": appVersion,
        "user": user,
        "business": bu
    }
    response = send_get_request(url, params)
    print("响应结果:", response)

def extract_page_id(url):
    """
    从URL中提取scene_id
    Args:
        url: 完整的URL字符串,如 https://qa.sankuai.com/client/page/5522/scene
    Returns:
        scene_id: 提取出的scene_id(int)
    """
    try:
        # 方法1:使用split分割
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'page':
                scene_id = int(parts[i+1])  # 转换为int类型
                return scene_id
                
    except Exception as e:
        print(f"解析scene_id出错:{str(e)}")
        return 0  # 解析失败返回0
        
    return 0  # 未找到scene_id返回0

def get_job_report(job_id: int):
    """
    获取任务报告信息

    :param job_id: 任务ID
    :return: 任务报告信息的JSON数据
    """
    url = f"https://client.hotel.test.sankuai.com/client/compatibility/reportInfo"
    params = {
        "jobId": job_id
    }
    response = send_get_request(url, params)
    pic_id=response['jobTask'][0]['sceneResultList'][0]['id']
    return pic_id

if __name__ == "__main__":
    report_data = get_job_report(360448)
    print(report_data)
    update_pics(report_data,'dzu','machongjian','12.33.40')
    # sceneId=47938
    # name="不太正式test0430"
    # priority=4
    # pageId=5442
    # implement="MRN"
    # productId=2 # 美团android为2
    # business = "dzupoimodule"
    # keyword = "不太正式"  # 你想筛选的关键字

    # app_url = "https://hyperloop-s3.sankuai.com/hpx-artifacts/3308332-973-1746004469590698/aimeituan-release_12.33.400-381025-aarch64.apk"
    # category = "美团"
    # job_name = "【MMCD】视觉AI运行验证0430"
    # user = "zhangxiaolong22"

    # # MMCD保存用例
    # result = add_scene(sceneId, name, pageId, priority)
    # print("接口返回：", result)

    # #MMCD设置用例产品信息
    # result = set_scene_product(productId, sceneId, implement)
    # print("接口返回：", result)


    # # 创建视觉测试任务过程中，根据关键字筛选用例    
    # filtered_pages = get_page_object(business, productId, keyword)
    # # print("筛选结果：", filtered_pages)

    # # 正式创建视觉测试任务
    # result = create_user_job(app_url, business, category, job_name, user, filtered_pages)
    # print("创建任务结果：", result)

    # # 随机获取1台空闲的ARM14执行机
    # arm14_device = get_available_arm14_device(business, category)
    # print("随选择的任意1台空闲的ARM14执行机：", arm14_device)

    # # 触发 hyperjump 视觉测试任务
    # result = trigger_hyperjump_job(app_url, business, category, job_name, user, arm14_device, filtered_pages, sceneId)
    # print("触发任务结果：", result)


