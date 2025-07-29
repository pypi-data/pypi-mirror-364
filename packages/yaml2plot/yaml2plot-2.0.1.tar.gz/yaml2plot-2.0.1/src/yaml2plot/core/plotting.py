"""
v1.0.0 Standalone plotting functions.

This module provides standalone plotting functions that work with
Dict[str, np.ndarray] data and PlotSpec configuration, following
the v1.0.0 architecture design.
"""

from typing import Dict, List, Optional, Any, Union
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False

from .plotspec import PlotSpec


def plot(
    data: Union[Dict[str, np.ndarray], str, "Path", "xr.Dataset"],
    spec: PlotSpec | Dict[str, Any],
    *,
    show: bool = True,
) -> go.Figure:
    """
    Create Plotly figure from data and PlotSpec configuration.

    Args:
        data: Data source - can be:
            - Dict mapping signal name → numpy array
            - Raw file path (str/Path) 
            - xarray Dataset (preferred for new code)
        spec: PlotSpec configuration object **or** raw configuration ``dict``
        show: When *True* (default) immediately display the figure via
              ``fig.show()`` – handy for interactive use.  Tests can pass
              ``show=False`` to suppress GUI pop-ups.

    Returns:
        Plotly ``go.Figure`` instance

    Raises:
        ValueError: If required signals are missing from data
    """
    # ---------------------------------------------
    # 1) Normalize *data* argument – support file paths and xarray Datasets
    # ---------------------------------------------
    def _dataset_to_dict(dataset):
        """Convert xarray Dataset to dict for internal plotting logic."""
        data_dict = {}
        # Add all data variables
        for var in dataset.data_vars:
            data_dict[var] = dataset[var].values
        # Add all coordinates (time, frequency, etc.)
        for coord in dataset.coords:
            data_dict[coord] = dataset.coords[coord].values
        return data_dict
    
    if isinstance(data, (str, Path)):
        # Lazy-load raw file on-demand so docs snippets like
        # wv.plot("sim.raw", spec) keep working.
        from ..loader import load_spice_raw  # local import to avoid cycle
        dataset = load_spice_raw(data)
        data = _dataset_to_dict(dataset)  # type: ignore[assignment]
    elif HAS_XARRAY and hasattr(data, 'data_vars') and hasattr(data, 'coords'):
        # xarray Dataset - convert to dict for internal plotting
        data = _dataset_to_dict(data)  # type: ignore[assignment]
    elif not isinstance(data, dict):
        raise TypeError(
            "data must be a dict, xarray Dataset, or raw-file path (str/Path)"
        )


    # ---------------------------------------------
    # 2) Normalize *spec* argument
    # ---------------------------------------------
    if isinstance(spec, PlotSpec):
        config = spec.to_dict()
    elif isinstance(spec, dict):
        config = spec
    else:
        raise TypeError("spec must be a PlotSpec instance or configuration dict")

    # Create figure and apply layout
    fig = create_figure()
    layout = create_layout(config)
    fig.update_layout(layout)

    # Get X-axis data
    x_signal = config["x"]["signal"]
    if x_signal not in data:
        raise ValueError(
            f"X-axis signal '{x_signal}' not found in data. Available: {list(data.keys())}"
        )
    x_data = data[x_signal]

    # Add traces for each Y-axis
    for y_axis_idx, y_spec in enumerate(config["y"]):
        # Determine Y-axis ID
        y_axis_id = "y" if y_axis_idx == 0 else f"y{y_axis_idx + 1}"

        # Add each signal in this Y-axis
        for legend_name, signal_key in y_spec["signals"].items():
            # Support legacy "data." prefix used in documentation examples
            lookup_key = (
                signal_key[5:] if signal_key.startswith("data.") else signal_key
            )

            if lookup_key not in data:
                raise ValueError(
                    f"Signal '{signal_key}' not found in data. Available: {list(data.keys())}"
                )

            y_data = data[lookup_key]
            add_waveform(fig, x_data, y_data, name=legend_name, y_axis=y_axis_id)

    # Show figure for interactive workflows if requested
    if show:
        fig.show()

    return fig


def create_figure() -> go.Figure:
    """
    Create empty Plotly figure with basic setup.

    Returns:
        Empty Plotly Figure object
    """
    return go.Figure()


def _configure_title(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create title configuration for Plotly figure.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()

    Returns:
        Title configuration dictionary (empty if no title)
    """
    title_config = {}

    if config.get("title"):
        title_config["title"] = {
            "text": config["title"],
            "x": config.get("title_x", 0.5),
            "xanchor": config.get("title_xanchor", "center"),
        }

    return title_config


def _configure_dimensions(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create figure dimensions configuration for Plotly figure.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()

    Returns:
        Dimensions configuration dictionary (empty if no dimensions specified)
    """
    dimensions_config = {}

    if config.get("width"):
        dimensions_config["width"] = config["width"]
    if config.get("height"):
        dimensions_config["height"] = config["height"]

    return dimensions_config


def _configure_theme_and_legend(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create theme and legend configuration for Plotly figure.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()

    Returns:
        Theme and legend configuration dictionary
    """
    theme_legend_config = {}

    # Theme
    if config.get("theme") and config["theme"] != "plotly":
        theme_legend_config["template"] = config["theme"]

    # Legend
    theme_legend_config["showlegend"] = config.get("show_legend", True)

    return theme_legend_config


def _configure_x_axis(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create X-axis configuration for Plotly figure.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()

    Returns:
        X-axis configuration dictionary
    """
    x_spec = config.get("x", {})

    # Use custom label if provided, otherwise fall back to signal key
    title = x_spec.get("label") or x_spec.get("signal", "X-axis")

    x_axis_config = {
        "xaxis": {
            "title": title,
            "showgrid": config.get("grid", True),
            "rangeslider": {"visible": config.get("show_rangeslider", True)},
        }
    }

    # Configure axis type
    axis_type = "log" if x_spec.get("scale") == "log" else "linear"
    x_axis_config["xaxis"]["type"] = axis_type

    # Add range support
    if x_spec.get("range"):
        x_axis_config["xaxis"]["range"] = x_spec["range"]

    # Add engineering notation for all plots
    # Use SI prefixes (1G, 1M, 1k) instead of American notation (1B, 1M, 1K)
    # This provides consistent engineering notation across all axes
    x_axis_config["xaxis"]["exponentformat"] = "SI"

    return x_axis_config


def _calculate_y_axis_domains(num_y_axes: int) -> List[List[float]]:
    """
    Calculate Y-axis domain splits for multi-axis plots.

    First Y-axis appears at the top (matching YAML order), subsequent axes below.

    Args:
        num_y_axes: Number of Y-axes to create

    Returns:
        List of [bottom, top] domain pairs for each Y-axis
    """
    if num_y_axes == 1:
        # Single Y-axis gets full domain
        return [[0, 1]]
    else:
        # Multiple Y-axes share the space from top to bottom
        gap = 0.05
        total_gap_space = gap * (num_y_axes - 1)
        effective_height = 1.0 - total_gap_space
        single_axis_height = effective_height / num_y_axes

        domains = []
        current_top = 1.0  # Start from the top
        for i in range(num_y_axes):
            domain_bottom = current_top - single_axis_height
            # Ensure domains are within [0, 1] bounds to avoid floating-point precision issues
            domain_bottom = max(0.0, domain_bottom)
            current_top = min(1.0, current_top)

            domains.append([domain_bottom, current_top])
            current_top = domain_bottom - gap  # Move down for next axis

        return domains


def _create_single_y_axis_config(
    y_spec: Dict[str, Any],
    domain: List[float],
    axis_index: int,
    global_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create configuration for a single Y-axis.

    Args:
        y_spec: Y-axis specification from PlotSpec (label, log_scale, range, etc.)
        domain: [bottom, top] domain values for this axis
        axis_index: 0-based index of this axis
        global_config: Global configuration for shared settings (grid, etc.)

    Returns:
        Single Y-axis configuration dictionary
    """
    # Use custom label if provided, otherwise fall back to "Y-axis"
    title = y_spec.get("label") or f"Y-axis {axis_index}"

    axis_config = {
        "title": title,
        "domain": domain,
        "showgrid": global_config.get("grid", True),
    }

    # Configure axis type
    axis_type = "log" if y_spec.get("scale") == "log" else "linear"
    axis_config["type"] = axis_type

    # Range support
    if y_spec.get("range"):
        axis_config["range"] = y_spec["range"]

    # Add engineering notation for consistent SI prefix display
    # Use SI prefixes (1G, 1M, 1k) instead of American notation (1B, 1M, 1K)
    axis_config["exponentformat"] = "SI"

    return axis_config


def _config_zoom(config: Dict[str, Any], num_y_axes: int) -> Dict[str, Any]:
    """
    Configure optimal zoom settings for Plotly figure.

    Sets the zoom XY mode by default - enables flexible zooming on all axes.
    Users can drag in X-only, Y-only, or XY directions naturally.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()
        num_y_axes: Number of Y-axes in the plot

    Returns:
        Zoom configuration dictionary with optimal settings
    """
    zoom_config = {}

    if num_y_axes == 0:
        return zoom_config

    # Apply optimal zoom XY settings by default
    zoom_config["dragmode"] = "zoom"
    zoom_config["xaxis.fixedrange"] = False

    # Enable flexible zooming on all Y-axes
    for i in range(num_y_axes):
        axis_id = "yaxis" if i == 0 else f"yaxis{i + 1}"
        zoom_config[f"{axis_id}.fixedrange"] = False

    return zoom_config


def create_layout(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create layout configuration for Plotly figure.

    Args:
        config: Configuration dictionary from PlotSpec.to_dict()

    Returns:
        Layout configuration dictionary
    """
    layout = {}

    # Title configuration
    layout.update(_configure_title(config))

    # Figure dimensions
    layout.update(_configure_dimensions(config))

    # Theme and legend
    layout.update(_configure_theme_and_legend(config))

    # X-axis configuration
    layout.update(_configure_x_axis(config))

    # Y-axes configuration
    num_y_axes = len(config.get("y", []))

    if num_y_axes > 0:
        # Calculate Y-axis domains for multi-axis plots
        domains = _calculate_y_axis_domains(num_y_axes)

        # Configure each Y-axis
        for i, y_spec in enumerate(config["y"]):
            axis_key = "yaxis" if i == 0 else f"yaxis{i + 1}"

            axis_config = _create_single_y_axis_config(
                y_spec=y_spec, domain=domains[i], axis_index=i, global_config=config
            )

            layout[axis_key] = axis_config

    # Optimal zoom configuration (zoom XY mode by default)
    layout.update(_config_zoom(config, num_y_axes))

    # Zoom buttons functionality has been removed from v1.0.0.

    return layout


def add_waveform(
    fig: go.Figure,
    x_data: np.ndarray,
    y_data: np.ndarray,
    name: str,
    y_axis: str = "y",
    **kwargs,
) -> None:
    """
    Add single waveform trace to figure.

    Args:
        fig: Plotly figure to add trace to
        x_data: X-axis data array
        y_data: Y-axis data array
        name: Trace name for legend
        y_axis: Y-axis identifier (y, y2, y3, etc.)
        **kwargs: Additional trace styling options
    """
    # Convert complex signals to real for Plotly compatibility
    # For complex signals, take the real part (magnitude would be np.abs())
    if np.iscomplexobj(x_data):
        # For most cases like frequency, time, we want the real part
        # For AC analysis voltages/currents, users should use processed_data for magnitude/phase
        x_data = np.real(x_data)

    if np.iscomplexobj(y_data):
        # For most cases like frequency, time, we want the real part
        # For AC analysis voltages/currents, users should use processed_data for magnitude/phase
        y_data = np.real(y_data)

    # Create scatter trace
    trace = go.Scatter(x=x_data, y=y_data, name=name, yaxis=y_axis, **kwargs)

    # Add trace to figure
    fig.add_trace(trace)
