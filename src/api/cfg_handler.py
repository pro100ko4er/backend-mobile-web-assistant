import os
import json
from abc import abstractmethod


class JSONBase(object):
    """Base class for JSON configs"""
    def __init__(self, file_name, assert_missing=True):
        # Path to config files
        self.local_path = os.path.join(os.path.dirname(__file__), file_name)
        self.is_changed = False
        self.data = {}
        self.assert_missing = assert_missing

    @abstractmethod
    def load(self):
        """Loads file"""
        pass

    @abstractmethod
    def save(self):
        """Save changes"""
        pass


class JSON(JSONBase):
    def __init__(self, file_name, assert_missing=True):
        super().__init__(file_name, assert_missing)

    def load(self):
        """Loads file"""
        with open(self.local_path) as f:
            self.data = json.load(f)

    def save(self):
        """Save changes"""
        if self.is_changed:
            with open(self.local_path, "w") as f:
                json.dump(self.data, f, indent=2, sort_keys=True)

    def get(self, *keys):
        """Returns parsed value"""
        res = self.data.get(keys[0]) if len(keys) else None
        for key in keys[1:]:
            res = res.get(key)
            if res is None:
                if self.assert_missing:
                    raise ValueError(f"{key} in [{keys}] is missing")
                return
        return res

    def get_selection_config(self, *keys):
        """This is used for an easy switch between different models/embeddings, etc.
            We find a root dict that contains 'config' value controlling,
            which set of parameters is to select"""
        root = self.get(*keys)
        selection = root.get('config')
        return root.get(selection)

    def set(self, value, *keys):
        """Inserts a value in a nested dictionary using keys from a list"""
        curr = self.data
        for key in keys[:-1]:
            curr = curr.setdefault(key, {})
        curr[keys[-1]] = value
        self.is_changed = True


def load_config(config_file, storage_type='local'):
    """Returns a config from local config file"""
    cfg = {}
    if storage_type == 'local':
        cfg = JSON(config_file)
    cfg.load()
    return cfg


