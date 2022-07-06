from pydatafront.decorator import textea_export


@textea_export(path='calc', config=['type'], input=['a', 'b'], type={
    'whitelist': ['add', 'minus']
})
def calc(a: int, b: int, type: str):
    if type == 'add':
        return a + b
    elif type == 'minus':
        return a - b
    else:
        raise 'invalid parameter type'


@textea_export(path='calc_add', config=[], input=['a', 'b'])
def calc_add(a: int, b: int):
    return calc(a, b, 'add')


@textea_export(path='test', config=['username', 'pi', 'd', 'arr'], input=[], username={
    'whitelist': ['turx']
}, pi={
    'example': [3.1415926535]
}, arr={
    'example': [
        [1, 2, 3],
        [4, 5, 6]
    ]
})
def test(username: str, pi: float, d: dict, arr: list):
    s = ''
    s += ('{}, {}\n').format(username, type(username))
    s += ('{}, {}\n').format(pi, type(pi))
    s += ('{}, {}\n').format(d, type(d))
    s += ('{}, {}\n').format(arr, type(arr))
    return s
