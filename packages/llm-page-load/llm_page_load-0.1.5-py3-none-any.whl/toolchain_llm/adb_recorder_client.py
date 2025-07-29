import subprocess
import threading
import time
import logging
import base64
import socketio

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AndroidScreenRecorder:
    def __init__(self, server_url, device_id=None, frame_rate=1, bit_rate="1M", peer_sid=''):
        """
        初始化录屏器

        Args:
            server_url: Socket.IO服务器URL
            device_id: 安卓设备ID，如果为None则使用默认连接的设备
            frame_rate: 录屏帧率
            bit_rate: 录屏比特率
        """
        self.server_url = server_url
        self.device_id = device_id
        self.frame_rate = frame_rate
        self.bit_rate = bit_rate
        self.running = False
        self.sio = None
        self.peer_sid = peer_sid

    def _get_adb_prefix(self):
        """返回带设备ID的ADB命令前缀"""
        if self.device_id:
            return ["adb", "-s", self.device_id]
        return ["adb"]

    def _check_device_connected(self):
        """检查设备是否已连接"""
        try:
            cmd = self._get_adb_prefix() + ["devices"]
            result = subprocess.check_output(cmd).decode('utf-8')
            if "device" not in result or result.count("\n") <= 1:
                logger.error("没有找到已连接的安卓设备")
                return False
            return True
        except Exception as e:
            logger.error(f"检查设备连接时出错: {e}")
            return False

    def _connect_socketio(self):
        """连接到Socket.IO服务器"""
        try:
            self.sio = socketio.Client(reconnection=True,
                                       reconnection_attempts=0,
                                       reconnection_delay=1,
                                       logger=logger,
                                       reconnection_delay_max=5)

            @self.sio.event(namespace='/hyperjump/copilot/driver')
            def connect():
                logger.info("已连接到服务器")
                # 注册为屏幕源
                self.sio.emit(
                    'register', {'type': 'screen_source'}, namespace='/hyperjump/copilot/driver')

            @self.sio.event(namespace='/hyperjump/copilot/driver')
            def connect_error(data):
                logger.error(f"连接错误: {data}")

            @self.sio.event(namespace='/hyperjump/copilot/driver')
            def disconnect():
                logger.info("已断开连接")

            def on_action(content):
                logger.info(f'收到事件 action: {content}')
                if content == 'stop':
                    self.stop_recording()
                elif content['event_name'] == 'screenshot':
                    self.sio.emit('action', 'http://msstest.sankuai.com/v1/mss_29bc475beb7e4563a9a6f802f29acd83/compatibility/resource/449749actionimg.png',
                                  namespace='/hyperjump/copilot/driver')
                elif content['event_name'] == 'get_xml':
                    self.sio.emit('action', 'http://msstest.sankuai.com/v1/mss_29bc475beb7e4563a9a6f802f29acd83/compatibility/resource/977474actionxml.xml',
                                  namespace='/hyperjump/copilot/driver')
                elif content['event_name'] == 'get_device_size':
                    self.sio.emit('action', "[1080, 2340]", namespace='/hyperjump/copilot/driver')
                else:
                    self.sio.emit('action', 'done', namespace='/hyperjump/copilot/driver')

            self.sio.on('action', on_action, namespace='/hyperjump/copilot/driver')

            # 连接到服务器
            self.sio.connect(self.server_url, namespaces=['/hyperjump/copilot/driver'])
            self.sio.emit('message', {'event_name': 'peer', 'event_data': self.peer_sid, 'direction': 'Device2Server'},
                          namespace='/hyperjump/copilot/driver')
            return True
        except Exception as e:
            logger.error(f"连接Socket.IO服务器时出错: {e}")
            return False

    def start_recording(self):
        """开始录屏并发送数据"""
        if not self._check_device_connected():
            return False

        if not self._connect_socketio():
            return False

        self.running = True
        recording_thread = threading.Thread(target=self._recording_loop)
        recording_thread.daemon = True
        recording_thread.start()

        # logger.info("开始录屏并发送数据")
        return True

    def _recording_loop(self):
        """录屏主循环"""
        try:
            # 使用 screenrecord 命令获取视频流
            cmd = self._get_adb_prefix() + [
                "shell",
                "screenrecord",
                "--output-format=h264",
                f"--bit-rate={self.bit_rate}",
                "--size=380x720",
                "--time-limit=180",
                "-"
            ]

            # 使用 FFmpeg 将视频流转换为图片
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", "pipe:0",         # 视频输入
                "-f", "image2pipe",     # 输出为图片管道
                "-pix_fmt", "rgb24",    # 像素格式
                "-vcodec", "png",       # PNG 格式
                "-r", str(self.frame_rate),  # 输出帧率
                "pipe:1"                # 输出到管道
            ]

            while self.running:
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ffmpeg_process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdin=process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.stdout.close()

                # 读取 PNG 图片数据的魔数
                PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
                buffer = bytearray()

                while self.running:
                    chunk = ffmpeg_process.stdout.read(512)
                    if not chunk:
                        break

                    buffer.extend(chunk)

                    # 查找并发送完整的 PNG 图片
                    while True:
                        magic_index = buffer.find(PNG_MAGIC)
                        if magic_index == -1:
                            break

                        # 查找下一个 PNG 头以确定当前图片的结束位置
                        next_magic_index = buffer.find(
                            PNG_MAGIC, magic_index + 8)
                        if next_magic_index == -1:
                            # 如果没找到下一个 PNG 头，可能数据还不完整
                            if len(buffer) - magic_index > 1024 * 1024:  # 安全检查
                                buffer = buffer[magic_index + 8:]  # 丢弃可能损坏的数据
                            break

                        # 提取完整的 PNG 图片
                        image_data = buffer[magic_index:next_magic_index]
                        buffer = buffer[next_magic_index:]  # 更新缓冲区

                        if not self.sio or not self.sio.connected:
                            logger.error("Socket.IO 未连接")
                            break

                        try:
                            self.sio.emit('screenrecord', {
                                'type': 'image/png',
                                'data': base64.b64encode(image_data).decode('utf-8')
                            }, namespace='/hyperjump/copilot/driver')
                            logger.info('emit已发送,screenrecord')
                        except Exception as e:
                            logger.error(f"发送数据失败: {e}")
                            break

                # 清理进程
                ffmpeg_process.terminate()
                process.terminate()
                try:
                    ffmpeg_process.wait(timeout=5)
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ffmpeg_process.kill()
                    process.kill()

        except Exception as e:
            logger.error(f"录屏过程中出错: {e}")
        finally:
            self.stop_recording()

    def stop_recording(self):
        """停止录屏"""
        self.running = False
        if self.sio:
            self.sio.disconnect()
            self.sio = None
        logger.info("录屏已停止")


# 使用示例
if __name__ == "__main__":
    # Socket.IO服务器地址
    server_url = "http://11.45.13.238:8002"
    peer_sid = 'zsSqejLvJlsJ8NdWAAAB'

    recorder = AndroidScreenRecorder(server_url, peer_sid=peer_sid)

    try:
        if recorder.start_recording():
            # 持续运行直到手动中断
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("用户中断录制")
    finally:
        recorder.stop_recording()
