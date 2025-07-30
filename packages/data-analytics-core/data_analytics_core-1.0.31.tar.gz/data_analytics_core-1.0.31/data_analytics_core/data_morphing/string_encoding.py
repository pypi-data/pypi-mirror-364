import json
import base64
import pandas as pd
from typing import Union, List, Dict, Literal


def encode_df_json_to_string(data: Union[pd.DataFrame, Dict, List], save_index: bool = False) -> str:
    if isinstance(data, pd.DataFrame):
        if save_index:
            orient = 'tight'
        else:
            orient = 'list'
        data = data.to_dict(orient=orient)
    return base64.b64encode(json.dumps(data).encode('utf-8')).decode("utf-8")


def decode_string_to_df_json(data: str, output: Literal['df', 'json'] = 'df') -> Union[pd.DataFrame, Dict, List]:
    '''
    output: 'df' or 'json'
    '''
    data_decoded = json.loads(base64.b64decode(data))
    if output == 'df':
        orient = 'tight' if 'index' in data_decoded else 'columns'
        return pd.DataFrame.from_dict(data_decoded, orient=orient)
    elif output == 'json':
        return data_decoded
    else:
        raise ValueError("output must be 'df' or 'json'")
