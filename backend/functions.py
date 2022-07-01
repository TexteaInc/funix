from pydatafront.decorator import textea_export
from pydatafront.type import Output, Input


@textea_export(
    path='calc',
    description="""
    Hello, world!
    """,
    name="My Calc",
    inputs={
        'a': int,
        'b': int,
        'type': ['add', 'minus']
    },
    outputs={
        'a': int,
        'b': int,
        'ans': int
    }
)
def calc(inputs: Input, outputs: Output):
    if inputs.type == 'add':
        outputs.set({"a": inputs.a, "b": inputs.b, "ans": inputs.a + inputs.b})
    elif inputs.type == 'minus':
        outputs.set({"a": inputs.a, "b": inputs.b, "ans": inputs.a - inputs.b})
    else:
        raise 'invalid parameter type'


@textea_export(path='test',
               description="just a test",
               name="MyTest",
               inputs={
                   "username": ['turx'],
                   "pi": {
                       "$type": float,
                       "default": 3.1415926535
                   },
                   "d": dict,
                   "arr": {
                       "$type": list,
                       "default": [
                           [1, 2, 3],
                           [4, 5, 6]
                       ]
                   }
               },
               outputs=str
               )
def test(inputs: Input, outputs: Output):
    s = ''
    s += '{}, {}\n'.format(inputs.username, type(inputs.username))
    s += '{}, {}\n'.format(inputs.pi, type(inputs.pi))
    s += '{}, {}\n'.format(inputs.d, type(inputs.d))
    s += '{}, {}\n'.format(inputs.arr, type(inputs.arr))
    outputs.set(s)

