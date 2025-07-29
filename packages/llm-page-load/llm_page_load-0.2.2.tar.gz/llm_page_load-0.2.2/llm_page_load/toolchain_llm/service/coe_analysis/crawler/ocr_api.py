import numpy
import time
import requests
import json

ocr_host = 'http://qa.sankuai.com/clientdata/horus/recognize/ocr'  #测试环境，如批量请求申请线上资源  
def get_ocr(image_source, offset_y=0, ocr_filter_score=0.95):
    result = {'code': 0, 'data': {'roi_text': [], 'img_shape': []}}
    header = {'Content-Type': 'application/json;charset=utf-8'}
    host = ocr_host
    payload = {'url': image_source, 'model_type': '2'}
    resp = requests.request('POST', url=host, data=json.dumps(payload), headers=header, timeout=30.0)
    resp_obj = json.loads(resp.text)
    # retry
    if resp_obj.get('code') != 0:
        time.sleep(2)
        resp = requests.request('POST', url=host, data=json.dumps(payload), headers=header, timeout=30.0)
        resp_obj = json.loads(resp.text)
    # process
    if resp_obj.get('code') == 0:
        shape_info = resp_obj['shape_info']
        if shape_info[0] > shape_info[1]:
            img_h, img_w = shape_info[0], shape_info[1]
        else:
            img_h, img_w = shape_info[1], shape_info[0]
        result['data']['img_shape'] = [img_h, img_w, 1]
        for i in range(len(resp_obj['results_str'])):
            score = float(resp_obj['prob_string'][i])
            text = resp_obj['results_str'][i]
            points = [int(point) for point in resp_obj['location'][i].replace('[', '').replace(']', '').split(' ') if len(point) > 0]
            rect = numpy.array([[points[0], points[1]+offset_y], [points[2], points[3]+offset_y],
                                [points[4], points[5]+offset_y], [points[6], points[7]+offset_y]])
            result['data']['roi_text'].append({'rect': rect, 'text': text, 'score': score}) if score > ocr_filter_score else 0
    else:
        result['code'] = 1
        result['data']['roi_text'].append({'rect': [], 'text': resp.text, 'score': 1.0})
    return result


if __name__=='__main__':
    answer = get_ocr('https://s3plus.sankuai.com/v1/mss_8122b41e49f949ed966dc671c9211129/issue/coe-files/2021-09-22-151851-image.png')
    print(answer)