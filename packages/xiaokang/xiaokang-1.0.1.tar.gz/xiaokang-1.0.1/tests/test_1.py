from xiaokang.常用 import 报错信息, xk


def test_报错信息():
    try:
        print('1'+1)
    except:
        print(报错信息('json'))


def test_xk():
    xk()


test_报错信息()
