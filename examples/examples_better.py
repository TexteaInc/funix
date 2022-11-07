from pydatafront.decorator import funix_export


@funix_export(
    widgets={
        "switch": ["arg1"]
    },
    treat_as={
        "column": ["arg2"],
    },
    whitelist={
        "arg2": ["a", "b", "c"]
    }
)
def elegant(arg1: bool, arg2: str):
    return {
        "arg1": arg1,
        "arg2": arg2
    }
