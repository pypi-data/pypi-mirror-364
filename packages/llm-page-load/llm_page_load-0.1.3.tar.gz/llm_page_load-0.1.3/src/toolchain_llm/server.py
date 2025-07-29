import json
from flask import Flask, g, request
from flask import jsonify
import time
from flask_cors import CORS
from api.conversation import conversation
from api.impact_analysis import impact_analysis
from api.scenetivity_server import scentivity
import api.coe_service as coe_server
from api.components.limiter import limiter
import api.campaign_analysis_server as campaigin_server
from api.es_service import es_service
from api.by_pass import bypass
from api.app_traversal import app_traversal_service
from api.feature_api import feature_api
from api.me_translation import me_translation
from api.ui_detection import ui_detection
from api.gpt_stream import gpt_stream
from api.urlscheme_query_classification import urlscheme_query_classification_service
from api.auitest import auitest
from api.case_generation import auto_case_generate
from api.trace_compare import trace_compare_service
import traceback
from flask_socketio import SocketIO
from socket_dispatcher import CampaignActivityDispatcher, CoeChatDispatcher
from socket_dispatcher.chat_socket_dispatcher import ChatSocketDispatcher
from socket_dispatcher.driver_socket_dispatcher import DriverSocketDispatcher
from socket_dispatcher.case_generate_socket_dispatcher import CaseGenerateSocketDispatcher
from utils import appkey, logger  # noqa
from pycat import Cat, DefaultTransaction  # 接入 raptor
from service.aui_test_agent.hyperjump_copilot.utils.ui_case_api import LyrebirdClient



app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = appkey
Cat.init_cat(appkey, disable_falcon=True)

limiter.init_app(app)

CORS(app, resources=r'/*', supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading', logger=False,
                    engineio_logger=False, ping_interval=45, ping_timeout=20)

app.register_blueprint(conversation, url_prefix='/conversation')
app.register_blueprint(impact_analysis, url_prefix='/impact-analysis')
app.register_blueprint(me_translation, url_prefix='/me')
app.register_blueprint(ui_detection, url_prefix='/ui_detection')
app.register_blueprint(gpt_stream, url_prefix='/gpt_stream')
app.register_blueprint(feature_api, url_prefix='/feature_api')
app.register_blueprint(scentivity, url_prefix='/scenetivity')
app.register_blueprint(coe_server.coe, url_prefix=coe_server.NameSpace)
app.register_blueprint(campaigin_server.campaign,
                       url_prefix=campaigin_server.NameSpace)
app.register_blueprint(es_service, url_prefix='/es_service')
app.register_blueprint(app_traversal_service, url_prefix='/app_traversal_service')
app.register_blueprint(bypass, url_prefix='/bypass')
app.register_blueprint(urlscheme_query_classification_service, url_prefix='/urlscheme_query_classification')
app.register_blueprint(auitest, url_prefix='/auitest')
app.register_blueprint(auto_case_generate, url_prefix='/case_generate')
app.register_blueprint(trace_compare_service, url_prefix='/trace_compare')

CampaignActivityDispatcher.bind_socket(socket=socketio,
                                       namespace=campaigin_server.NameSpace)

CoeChatDispatcher.bind_socket(socket=socketio, namespace=coe_server.NameSpace)
ChatSocketDispatcher.bind_socket(socket=socketio, namespace='/hyperjump/copilot/chat')
DriverSocketDispatcher.bind_socket(socket=socketio, namespace='/hyperjump/copilot/driver')
CaseGenerateSocketDispatcher.bind_socket(socket=socketio,namespace='/hyperjump/copilot/case_generate')



@app.errorhandler(Exception)
def error(e):
    ret = dict()
    ret["code"] = 1
    ret["error"] = repr(e)
    ret["msg"] = traceback.format_exc()
    ret["message"] = ret["msg"]
    ret['data'] = None
    return jsonify(ret)


@app.before_request
def cat_transaction_begin():
    g.url_transaction = Cat.new_transaction("RESTFUL_" + request.method, request.path)
    try:
        data = {
            'url': request.full_path,
            'method': request.method,
            'args': {k: v for k, v in request.args.items()},
            'body': request.get_data(as_text=True)
        }
        time_stamp = time.time()
        now = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_stamp))
        e = Cat.new_event(request.path, now)
        e.can_be_aggregated = False
        e.add_data(json.dumps(data, ensure_ascii=False, indent=2))
        e.complete()
    except Exception as e:
        Cat.log_error("RESTFUL_" + request.method, repr(e))


@app.after_request
def cat_transaction_complete(response):
    if g.url_transaction and isinstance(g.url_transaction, DefaultTransaction):
        g.url_transaction.complete()
    return response


@app.route('/hypejump/copilot/attach_device')
def _hyc_attach():
    from adb_recorder_client import AndroidScreenRecorder
    server_url = 'http://' + request.args.get('host') + ':' + request.args.get('port')
    peer_sid = request.args.get('peer_sid')
    recorder = AndroidScreenRecorder(server_url=server_url, peer_sid=peer_sid)
    ret = recorder.start_recording()
    return jsonify({'success': ret})


if __name__ == '__main__':
    # LyrebirdClient.start_background_service(direction='dzu')
    socketio.run(app, host="0.0.0.0", port=8002, debug=True)
    
    # app.run(host="0.0.0.0", port=8002)
