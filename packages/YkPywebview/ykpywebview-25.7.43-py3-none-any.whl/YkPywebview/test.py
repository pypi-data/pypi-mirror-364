from core import YkWebviewApi, start, CombinedApi
import inspect


class Api1(YkWebviewApi):
    def __init__(self) -> None:
        super().__init__()

    def greet1(self, msg):
        print(f"111: {msg}")


class Api2(YkWebviewApi):
    def __init__(self) -> None:
        super().__init__()

    def greet2(self, msg):
        print(f"222: {msg}")

api = CombinedApi([Api1, Api2])
api.greet1("hello 1")
api.greet2("hello 2")
print(api.__dir__())

method = api.greet1
print(type(method))  # <class 'method'>
print(inspect.ismethod(method))  # 输出: True
# start([Api1, Api2], 'http://127.0.0.1:8080/', debug=True)
