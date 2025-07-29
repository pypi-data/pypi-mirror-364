from flask import jsonify
from flask import request
from flask import Blueprint
from scenetivity import replace, map
from utils import logger
from lxml.html.clean import clean_html


scentivity = Blueprint('scenetivity', __name__)


@scentivity.route('/replace', methods=['POST'])
def replace_text():
    """
    payload = {
        'text':<待脱敏文本>,
        'level':<脱敏等级>=1 (optional)
    }
    return = {
        'text':<脱敏后的文本>
        'code':1
    }
    """
    logger.info(f'[scenetivity/replace] request={request.json}')
    payload = request.json
    text = payload.get('text')
    level = int(payload.get('level', 1))
    if text is None:
        logger.warn('[scenetivity/replace] warn = please provide text')
        return jsonify({"code": 400, "message": "please provide text"})
    text = replace(text, level)
    # 防止xss攻击
    text = clean_html(text)
    logger.info(f'[scenetivity/replace] output = {text}')
    return jsonify({'code': 1, 'text': text})


@scentivity.route('/map', methods=['GET'])
def get_replace_map():
    logger.info('[scenetivity/map]')
    return jsonify({'code': 1, 'map': map()})
