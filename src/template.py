from typing import Union, List, Dict


def ret_content_template(code: int, message: str, data: Union[List, Dict]):
    return {
        "code": code,
        "message": message,
        "data": data
   }