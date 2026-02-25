from typing import Union
import json

class Config:
    """
    Basic Config management.
    """

    def __init__(
        self,
        polling_interval: int,
        port: int,
        adapter: str,
        adapter_config: dict
    ) -> None:
        """
        Initialize a Config object.

        Attributes:
            polling_interval (int):
                The interval between the MPC polling on seconds (Ex: 5)

            adapter_config (dict):
                Specific adapter configuration.

            adapter (str):
                Adapter to be used. (Ex: tmdb, imdb)

            port (int):
                Port where MPC Web Interface is running on.
        """

        self.polling_interval: int = polling_interval
        self.adapter_config: dict = adapter_config
        self.adapter: str = adapter
        self.port: int = port

    @staticmethod
    def from_file(path: str) -> Config:
        """
        Initialize a Config object from a json file.

        Args:
            path (str):
                Path to the json file.
        
        Returns:
            Config:
                Config object containing the parsed configuration.
        """

        with open(path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        
        # Gets the configuration of the selected adapter.
        config_adapters: dict[str, dict[str, Union[str, int]]] = data.get("config_adapters", {})
        adapter_config: dict[str, Union[str, int]] = config_adapters.get(adapter, {})

        return Config(
            int(data["polling_interval"]),
            int(data["port"]),
            data["adapter"],
            adapter_config
        )