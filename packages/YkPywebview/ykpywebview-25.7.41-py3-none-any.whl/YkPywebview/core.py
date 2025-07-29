import webview
import os
import pickle
import toml
import json

_initialized = False
window = None  # 全局 window 变量，所有模块共享


def deep_merge(d1, d2):
    """
    深度合并两个字典，d2 会覆盖 d1 的相同 key（递归）
    """
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            deep_merge(d1[key], d2[key])
        else:
            d1[key] = d2[key]
    return d1


class CombinedApi:
    def __init__(self, api_list: list):
        """
        要让方法在pywebview中暴露给js，主要是要使方法通过inspect.ismethod(method)校验，必须是实例的bound method才行，这里试了多种方法，
        目前这种是唯一可行的。functools.partial()方法是不行的，类的静态方法和类方法都是不行的，必须是常规的method(self, args)方法才行。
        """
        self.api_list = api_list
        self.instances = {}

    def __getattr__(self, name):
        for api in self.api_list:
            if hasattr(api, name):
                # 只有在第一次调用时才创建实例
                if api not in self.instances:
                    self.instances[api] = api()
                instance = self.instances[api]
                method = getattr(instance, name)
                return method  # 直接返回方法，Python 会自动绑定 self
        raise AttributeError(f"'{name}' not found in any of the APIs")

    def __dir__(self):
        result = []
        for api in self.api_list:
            for name in dir(api):
                if name not in result:
                    result.append(name)
        return result


class YkWebviewApi:
    def __init__(self) -> None:
        self.mute = False
        self.user_file = 'user.pkl'
        self.window_settings_key = 'window_settings'
        self.settings = self.loadProjectSettings()

    def setWindow(self):
        pass

    @property
    def window(self):
        return window

    def printToTerm(self, msg: str, kind='info'):
        """
        打印日志到终端

        :param msg: 输出的消息。
        :param kind: 可取值warning info success error system
        :return:
        """
        if self.mute:
            return
        if isinstance(self.window, webview.Window):
            # 使用JSON序列化来安全转义所有特殊字符
            escaped_msg = json.dumps(msg)[1:-1]  # 去掉外层的引号
            cmd = f'window.printToTerm("{escaped_msg}", "{kind}")'
            self.window.evaluate_js(cmd, callback=None)
        else:
            print(f'window不可用, {self.window=}')

    def setTaskBar(self, title: str, progress: int = 0):
        """
        设置任务栏图标和进度条

        :param title: 任务栏标题
        :param progress: 任务栏进度
        """
        if isinstance(self.window, webview.Window):
            escaped_title = json.dumps(title)[1:-1]  # 使用JSON转义并去掉外层引号
            cmd = f'window.setTaskBar("{escaped_title}", {progress})'
            self.window.evaluate_js(cmd, callback=None)
        else:
            print(f'window不可用, {self.window=}')

    def openTerminal(self):
        """
        对应前端App.vue中的openDrawer方法
        用于打开终端抽屉
        """
        self.window.evaluate_js("window.openDrawer()")

    def saveLoginInfo(self, userInfo: dict):
        """
        保存登录信息到本地user.pkl文件

        :param userInfo: 用户信息字典，包含username和password
        """
        try:
            with open(self.user_file, 'wb') as f:
                pickle.dump(userInfo, f)
            return True
        except Exception as e:
            print(f"保存登录信息失败: {e}")
            return False

    def getLoginInfo(self):
        """
        获取登录信息，读取本地文件user.pkl保存的username和password

        :return: 用户名和密码
        """
        if not os.path.exists(self.user_file):
            return None

        try:
            with open(self.user_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"读取登录信息失败: {e}")
            return None

    def toggle_fullscreen(self):
        """
        全屏
        """
        if isinstance(self.window, webview.Window):
            self.window.toggle_fullscreen()
            from webview import localization
        else:
            print(f'window不可用, {self.window=}')

    def loadAppSettings(self):
        """
        加载调用项目的settings.app.toml文件

        :return: 返回解析后的TOML对象，如果文件不存在或解析失败则返回None
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.app.toml')

            if not os.path.exists(settings_path):
                print(f"配置文件不存在: {settings_path}")
                return {}

            with open(settings_path, 'r', encoding='utf-8') as f:
                return toml.load(f)

        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def loadProjectSettings(self):
        """
        加载调用项目的settings.project.toml文件

        :return: 返回解析后的TOML对象，如果文件不存在则返回空字典，解析失败返回None
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.project.toml')

            if not os.path.exists(settings_path):
                print(f"项目配置文件不存在: {settings_path}")
                return {}

            with open(settings_path, 'r', encoding='utf-8') as f:
                self.settings = toml.load(f)
                return self.settings

        except Exception as e:
            print(f"加载项目配置文件失败: {e}")
            return None

    def saveAppSettings(self, settings: dict):
        """
        保存配置到调用项目的settings.app.toml文件

        :param settings: 要保存的配置字典
        :return: 成功返回True，失败返回False
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.app.toml')

            # 确保目录存在
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)

            with open(settings_path, 'w', encoding='utf-8') as f:
                toml.dump(settings, f)
            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def saveProjectSettings(self, settings: dict):
        """
        保存配置到调用项目的settings.project.toml文件

        :param settings: 要保存的配置字典
        :return: 成功返回True，失败返回False
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.project.toml')

            # 确保目录存在
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)

            # 深度合并传入的 settings 到 self.settings
            self.settings = deep_merge(self.settings.copy(), settings)

            with open(settings_path, 'w', encoding='utf-8') as f:
                toml.dump(self.settings, f)
            return True

        except Exception as e:
            print(f"保存项目配置文件失败: {e}")
            return False

    def setProjectSettings(self, settings: dict):
        return self.saveProjectSettings(settings)

    def setAppSettings(self, settings: dict):
        return self.saveAppSettings(settings)

    def getProjectSettings(self):
        return self.loadProjectSettings()

    def getAppSettings(self):
        return self.loadAppSettings()

    def get_window_geometry(self):
        """
        获取当前窗口的位置和大小信息
        返回格式: {'x': x坐标, 'y': y坐标, 'width': 宽度, 'height': 高度}
        注意: 
        - 仅在window对象有效时返回数据
        - 如果window不可用则返回None
        """
        if isinstance(self.window, webview.Window):
            return {
                'x': self.window.x,  # 窗口左上角的x坐标(像素)
                'y': self.window.y,  # 窗口左上角的y坐标(像素)
                'width': self.window.width,  # 窗口宽度(像素)
                'height': self.window.height  # 窗口高度(像素)
            }
        return None

    def save_window_geometry(self):
        """
        保存当前窗口位置和大小到settings.app.toml配置文件
        执行流程:
        1. 先获取当前窗口几何信息
        2. 加载现有应用设置
        3. 将窗口信息合并到设置中
        4. 保存更新后的设置
        返回值: 
        - 成功保存返回True
        - 失败或window不可用时返回False
        """
        geometry = self.get_window_geometry()
        if geometry:
            settings = self.loadAppSettings()  # 加载现有设置
            settings[self.window_settings_key] = geometry  # 添加/更新窗口设置
            return self.saveAppSettings(settings)  # 保存设置
        return False

    def load_window_geometry(self):
        """
        从settings.app.toml加载保存的窗口位置和大小
        返回值:
        - 成功返回包含窗口几何信息的字典
        - 如果设置不存在或无效则返回None
        注意: 该方法不会自动应用设置，需要调用方处理返回值
        """
        settings = self.loadAppSettings()
        return settings.get(self.window_settings_key)  # 获取窗口设置或None


def start(Api, url: str, ssl=True, debug=False, localization=None, title='gf-ui', width=900, height=620,
          text_select=True, confirm_close=True):
    """
    启动webview窗口的主函数

    新增功能说明:
    - 启动时会尝试加载上次保存的窗口位置和大小
    - 窗口关闭时会自动保存当前窗口位置和大小

    参数说明:
    :param Api: 必须实现的API类，可以实现多个，这里传入实现的类的列表，则前端可以调用多个类中的方法，每个类中方法相互独立，如有重名方法，则优先调用列表中靠前的类的方法
    :param url: 要加载的URL地址
    :param ssl: 是否启用SSL验证(默认True)
    :param debug: 是否启用调试模式(默认False)
    :param localization: 本地化字典(默认提供中文)
    :param title: 窗口标题(默认'gf-ui')
    :param width: 默认宽度(900像素)
    :param height: 默认高度(620像素)
    :param text_select: 是否允许文本选择(默认True)
    :param confirm_close: 关闭时是否需要确认(默认True)
    """
    global window
    if localization is None:
        localization = {
            'global.quitConfirmation': u'确定关闭?',
            'global.ok': '确定',
            'global.quit': '退出',
            'global.cancel': '取消',
            'global.saveFile': '保存文件',
            'windows.fileFilter.allFiles': '所有文件',
            'windows.fileFilter.otherFiles': '其他文件类型',
            'linux.openFile': '打开文件',
            'linux.openFiles': '打开文件',
            'linux.openFolder': '打开文件夹',
        }

    if isinstance(Api, list):
        api = CombinedApi(Api)
    else:
        api = Api()

    # 加载保存的窗口设置(如果存在)
    saved_geometry = api.load_window_geometry()
    if saved_geometry:  # 如果存在保存的设置
        x = saved_geometry.get('x', 0)  # 获取保存的x坐标
        y = saved_geometry.get('y', 0)  # 获取保存的y坐标
        width = saved_geometry.get('width', width)  # 获取保存的宽度(使用默认值作为后备)
        height = saved_geometry.get('height', height)  # 获取保存的高度(使用默认值作为后备)
    else:
        x = y = 0

    window = webview.create_window(
        title=title,
        url=url,
        x=x if 'x' in locals() else None,
        y=y if 'y' in locals() else None,
        width=width,
        height=height,
        resizable=True,
        text_select=text_select,
        confirm_close=confirm_close,
        js_api=api,
        min_size=(900, 620)
    )

    # 设置窗口关闭时的回调函数

    def before_close():
        """
        窗口关闭事件回调函数
        功能: 在窗口关闭前保存当前窗口位置和大小
        """
        print("窗口关闭")
        try:
            api.save_window_geometry()
        except Exception as e:
            print(f"保存窗口几何信息失败: {e}")

        # 延迟清理临时文件
        import time
        time.sleep(0.1)  # 等待1秒让资源释放

    window.events.closing += before_close  # 注册关闭事件回调

    # 启动窗口
    webview.start(localization=localization, ssl=ssl,
                  debug=debug)  # 该语句会阻塞，直到程序关闭后才会继续执行后续代码
