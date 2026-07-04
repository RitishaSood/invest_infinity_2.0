"""
Config package for Invest Infinity ML pipeline.

Exposes a single ready-to-use `config` object built from settings.yaml.
Usage in any other file:

    from config.config import config
    print(config.sequence_length)
"""

from config.config import config

__all__ = ["config"]