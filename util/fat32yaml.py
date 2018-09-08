from ruamel.yaml import YAML

from util.commonYaml import yamlObject

yaml = YAML()

class fat32Yaml(yamlObject):
    yaml_tag = u'!fat32Yaml'

    # @classmethod
    # def from_yaml(cls, loader, node):
    #     mapping =yaml.map()
    #     values = loader.construct_mapping(node, maptyp=mapping)
    #     result = {}
    #
    #     return cls(**result)



