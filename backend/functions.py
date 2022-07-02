from pydatafront.decorator import textea_export


@textea_export(path='calc', type={
    'whitelist': ['add', 'minus']
})
def calc(a: int, b: int, type: str):
    if type == 'add':
        return a + b
    elif type == 'minus':
        return a - b
    else:
        raise 'invalid parameter type'


@textea_export(path='calc_add')
def calc_add(a: int, b: int):
    return calc(a, b, 'add')


@textea_export(path='test', username={
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
