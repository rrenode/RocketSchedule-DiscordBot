from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import yaml
import datetime

load_dotenv()

FIELD_TYPE_CONVERTERS = {
    int: int,
    float: float,
    str: str,
    bool: lambda x: x.lower() in ('true', '1', 'yes'),
    datetime.datetime: lambda value: datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S"),
    Path: lambda value: Path(value)
}

def dev_config(cls):
    for key, field_type in cls.__annotations__.items():
        if str(key).startswith("__"):
            continue
        env_value = getenv(key)
        if env_value is not None and field_type in FIELD_TYPE_CONVERTERS:
            value = FIELD_TYPE_CONVERTERS[field_type](env_value)
            setattr(cls, key, value)
    return cls

@dev_config
class Paths:
    CONFIG_PATH: Path = Path("config.yaml")
    SECRETS_PATH: Path = Path(".secrets")
class DevConfig:
    VERBOSE_DEV: bool = False
    CONFIG_CONTROLLER_LOG: bool = False

def config(cls):
    try:
        config_path = Paths.CONFIG_PATH
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        if config_data is None:
            config_data = {}

        class_name = cls.__name__
        class_config = config_data.get(class_name, {})
        
        for key in vars(cls):
            if key in class_config:
                if str(key).startswith("__"):
                    continue
                value = class_config[key]
                field_type = getattr(cls, key)
                if field_type in FIELD_TYPE_CONVERTERS:
                    value = FIELD_TYPE_CONVERTERS[field_type](value)
                setattr(cls, key, value)
                if DevConfig.VERBOSE_DEV or DevConfig.CONFIG_CONTROLLER_LOG:
                    print(f"Set {cls.__name__}.{key} to {value}")
            elif not str(key).startswith("__"):
                if DevConfig.VERBOSE_DEV or DevConfig.CONFIG_CONTROLLER_LOG:
                    print(f"Using default value for {cls.__name__}.{key}: {getattr(cls, key)}")
                pass
            
    except FileNotFoundError:
        raise FileNotFoundError(f"The configuration file '{config_path}' was not found")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

    return cls

class Secrets:
    secrets_data = None
    
    @staticmethod
    def load_secrets():
        secrets_path = Paths.SECRETS_PATH
        config_path = Paths.CONFIG_PATH
        if secrets_path == config_path:
            raise ValueError("SECRETS_PATH and CONFIG_PATH cannot be the same.")
        
        try:
            with open(secrets_path, 'r') as file:
                Secrets.secrets_data = {}
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    Secrets.secrets_data[key.strip()] = value.strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"The secrets file '{secrets_path}' was not found")
        except Exception as e:
            raise ValueError(f"Error loading secrets file: {e}")
    
    @staticmethod
    def get(var_name):
        if Secrets.secrets_data is None:
            Secrets.load_secrets()
        return Secrets.secrets_data.get(var_name)
