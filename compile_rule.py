import argparse
import logging
import os

import yaml

TEMPLATES_DIR = "generic"
RULES_DIR = f"{TEMPLATES_DIR}/rules"
SQL_DIR = f"{TEMPLATES_DIR}/sql"
COMPILED_DIR = "compiled"

ENVIRONMENTS_FILENAME = "environments.yaml"
RULE_DIMENSIONS_FILENAME = "rule_dimensions.yaml"
ROW_FILTERS_FILENAME = "row_filters.yaml"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, str_presenter)


def resolve_sql_code(yaml_data):
    for rule_name, rule_value in yaml_data['rules'].items():
        for param in ['custom_sql_statement', 'custom_sql_expr']:
            rule_params = rule_value.get('params', {})
            if param in rule_params:
                rule_path = rule_params.get(param, {})
                if ' ' not in rule_path:
                    sql_file = os.path.join(SQL_DIR, rule_path + '.sql')
                    if os.path.exists(sql_file):
                        log.info(f"Rule {rule_name} was resolved at {sql_file}")
                        with open(sql_file, 'r') as f:
                            sql_code = f.read()
                        yaml_data['rules'][rule_name]['params'][param] = sql_code.strip()
                    else:
                        log.warning(f"Rule {rule_name} was not resolved at {sql_file}")
                        raise FileNotFoundError
    return yaml_data


def get_environment_config(env_name):
    env_filename = f"{TEMPLATES_DIR}/{ENVIRONMENTS_FILENAME}"
    return load_generic_config(env_filename).get(env_name, {})


def load_generic_config(filename):
    with open(filename, 'r') as env_stream:
        try:
            env_data = yaml.safe_load(env_stream)
            log.info(f"Loaded {filename} configuration")
            return env_data
        except yaml.YAMLError as exc:
            log.error(f"Failed to load {filename} configuration")
            raise exc


def main(yaml_file, compiled_directory, environment):
    yaml_data = load_yaml(yaml_file)

    yaml_data = add_common_rules(yaml_data)
    yaml_data = set_environment(environment, yaml_data)
    yaml_data = set_dimensions(yaml_data)
    yaml_data = set_row_filters(yaml_data)

    output_yaml_filename = get_output_filename(compiled_directory, yaml_file, environment)
    os.makedirs(os.path.dirname(output_yaml_filename), exist_ok=True)
    with open(output_yaml_filename, 'w') as outfile:
        yaml.dump(yaml_data, outfile, default_flow_style=False)
        log.info(f"File {output_yaml_filename} created.")


def load_yaml(yaml_filename):
    with open(yaml_filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            log.error(f"Failed to load {yaml_filename}")
            raise exc


def set_environment(environment, yaml_data):
    if 'metadata_registry_defaults' not in yaml_data:
        yaml_data['metadata_registry_defaults'] = {}
    if 'dataplex' not in yaml_data['metadata_registry_defaults']:
        yaml_data['metadata_registry_defaults']['dataplex'] = {}
    env_config = get_environment_config(environment)
    yaml_data['metadata_registry_defaults']['dataplex'].update(env_config)
    return yaml_data


def add_common_rules(yaml_data):
    yaml_files = [file for file in os.listdir(RULES_DIR) if file.endswith(".yaml") or file.endswith(".yml")]
    log.info(f"Adding rules from {yaml_files}")
    for file in yaml_files:
        yaml_data = __add_property(f"{RULES_DIR}/{file}", yaml_data, 'rules')

    return resolve_sql_code(yaml_data)


def set_dimensions(yaml_data):
    filename = f"{TEMPLATES_DIR}/{RULE_DIMENSIONS_FILENAME}"
    return __add_property(filename, yaml_data, 'rule_dimensions')


def set_row_filters(yaml_data):
    filename = f"{TEMPLATES_DIR}/{ROW_FILTERS_FILENAME}"
    return __add_property(filename, yaml_data, 'row_filters')


def __add_property(filename, yaml_data, property_name):
    property_data = load_generic_config(filename).get(property_name, {})
    if property_name not in yaml_data:
        yaml_data[property_name] = {}
    if type(property_data) is list:
        yaml_data[property_name] = property_data
    else:
        yaml_data[property_name].update(property_data)
    return yaml_data


def get_output_filename(compiled_directory, yaml_file, environment):
    output_file = os.path.splitext(yaml_file)[0]
    output_yaml_file = f"{compiled_directory}/{output_file}-{environment}.yaml"
    return output_yaml_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile YAML file with external SQL.')
    parser.add_argument('yaml_file', type=str, help='Path to the YAML file at the templates directory')
    parser.add_argument('compiled_directory', type=str, default=COMPILED_DIR,
                        help='Directory where compiled YAML files are stored.')
    parser.add_argument('environment', type=str, help='Name of the environment to fetch configurations from.')

    args = parser.parse_args()
    main(args.yaml_file, args.compiled_directory, args.environment)
