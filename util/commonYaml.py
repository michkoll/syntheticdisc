from copy import deepcopy

from ruamel.yaml import YAML, yaml_object, YAMLObject, SafeLoader

yaml = YAML()

@yaml_object(yaml)
class yamlObject(YAMLObject):
    yaml_tag = u'!yamlObject'

    def __init__(self):
        pass

    @classmethod
    def to_yaml(cls, dumper, data):
        newdata = deepcopy(data)
        for item in dir(newdata):
            if item.startswith("_") and not item.startswith("__") and item in newdata.__dict__:
                del newdata.__dict__[item]
        return dumper.represent_yaml_object(cls.yaml_tag, newdata, cls,
                                            #flow_style=cls.yaml_flow_style
                                            )

