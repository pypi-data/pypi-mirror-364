'''Makes datasets behave like bundles of submodules.'''

from . import cdc, food_ids, atu_dirty

__all__ = ["cdc", "food_ids", "atu_dirty"]