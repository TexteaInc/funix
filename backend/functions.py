from pydatafront.decorator import textea_export

@textea_export(
    path='calc',
    type={
        'whitelist': ['add', 'minus'],
        'treat_as': 'config'
    },
    a={
       'treat_as' : 'column'
    },
    b={
       'treat_as' : 'column'
    }
)
def calc(a: int, b: int, type: str) -> int:
    if type == 'add':
        return a + b
    elif type == 'minus':
        return a - b
    else:
        raise 'invalid parameter type'


@textea_export(
    path='calc_add',
    a={
        'treat_as' : 'column'
    },
    b={
        'treat_as' : 'column'
    }
)
def calc_add(a: int, b: int) -> int:
    return calc(a, b, 'add')


@textea_export(
    path='test',
    username={
        'treat_as' : 'config',
        'whitelist': ['turx']
    },
    pi={
        'treat_as' : 'config',
        'example': [3.1415926535]
    },
    arr={
        'example':
            [[1, 2, 3],
            [4, 5, 6]],
        'treat_as' : 'config'
    },
    d={
        'treat_as' : 'config'
    }
)
def test(username: str, pi: float, d: dict, arr: list) -> str:
    s = ''
    s += ('{}, {}\n').format(username, type(username))
    s += ('{}, {}\n').format(pi, type(pi))
    s += ('{}, {}\n').format(d, type(d))
    s += ('{}, {}\n').format(arr, type(arr))
    return s

@textea_export(
    path='owo',
    a={
        'treat_as': 'column'
    },
    b={
        'treat_as' : 'column'
    },
    output_dict={
        'add': int,
        'sub': int,
    }
)
def add_with_sub(a: int, b: int) -> dict:
    return {
        'add': a + b,
        'sub': a - b
    }