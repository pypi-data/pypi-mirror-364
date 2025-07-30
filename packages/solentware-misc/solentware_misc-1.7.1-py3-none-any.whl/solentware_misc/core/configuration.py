# configuration.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Access and update items in a configuration file.

The initial values are taken from file named in self._CONFIGURATION in the
user's home directory if the file exists.

"""

import os

_items = {}


class ConfigurationError(Exception):
    """Exception class for configuration module."""


class Configuration:
    """Identify configuration file and access and update item values.

    Subclasses should override _CONFIGURATION and _DEFAULT_ITEM_VAULES with
    suitable values.

    _DEFAULT_ITEM_VAULES should contain (<name>, <value>) tuples.

    """

    _CONFIGURATION = ".configuration.conf"
    _DEFAULT_ITEM_VAULES = ()

    def __init__(self):
        """Initialiase configuration._items when first instance is created."""
        if len(_items) == 0:
            self.set_configuration_values_from_text(
                self.get_configuration_text_and_values_for_items_from_file(
                    {
                        default[0]: default[1]
                        for default in self._DEFAULT_ITEM_VAULES
                    }
                )
            )

    def get_configuration_file_name(self):
        """Return configuration file name."""
        return self._CONFIGURATION

    def get_configuration_file_path(self):
        """Return configuration file path."""
        return os.path.expanduser(os.path.join("~", self._CONFIGURATION))

    @staticmethod
    def get_configuration_value(item, default=None):
        """Return value of configuration item or default if item not found.

        The return value is the default value or the most recent value saved
        by set_configuration_value().

        Changes in the configuration file since the file was read at start-up
        are not seen.  Use get_configuration_value_from_file() to see that.

        """
        return _items.get(item, default)

    @staticmethod
    def get_configuration_value_from_file(item, default=None):
        """Return configuration item value on file or default if not found.

        Use get_configuration_value() to avoid reading the configuration file
        on each call, but this may not return the current value on file.
        After editing with another program for example.

        """
        return _items.get(item, default=default)

    def get_configuration_text_for_items_from_file(self, items, values=False):
        """Return text in file configuration items.

        Values are cached if bool(values) evaluates True.

        """
        try:
            with open(
                os.path.expanduser(os.path.join("~", self._CONFIGURATION))
            ) as config_file:
                config_text_on_file = config_file.read()
        except OSError:
            config_text_on_file = ""
        config_text_lines = []
        for item in config_text_on_file.splitlines():
            item = item.strip()
            if len(item) == 0:
                continue
            item = item.split(maxsplit=1)
            if len(item) == 1:
                continue
            key, value = item
            if key not in items:
                continue
            if values:
                _items[key] = value
            config_text_lines.append(" ".join(item))
        return "\n".join(config_text_lines)

    def get_configuration_text_and_values_for_items_from_file(self, items):
        """Cache values and return text in file configuration items."""
        return self.get_configuration_text_for_items_from_file(
            items, values=True
        )

    def set_configuration_value(self, item, value):
        """Set value of configuration item if item exists."""
        if item in _items:
            if _items[item] != value:
                _items[item] = value
                self._save_configuration()

    def set_configuration_values_from_text(self, text, config_items=None):
        """Set values of configuration items from text if item exists."""
        if config_items is None:
            config_items = {}
        default_values = {
            default[0]: default[1] for default in self._DEFAULT_ITEM_VAULES
        }

        change = False
        for i in text.splitlines():
            i = i.split(maxsplit=1)
            if not i:
                continue
            key = i[0]
            if key not in config_items or key not in default_values:
                continue
            if len(i) == 1:
                value = default_values[key]
            else:
                value = i[1].strip()
            if key not in _items or _items[key] != value:
                _items[key] = value
                change = True
        for key, value in default_values.items():
            if key not in _items:
                _items[key] = value
                change = True
        if change:
            self._save_configuration()

    @staticmethod
    def convert_home_directory_to_tilde(path):
        """Return path with leading /home/<user> converted to ~."""
        home = os.path.expanduser("~")

        # removeprefix not available until Python3.9
        # pylint and pycodestyle disagree on spaces in ' + 1 :'.
        if path.startswith(home):
            return os.path.join("~", path[len(home) + 1 :])
        return path

    def _save_configuration(self):
        """Save the configuration in file named in self._CONFIGURATION."""
        config_text = []
        for key in sorted(_items):
            config_text.append(" ".join((key, _items[key])))
        config_text = "\n".join(config_text)
        try:
            with open(
                os.path.expanduser(os.path.join("~", self._CONFIGURATION)), "w"
            ) as config_file:
                config_file.write(config_text)
        except OSError as error:
            raise ConfigurationError(
                "Unable to save configuration file"
            ) from error
