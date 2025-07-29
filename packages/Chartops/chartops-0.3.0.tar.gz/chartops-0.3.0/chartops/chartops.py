from pathlib import Path
from typing import List, Optional, Tuple, Union

import geopandas as gpd
import ipywidgets as widgets
import xyzservices.providers as xyz
from ipyleaflet import (
    Layer,
    GeoJSON,
    ImageOverlay,
    LayersControl,
    Map as iPyLeafletMap,
    TileLayer,
    VideoOverlay,
    WidgetControl,
    WMSLayer,
    basemap_to_tiles,
)
from chartops import common


class Map(iPyLeafletMap):
    def _get_basemap_layers(self) -> List[Layer]:
        return [layer for layer in self.layers if layer.base]

    def _get_latest_basemap_layer(self) -> Layer:
        return self._get_basemap_layers()[-1]

    def _create_basemap_tile_layer(self, name: str) -> TileLayer:
        tile = basemap_to_tiles(xyz.query_name(name))
        tile.base = True
        tile.name = name
        return tile

    def _validate_opacity(self, opacity: float) -> None:
        if not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1):
            raise TypeError("opacity must be a float between 0 and 1")

    def _validate_bounds(
        self, bounds: Tuple[Tuple[float, float], Tuple[float, float]]
    ) -> None:
        if (
            not isinstance(bounds, tuple)
            or len(bounds) != 2
            or not all(isinstance(pair, tuple) and len(pair) == 2 for pair in bounds)
            or not all(
                isinstance(coord, (int, float)) for pair in bounds for coord in pair
            )
        ):
            raise TypeError(
                "bounds must be a tuple of two (lat, lon) tuples: ((south, west), (north, east))"
            )

    def _validate_position(self, position: str) -> None:
        valid_positions = ["topright", "topleft", "bottomright", "bottomleft"]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position '{position}'. Valid positions are: {valid_positions}"
            )

    def add_basemap(self, basemap_name: str, **kwargs) -> None:
        """
        Add a basemap to the ipyleaflet map.

        Args:
            basemap_name (str): Name of the basemap to add. Resolved with xyzservices.
            **kwargs (dict): Extra kwargs to pass to basemap_to_tiles.

        Returns:
            None
        """
        basemap_tiles = self._create_basemap_tile_layer(basemap_name)
        self.add(basemap_tiles)

    def add_layer_control(self, position: str = "topright") -> None:
        """
        Add a layer control to the map.

        Args:
            position (str, optional): Position of the layer control. Valid positions are "topright", "topleft", "bottomright", "bottomleft". Default is "topright".

        Returns:
            None

        Raises:
            ValueError: If the position is not valid.
        """
        self._validate_position(position)
        self.add(LayersControl(position=position))

    def add_vector(self, filepath: Union[Path, str], name: str = "", **kwargs) -> None:
        """
        Add a vector layer to the map.

        Args:
            filepath (Path or str): Path to the vector dataset or URL to a remote file.
            name (str): Name of the layer. Defaults to ''..
            **kwargs (dict): Additional styling options for the layer. Valid options include:
                - color: str (default: 'blue')
                - weight: int (default: 2)
                - fillOpacity: float (default: 0.1)

        Returns:
            None

        Raises:
            FileNotFoundError: If the local filepath does not exist.
            ValueError: If the vector data cannot be read or converted to GeoJSON, or if styling options are invalid.
        """
        if isinstance(filepath, Path) and not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        color = kwargs.get("color", "blue")
        if not isinstance(color, str):
            raise ValueError(f"color must be a string, got {type(color)}")

        weight = kwargs.get("weight", 2)
        if not isinstance(weight, int):
            raise ValueError(f"weight must be an integer, got {type(weight)}")

        fillOpacity = kwargs.get("fillOpacity", 0.1)
        self._validate_opacity(fillOpacity)

        try:
            gdf = gpd.read_file(filepath)
            geojson = gdf.__geo_interface__
            layer = GeoJSON(
                data=geojson,
                name=name,
                style={"color": color, "weight": weight, "fillOpacity": fillOpacity},
            )
            self.add(layer)
        except Exception as e:
            raise ValueError(f"Failed to add vector layer from {filepath}: {e}")

    def add_raster(
        self,
        url: Union[str, Path],
        opacity: float,
        name: Optional[str] = None,
        colormap: Optional[Union[str, dict]] = None,
        **kwargs,
    ) -> None:
        """
        Add a raster layer to the map using a local or remote tile source.

        Args:
            url (str or Path): Path or URL to the raster file.
            opacity (float): Opacity of the raster layer. Must be between 0 and 1.
            name (str, optional): Name of the layer. Defaults to the stem of the file path.
            colormap (str or dict, optional): Colormap to apply to the raster. Can be a colormap name or a dict. Resolved using `common.resolve_colormap`.
            **kwargs (dict): Additional keyword arguments passed to the tile layer.

        Returns:
            None

        Raises:
            FileNotFoundError: If the local raster file does not exist.
            ValueError: If the opacity is not valid or raster layer cannot be added.
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Raster file not found: {url}")

        self._validate_opacity(opacity)

        try:
            colormap_arg = common.resolve_colormap(colormap)
        except Exception as e:
            raise ValueError(f"Failed to resolve colormap: {e}")

        try:
            client = TileClient(str(url))
            self.center = client.center()
            self.zoom = client.default_zoom
            tile_layer = get_leaflet_tile_layer(
                client, colormap=colormap_arg, opacity=opacity, **kwargs
            )
            tile_layer.name = name or ""
            self.add(tile_layer)
        except Exception as e:
            raise ValueError(f"Failed to add raster layer: {e}")

    def add_image(
        self,
        url: Union[str, Path],
        bounds: Tuple[Tuple[float, float], Tuple[float, float]],
        opacity: float,
        **kwargs,
    ) -> None:
        """
        Add a static image overlay to the map.

        Args:
            url (str or Path): URL or path to the image to overlay.
            bounds (tuple): A tuple of ((south, west), (north, east)) coordinates defining the bounding box of the image.
            opacity (float): Opacity of the image overlay. Must be between 0 and 1.
            **kwargs (dict): Additional keyword arguments passed to ImageOverlay.

        Returns:
            None

        Raises:
            ValueError: If the bounds are not in correct format or opacity is invalid.
            FileNotFoundError: If the local image path does not exist.
        """
        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Image file not found: {url}")

        self._validate_bounds(bounds)
        self._validate_opacity(opacity)

        try:
            image = ImageOverlay(url=str(url), bounds=bounds, opacity=opacity, **kwargs)
            self.add(image)
        except Exception as e:
            raise ValueError(f"Failed to add image overlay: {e}")

    def add_video(
        self,
        url: Union[str, Path],
        bounds: Tuple[Tuple[float, float], Tuple[float, float]],
        opacity: float,
        **kwargs,
    ) -> None:
        """
        Add a video overlay to the map.

        Args:
            url (str or Path): URL or path to the video to overlay.
            bounds (tuple): A tuple of ((south, west), (north, east)) coordinates defining the bounding box of the video.
            opacity (float): Opacity of the video overlay. Must be between 0 and 1.
            **kwargs (dict): Additional keyword arguments passed to VideoOverlay.

        Returns:
            None

        Raises:
            ValueError: If the bounds are not in correct format or opacity is invalid.
            FileNotFoundError: If the local video path does not exist.
        """
        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Video file not found: {url}")

        self._validate_bounds(bounds)
        self._validate_opacity(opacity)

        try:
            video = VideoOverlay(url=str(url), bounds=bounds, opacity=opacity, **kwargs)
            self.add(video)
        except Exception as e:
            raise ValueError(f"Failed to add video overlay: {e}")

    def add_wms_layer(
        self, url: str, layers: str, name: str, format: str, transparent: bool, **kwargs
    ) -> None:
        """
        Add a WMS (Web Map Service) layer to the map.

        Args:
            url (str): Base URL of the WMS service.
            layers (str): Comma-separated list of layer names to request from the service.
            name (str): Name of the layer to show in the map.
            format (str): Image format for the WMS tiles (e.g., 'image/png').
            transparent (bool): Whether the WMS tiles should support transparency.
            **kwargs (dict): Additional keyword arguments passed to the WMSLayer.

        Returns:
            None

        Raises:
            TypeError: If any of the required parameters are not of the expected type.
            ValueError: If the WMS layer cannot be created or added.
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url)}")
        if not isinstance(layers, str):
            raise TypeError(f"layers must be a string, got {type(layers)}")
        if not isinstance(name, str):
            raise TypeError(f"name must be a string, got {type(name)}")
        if not isinstance(format, str):
            raise TypeError(f"format must be a string, got {type(format)}")
        if not isinstance(transparent, bool):
            raise TypeError(f"transparent must be a boolean, got {type(transparent)}")

        try:
            wms = WMSLayer(
                url=url,
                layers=layers,
                format=format,
                transparent=transparent,
                **kwargs,
            )
            wms.name = name
            self.add(wms)
        except Exception as e:
            raise ValueError(f"Failed to add WMS layer: {e}")

    def add_basemap_gui(self, position="topright") -> None:
        """
        Add a toggleable dropdown GUI to select and switch basemaps on the map.

        A small toggle button is initially displayed at the given position.
        When clicked, it reveals a dropdown menu listing available free basemaps.
        The user can select a different basemap, which replaces the latest one.

        Args:
            position (str, optional): Position of the widget control on the map.
                Must be one of "topright", "topleft", "bottomright", or "bottomleft".
                Default is "topright".

        Returns:
            None

        Raises:
            ValueError: If the provided position is not valid.
        """
        self._validate_position(position)

        basemap_names = common.get_free_basemap_names()
        current = self._get_latest_basemap_layer().name

        dropdown = widgets.Dropdown(
            options=basemap_names,
            value=current,
            description="Basemap:",
            layout=widgets.Layout(height="42px", width="auto"),
        )

        name_to_tile = {
            name: self._create_basemap_tile_layer(name) for name in basemap_names
        }

        def on_dropdown_change(change):
            new = change["new"]
            if new != self._get_latest_basemap_layer().name:
                self.substitute(self._get_latest_basemap_layer(), name_to_tile[new])

        dropdown.observe(on_dropdown_change, names="value")

        toggle = widgets.ToggleButton(
            value=False,
            tooltip="Show/hide basemap GUI",
            icon="map",
            layout=widgets.Layout(width="42px", height="42px"),
        )
        btn_control = WidgetControl(widget=toggle, position=position)

        dropdown_box = widgets.HBox([dropdown, toggle])
        gui_control = WidgetControl(widget=dropdown_box, position=position)

        def on_toggle(change):
            if change["new"]:
                self.remove(btn_control)
                self.add(gui_control)
            else:
                try:
                    self.remove(gui_control)
                except ValueError:
                    pass
                self.add(btn_control)

        toggle.observe(on_toggle, names="value")

        self.add(btn_control)
