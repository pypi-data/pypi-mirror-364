import xyzservices.providers as xyz
from typing import Union, Optional, List
from matplotlib.colors import Colormap, LinearSegmentedColormap
from matplotlib import colormaps


def resolve_colormap(colormap: Optional[Union[str, dict]]) -> Optional[Colormap]:
    """
    Resolve a colormap input to a matplotlib colormap object.

    Args:
        colormap (str or dict): The input colormap.
            - If dict: Creates and returns a LinearSegmentedColormap.
            - If str: Returns the corresponding built-in matplotlib colormap.
            - If None: Returns None.

    Returns:
        matplotlib.colors.Colormap: A valid colormap object.

    Raises:
        ValueError: If the colormap dictionary is invalid or the string is not a recognized colormap name.
        TypeError: If the input type is not str or dict.
    """
    if colormap is None:
        return None

    if isinstance(colormap, dict):
        try:
            custom_colormap = LinearSegmentedColormap("custom", colormap)
            custom_colormap._init()  # Forces colormap dict validation
            return custom_colormap
        except Exception as e:
            raise ValueError(f"Invalid colormap dictionary format: {e}")

    if isinstance(colormap, str):
        if colormap in colormaps:
            return colormaps[colormap]
        else:
            raise ValueError(
                f"Invalid colormap name '{colormap}'. Must be one of: {list(colormaps)}"
            )

    raise TypeError(
        f"Invalid colormap type: expected str, dict, or Colormap, got {type(colormap)}"
    )


def get_free_basemap_names() -> List[str]:
    basemaps = xyz.flatten()
    valid_names = []

    for name, provider in basemaps.items():
        try:
            provider.build_url()  # Validates the tile source
            valid_names.append(name)
        except Exception:
            continue

    return valid_names
