import sys
import yaml
import subprocess
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


def get_staged_yaml_files():
    """ Returns a list of staged YAML files. """
    result = subprocess.run(
        ["git", "diff", "--name-only", "--cached"], capture_output=True,
        text=True)
    files = result.stdout.splitlines()
    return [f for f in files if f.endswith((".yml", ".yaml"))]


def process_file(file_path):
    """ Reads, sorts, and updates the file if needed. """
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        sorted_data = sort_yaml_keys(data, key_to_move_last="env")

        original_yaml = yaml.dump(
            data, sort_keys=False, default_flow_style=False)
        sorted_yaml = yaml.dump(
            sorted_data, sort_keys=False, default_flow_style=False)

        if original_yaml != sorted_yaml:
            with open(file_path, 'w') as file:
                file.write(sorted_yaml)
            return True  # File was modified

    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error processing '{file_path}': {e}")
        return False

    return False


if __name__ == "__main__":
    yaml_files = get_staged_yaml_files()

    if not yaml_files:
        sys.exit(0)  # No YAML files staged, exit with success

    modified = False

    for file in yaml_files:
        if process_file(file):
            modified = True

    if modified:
        print("Some YAML files were modified. Please stage the changes and " +
              "commit again.")
        sys.exit(1)
    else:
        sys.exit(0)  # No changes needed
