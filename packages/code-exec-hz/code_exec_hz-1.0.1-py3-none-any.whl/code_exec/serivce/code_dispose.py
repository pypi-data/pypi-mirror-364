from code_exec.model.model import LanguageType

def dispose(language: str, inputs: dict, code: str):
    ret = {}
    if language == LanguageType.PYTHON:
        ret = dispose_python(inputs, code)
    return ret


def dispose_python(inputs: dict, code: str):
    # exec_context = {}
    exec(code, inputs)
    print(f"result: {inputs['result']}")
    return inputs['result']