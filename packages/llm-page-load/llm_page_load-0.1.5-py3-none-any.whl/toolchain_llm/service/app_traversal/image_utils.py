

blank = 5
text_width, text_height = 23, 27

def get_center_pos(contour):
    x = int((contour[0][0]+contour[1][0])/2)
    y = int((contour[1][1]+contour[2][1])/2)
    return x, y

def get_bbox_center_pos(bbox):
    x = int((bbox[0] + bbox[2]) / 2)
    y = int((bbox[1] + bbox[3]) / 2)
    return x, y

def calculate_iou(box1, box2):
    # calculate intersection area
    # box1 = [x1, y1, x2, y2]
    # box2 = [x1, y1, x2, y2]
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)

    # calculate union area
    area_box1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    area_box2 = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    union_area = area_box1 + area_box2 - intersection_area

    # calculate iou
    iou = intersection_area / union_area
    return iou

def is_rectangles_nearby(rect1, rect2, dist):
    # 判断两个矩形是否邻近
    mid_x1, mid_y1 = (rect1[0] + rect1[2]) / 2, (rect1[1] + rect1[3]) / 2
    w1, h1 = rect1[2] - rect1[0], rect1[3] - rect1[1]
    mid_x2, mid_y2 = (rect2[0] + rect2[2]) / 2, (rect2[1] + rect2[3]) / 2
    w2, h2 = rect2[2] - rect2[0], rect2[3] - rect2[1]

    if abs(mid_x1 - mid_x2) < (w1 / 2 + w2 / 2 + dist) and abs(mid_y1 - mid_y2) < (h1 / 2 + h2 / 2 + dist):
        return True
    return False

def assemble_elems(elems, icon_dist):
    text_assembled_list = []
    # 先聚合text
    for i, elem in enumerate(elems):
        if elem['elem_det_type'] == 'textline':
            assembled = False
            x1, y1, x2, y2 = elem['elem_det_regionIterator'][0], \
                elem['elem_det_regionIterator'][1], \
                elem['elem_det_regionIterator'][2], \
                elem['elem_det_regionIterator'][3]
            for assembled_text in text_assembled_list:
                xx1, yy1, xx2, yy2 = assembled_text['elem_det_regionIterator'][0], \
                    assembled_text['elem_det_regionIterator'][1], \
                    assembled_text['elem_det_regionIterator'][2], \
                    assembled_text['elem_det_regionIterator'][3]
                # 如果iou大于0，说明重合，则直接聚合
                if calculate_iou([x1, y1, x2, y2], [xx1, yy1, xx2, yy2]) > 0:
                    assembled = True
                    assembled_text['elem_det_regionIterator'][0] = min(x1, xx1)
                    assembled_text['elem_det_regionIterator'][1] = min(y1, yy1)
                    assembled_text['elem_det_regionIterator'][2] = max(x2, xx2)
                    assembled_text['elem_det_regionIterator'][3] = max(y2, yy2)
                    if elem.get('elem_detail_info', '') != '':
                        assembled_text['elem_detail_info'] = assembled_text.get('elem_detail_info', '') + \
                                                                elem.get('elem_detail_info', '')
                    assembled_text['elem_det_type'] = 'textblock'
                    break
                # 如果间距小于一定阈值，则聚合
                elif is_rectangles_nearby([x1, y1, x2, y2], [xx1, yy1, xx2, yy2], icon_dist):
                    assembled = True
                    assembled_text['elem_det_regionIterator'][0] = min(x1, xx1)
                    assembled_text['elem_det_regionIterator'][1] = min(y1, yy1)
                    assembled_text['elem_det_regionIterator'][2] = max(x2, xx2)
                    assembled_text['elem_det_regionIterator'][3] = max(y2, yy2)
                    if elem.get('elem_detail_info', '') != '':
                        assembled_text['elem_detail_info'] = assembled_text.get('elem_detail_info', '') + \
                                                                elem.get('elem_detail_info', '')
                    assembled_text['elem_det_type'] = 'textblock'
                    break
            if not assembled:
                text_assembled_list.append(elem)
    text_assembled_list = assemble_union_elems(text_assembled_list)

    for elem in elems:
        if elem['elem_det_type'] != 'textline' and \
                elem['elem_det_type'] != 'top_system' and \
                elem['elem_det_type'] != 'bottom_system' and \
                elem['elem_det_type'] != 'bottom_ui':
            text_assembled_list.append(elem)
    text_assembled_list = assemble_union_elems(text_assembled_list)
    legal_elem = []
    for elem in text_assembled_list:
        if 'image' in elem['elem_det_type']:
            elem['elem_detail_info'] = ''
        if elem['elem_det_type'] == 'icon':
            elem['elem_detail_info'] = ''
        width = elem['elem_det_regionIterator'][2] - elem['elem_det_regionIterator'][0]
        height = elem['elem_det_regionIterator'][3] - elem['elem_det_regionIterator'][1]
        if width < blank + text_width or height < blank + text_height:
            continue
        else:
            legal_elem.append(elem)
    return legal_elem

def assemble_union_elems(elems):
    text_assembled_list = []
    for i, elem in enumerate(elems):
        assembled = False
        x1, y1, x2, y2 = elem['elem_det_regionIterator'][0], \
            elem['elem_det_regionIterator'][1], \
            elem['elem_det_regionIterator'][2], \
            elem['elem_det_regionIterator'][3]
        for assembled_text in text_assembled_list:
            xx1, yy1, xx2, yy2 = assembled_text['elem_det_regionIterator'][0], \
                assembled_text['elem_det_regionIterator'][1], \
                assembled_text['elem_det_regionIterator'][2], \
                assembled_text['elem_det_regionIterator'][3]
            # 如果iou大于0，说明重合，则直接聚合
            if calculate_iou([x1, y1, x2, y2], [xx1, yy1, xx2, yy2]) > 0:
                assembled = True
                assembled_text['elem_det_regionIterator'][0] = min(x1, xx1)
                assembled_text['elem_det_regionIterator'][1] = min(y1, yy1)
                assembled_text['elem_det_regionIterator'][2] = max(x2, xx2)
                assembled_text['elem_det_regionIterator'][3] = max(y2, yy2)
                if elem.get('elem_detail_info', '') != '':
                    if elem.get('elem_detail_info', '') not in assembled_text.get('elem_detail_info', ''):
                        assembled_text['elem_detail_info'] = assembled_text.get('elem_detail_info', '') + \
                                                                elem.get('elem_detail_info', '')
                if assembled_text['elem_det_type'] != elem['elem_det_type']:
                    assembled_text['elem_det_type'] = assembled_text.get('elem_det_type', '') + ' ' + elem.get(
                        'elem_det_type', '')
                break
        if not assembled:
            text_assembled_list.append(elem)
    return text_assembled_list

def get_ocr_only_text_result(result):
    result_str = ''
    ocr_result_list = result['roi_text']
    for ocr_object in ocr_result_list:
        if result_str != '':
            result_str += ' '
        result_str += ocr_object['text']
    return result_str
