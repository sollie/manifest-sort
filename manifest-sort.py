import sys
import yaml
from collections import OrderedDict


def sort_yaml_keys(data, key_to_move_last=None):
    """ Recursively sorts YAML keys, moving a specific key to the end if
    provided. """
    if isinstance(data, dict):
        sorted_keys = sorted(k for k in data.keys() if k != key_to_move_last)
        if key_to_move_last in data:
            sorted_keys.append(key_to_move_last)
        return OrderedDict((k, sort_yaml_keys(data[k], key_to_move_last))
                           for k in sorted_keys)
    elif isinstance(data, list):
        return [sort_yaml_keys(v, key_to_move_last) for v in data]
    else:
        return data


if len(sys.argv) != 2:
    print("Usage: python script.py <input_yaml_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, 'r') as file:
        data = yaml.safe_load(file)

    sorted_data = sort_yaml_keys(data, key_to_move_last="env")

    def ordered_dict_representer(dumper, data):
        return dumper.represent_dict(data.items())

    yaml.add_representer(OrderedDict, ordered_dict_representer)

    original_yaml = yaml.dump(data, sort_keys=False, default_flow_style=False)
    sorted_yaml = yaml.dump(sorted_data, sort_keys=False,
                            default_flow_style=False)

    if original_yaml != sorted_yaml:
        with open(input_file, 'w') as file:
            file.write(sorted_yaml)
        print(f"File '{input_file}' has been modified.")
        sys.exit(1)
    else:
        print("No changes needed in the file.")
        sys.exit(0)

except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"Error: Failed to parse YAML file. {e}")
    sys.exit(1)
