from typing import Union

from ruyaml.comments import TaggedScalar


def transform_yaml_to_dict(yaml_str) -> Union[dict, list]:
    if isinstance(yaml_str, dict):
        return {k: transform_yaml_to_dict(v) for k, v in yaml_str.items()}
    if isinstance(yaml_str, list):
        return [transform_yaml_to_dict(elem) for elem in yaml_str]
    if isinstance(yaml_str, TaggedScalar):
        return transform_yaml_to_dict(yaml_str.value)
    return yaml_str