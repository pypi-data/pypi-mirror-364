"""
YAML utilities for Prompt Gear using ruamel.yaml.
Provides consistent YAML formatting with block scalars for prompts.
"""
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from io import StringIO
from typing import Dict, Any, Union


def create_yaml_instance() -> YAML:
    """Create a configured YAML instance for Prompt Gear."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096  # Prevent line wrapping
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.default_flow_style = False
    return yaml


def prepare_prompt_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare prompt data for YAML serialization with proper formatting.
    
    Converts system_prompt and user_prompt to literal block scalars (|)
    for better readability and editing.
    """
    prepared_data = data.copy()
    
    # Convert prompts to literal scalar strings for | formatting
    if 'system_prompt' in prepared_data and prepared_data['system_prompt']:
        prepared_data['system_prompt'] = LiteralScalarString(prepared_data['system_prompt'])
    
    if 'user_prompt' in prepared_data and prepared_data['user_prompt']:
        prepared_data['user_prompt'] = LiteralScalarString(prepared_data['user_prompt'])
    
    return prepared_data


def dump_yaml(data: Dict[str, Any]) -> str:
    """
    Dump data to YAML string with proper formatting for prompts.
    """
    yaml = create_yaml_instance()
    prepared_data = prepare_prompt_data(data)
    
    stream = StringIO()
    yaml.dump(prepared_data, stream)
    return stream.getvalue()


def dump_yaml_to_file(data: Dict[str, Any], filepath: Union[str, Any]) -> None:
    """
    Dump data to YAML file with proper formatting for prompts.
    """
    yaml = create_yaml_instance()
    prepared_data = prepare_prompt_data(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(prepared_data, f)


def load_yaml(content: str) -> Dict[str, Any]:
    """
    Load YAML content from string.
    """
    yaml = create_yaml_instance()
    return yaml.load(content)


def load_yaml_from_file(filepath: Union[str, Any]) -> Dict[str, Any]:
    """
    Load YAML content from file.
    """
    yaml = create_yaml_instance()
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.load(f)
