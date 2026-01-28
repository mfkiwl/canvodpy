from datetime import datetime
import json
from pathlib import Path
import sys
import warnings
from typing import Any

import icechunk
from IPython.display import HTML, display
import numpy as np
import pandas as pd
import zarr


class RinexStoreViewer:
    """
    Rich HTML/CSS viewer for RINEX Icechunk stores.

    Parameters
    ----------
    store : icechunk.Store
        RINEX store to visualize.
    """

    def __init__(self, store) -> None:
        self.store = store
        self.css_styles = self._get_enhanced_css_styles()

    def _get_enhanced_css_styles(self) -> str:
        """Generate enhanced CSS styles for RINEX store preview."""
        return """
        <style>
        .rinex-store {
            font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 13px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
            margin: 15px 0;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .store-header {
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 50%, #581c87 100%);
            color: white;
            padding: 16px 20px;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
        }

        .store-title {
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .store-path {
            font-size: 11px;
            opacity: 0.9;
            margin-top: 6px;
            font-family: monospace;
            background: rgba(255,255,255,0.1);
            padding: 4px 8px;
            border-radius: 4px;
            word-break: break-all;
        }

        .store-stats {
            display: flex;
            gap: 20px;
            margin-top: 8px;
            font-size: 12px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .store-content {
            max-height: 600px;
            overflow-y: auto;
            background: white;
            margin: 0;
        }

        .branch-section {
            border-bottom: 2px solid #f3f4f6;
        }

        .branch-header {
            background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 12px 20px;
            font-weight: 600;
            color: #1f2937;
            border-bottom: 1px solid #d1d5db;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .branch-header:hover {
            background: linear-gradient(90deg, #e2e8f0 0%, #cbd5e1 100%);
        }

        .branch-content {
            padding: 0;
        }

        .site-group {
            border-bottom: 1px solid #f3f4f6;
        }

        .site-header {
            background: linear-gradient(90deg, #fef3c7 0%, #fbbf24 20%, #fef3c7 100%);
            padding: 10px 20px;
            font-weight: 500;
            color: #92400e;
            border-bottom: 1px solid #f59e0b;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .site-info {
            font-size: 11px;
            opacity: 0.8;
        }

        .tree-item {
            padding: 4px 20px;
            font-family: 'SF Mono', Consolas, monospace;
            white-space: pre-wrap;
            line-height: 1.5;
            border-left: 3px solid transparent;
        }

        .tree-item:hover {
            background: #f8fafc;
            border-left-color: #3b82f6;
        }

        .tree-metadata {
            background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 100%);
            border-left-color: #3b82f6 !important;
            font-weight: 500;
        }

        .tree-group {
            color: #059669;
            font-weight: 600;
        }

        .tree-array {
            color: #dc2626;
            font-weight: 500;
        }

        .tree-connector {
            color: #6b7280;
            font-weight: normal;
        }

        .array-info {
            color: #374151;
            font-size: 11px;
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 8px;
            display: inline-block;
        }

        .array-shape {
            color: #7c3aed;
            font-weight: 500;
        }

        .array-dtype {
            color: #059669;
        }

        .metadata-table {
            margin: 8px 20px;
            font-size: 11px;
            background: #f8fafc;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }

        .metadata-row {
            display: flex;
            padding: 6px 12px;
            border-bottom: 1px solid #e5e7eb;
        }

        .metadata-row:last-child {
            border-bottom: none;
        }

        .metadata-row:nth-child(even) {
            background: #f1f5f9;
        }

        .metadata-key {
            flex: 1;
            font-weight: 500;
            color: #374151;
        }

        .metadata-value {
            flex: 2;
            color: #6b7280;
            font-family: monospace;
        }

        .store-summary {
            background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 16px 20px;
            border-top: 2px solid #0ea5e9;
            font-size: 12px;
            color: #0c4a6e;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .summary-item {
            display: flex;
            align-items: center;
            gap: 8px;
            background: white;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #0ea5e9;
        }

        .highlight {
            background: #fef3c7;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 500;
        }

        .error-message {
            color: #dc2626;
            background: #fef2f2;
            padding: 12px 20px;
            border-left: 4px solid #dc2626;
            margin: 8px 20px;
            border-radius: 0 4px 4px 0;
        }

        .data-type-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 500;
            margin-left: 8px;
        }

        .badge-coordinate {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge-observation {
            background: #fecaca;
            color: #991b1b;
        }

        .badge-metadata {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-system {
            background: #e0e7ff;
            color: #3730a3;
        }
        </style>
        """

    def _identify_array_type(self, array_name: str) -> str:
        """Identify the RINEX array type and return its badge HTML."""
        coordinate_arrays = ['phi', 'theta', 'epoch']
        observation_arrays = ['SNR', 'code', 'pseudorange', 'carrier_phase']
        system_arrays = [
            'sv', 'sid', 'system', 'band', 'freq_center', 'freq_min',
            'freq_max'
        ]

        if array_name in coordinate_arrays:
            return (
                '<span class="data-type-badge badge-coordinate">'
                "📍 Coordinate</span>"
            )
        if array_name in observation_arrays:
            return (
                '<span class="data-type-badge badge-observation">'
                "📡 Observation</span>"
            )
        if array_name in system_arrays:
            return (
                '<span class="data-type-badge badge-system">'
                "🛰️ System</span>"
            )
        if array_name == "metadata":
            return (
                '<span class="data-type-badge badge-metadata">'
                "📋 Metadata</span>"
            )
        return '<span class="data-type-badge badge-system">📊 Data</span>'

    def _format_array_info(self, arr, array_name: str) -> str:
        """Format array information with enhanced styling."""
        try:
            shape_str = str(arr.shape)
            dtype_str = str(arr.dtype)
            badge = self._identify_array_type(array_name)

            # Calculate data size
            total_elements = np.prod(arr.shape)
            if total_elements > 1e6:
                size_str = f"{total_elements/1e6:.1f}M elements"
            elif total_elements > 1e3:
                size_str = f"{total_elements/1e3:.1f}K elements"
            else:
                size_str = f"{total_elements} elements"

            return (
                f'<span class="array-shape">{shape_str}</span> '
                f'<span class="array-dtype">{dtype_str}</span> '
                f"• {size_str}{badge}"
            )
        except Exception as e:
            return f'<span class="error-message">Error reading array: {e}</span>'

    def _try_read_metadata(self, group, site_name: str) -> str:
        """Attempt to read and format the metadata table."""
        try:
            if 'metadata' in group:
                metadata = group['metadata']
                # If it's a zarr array, try to read it
                if hasattr(metadata, 'attrs'):
                    attrs = dict(metadata.attrs)
                    if attrs:
                        return self._format_metadata_table(
                            attrs, f"{site_name} Metadata")

                # If it's readable as data
                try:
                    data = metadata[:]
                    if isinstance(data, (list, tuple, np.ndarray)):
                        # Try to interpret as key-value pairs
                        if len(data) > 0:
                            return (
                                '<div class="metadata-table">'
                                '<div class="metadata-row">'
                                '<div class="metadata-key">'
                                "Metadata Records</div>"
                                '<div class="metadata-value">'
                                f"{len(data)} entries</div>"
                                "</div></div>"
                            )
                except Exception:
                    pass

                return (
                    '<div class="metadata-table">'
                    '<div class="metadata-row">'
                    '<div class="metadata-key">Metadata</div>'
                    '<div class="metadata-value">'
                    "Present (format unknown)</div></div></div>"
                )
        except Exception as e:
            return f'<div class="error-message">Could not read metadata: {e}</div>'

        return ""

    def _format_metadata_table(
        self,
        metadata_dict: dict,
        title: str = "Metadata",
    ) -> str:
        """Format metadata as an HTML table."""
        if not metadata_dict:
            return ""

        html = '<div class="metadata-table">'
        html += (
            '<div class="metadata-row" style="background: #1e40af; '
            'color: white; font-weight: 600;">'
            '<div class="metadata-key">'
            f"{title}</div><div class=\"metadata-value\">Value</div></div>"
        )

        for key, value in metadata_dict.items():
            # Format different types of values
            if isinstance(value, (list, tuple, np.ndarray)):
                value_str = f"[{len(value)} items]"
            elif isinstance(value, dict):
                value_str = f"{{dict with {len(value)} keys}}"
            else:
                value_str = str(value)[:100]  # Truncate long values

            html += (
                '<div class="metadata-row">'
                f'<div class="metadata-key">{key}</div>'
                f'<div class="metadata-value">{value_str}</div>'
                "</div>"
            )

        html += '</div>'
        return html

    def _build_tree_html(
        self,
        group,
        prefix: str = "",
        max_depth: int | None = None,
        current_depth: int = 0,
        site_name: str = "",
    ) -> str:
        """Build enhanced HTML tree structure for RINEX data."""
        if max_depth is not None and current_depth >= max_depth:
            return ""

        html_parts = []

        try:
            # Get all groups and arrays
            groups = list(group.group_keys())
            arrays = list(group.array_keys())

            # Sort arrays by type for better organization
            coordinate_arrays = [
                a for a in arrays if a in ['phi', 'theta', 'epoch']
            ]
            observation_arrays = [
                a for a in arrays if a in ['SNR', 'code', 'pseudorange']
            ]
            system_arrays = [
                a for a in arrays if a in [
                    'sv', 'sid', 'system', 'band', 'freq_center', 'freq_min',
                    'freq_max'
                ]
            ]
            metadata_arrays = [a for a in arrays if a == 'metadata']
            other_arrays = [
                a for a in arrays if a not in coordinate_arrays +
                observation_arrays + system_arrays + metadata_arrays
            ]

            # Organize arrays by category
            organized_arrays = (
                metadata_arrays +
                coordinate_arrays +
                observation_arrays +
                system_arrays +
                other_arrays
            )
            items = groups + organized_arrays

            # Add metadata display if present
            if 'metadata' in arrays and site_name:
                metadata_html = self._try_read_metadata(group, site_name)
                if metadata_html:
                    html_parts.append(metadata_html)

            for i, item_name in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "

                if item_name in groups:
                    # It's a group (site)
                    html_parts.append(f'<div class="tree-item">')
                    html_parts.append(
                        f'<span class="tree-connector">{prefix}{connector}</span>'
                    )
                    html_parts.append(
                        f'<span class="tree-group">📁 {item_name}</span>')
                    html_parts.append('</div>')

                    # Recurse into subgroup
                    try:
                        subgroup = group[item_name]
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        html_parts.append(
                            self._build_tree_html(
                                subgroup,
                                new_prefix,
                                max_depth,
                                current_depth + 1,
                                item_name,
                            )
                        )
                    except Exception as e:
                        html_parts.append(
                            '<div class="error-message">Error accessing group '
                            f"{item_name}: {e}</div>"
                        )

                else:
                    # It's an array
                    try:
                        arr = group[item_name]
                        array_info = self._format_array_info(arr, item_name)

                        css_class = (
                            "tree-metadata"
                            if item_name == "metadata"
                            else "tree-item"
                        )

                        html_parts.append(f'<div class="{css_class}">')
                        html_parts.append(
                            f'<span class="tree-connector">{prefix}{connector}</span>'
                        )
                        html_parts.append(
                            f'<span class="tree-array">{item_name}</span>')
                        html_parts.append(
                            f'<span class="array-info">{array_info}</span>')
                        html_parts.append('</div>')

                    except Exception as e:
                        html_parts.append(
                            '<div class="error-message">Error accessing array '
                            f"{item_name}: {e}</div>"
                        )

        except Exception as e:
            html_parts.append(
                f'<div class="error-message">Error building tree: {e}</div>')

        return ''.join(html_parts)

    def _get_store_summary(self) -> dict[str, Any]:
        """Generate comprehensive summary statistics for RINEX store."""
        try:
            branches = self.store.get_branch_names()
            total_sites = 0
            total_arrays = 0
            total_observations = 0

            for branch in branches:
                try:
                    storage_config = icechunk.local_filesystem_storage(
                        self.store.store_path)
                    repo = icechunk.Repository.open(storage=storage_config)
                    session = repo.readonly_session(branch)
                    root = zarr.open(session.store, mode='r')

                    sites = list(root.group_keys())
                    total_sites += len(sites)

                    for site in sites:
                        site_group = root[site]
                        arrays = list(site_group.array_keys())
                        total_arrays += len(arrays)

                        # Estimate observations from epoch array if present
                        if 'epoch' in arrays:
                            try:
                                epoch_arr = site_group['epoch']
                                sid_arr = site_group['sid']
                                total_observations += (
                                    epoch_arr.shape[0] * sid_arr.shape[0]
                                )
                            except Exception:
                                pass

                except Exception:
                    pass

            return {
                'branches': len(branches),
                'sites': total_sites,
                'arrays': total_arrays,
                'observations': total_observations,
                'path': str(self.store.store_path)
            }
        except Exception as e:
            return {'error': str(e)}

    def _repr_html_(self) -> str:
        """Generate rich HTML representation for RINEX store."""
        html_parts = [self.css_styles]

        # Store header
        html_parts.append('<div class="rinex-store">')
        html_parts.append('<div class="store-header">')
        html_parts.append(
            '<div class="store-title">🛰️ RINEX IceChunk Store</div>')
        html_parts.append(
            f'<div class="store-path">{self.store.store_path}</div>')

        # Quick stats in header
        summary = self._get_store_summary()
        if 'error' not in summary:
            html_parts.append('<div class="store-stats">')
            html_parts.append(
                f'<div class="stat-item">📊 {summary["branches"]} branches</div>'
            )
            html_parts.append(
                f'<div class="stat-item">📍 {summary["sites"]} sites</div>')
            html_parts.append(
                '<div class="stat-item">📡 '
                f'{summary["observations"]:,} observations</div>'
            )
            html_parts.append('</div>')

        html_parts.append('</div>')

        # Store content
        html_parts.append('<div class="store-content">')

        try:
            branches = self.store.get_branch_names()

            if not branches:
                html_parts.append(
                    '<div class="error-message">No branches found in store</div>'
                )
            else:
                for i, branch in enumerate(branches):
                    # Branch section
                    html_parts.append('<div class="branch-section">')
                    html_parts.append(
                        '<div class="branch-header">🌿 Branch: '
                        f'<span class="highlight">{branch}</span></div>'
                    )
                    html_parts.append('<div class="branch-content">')

                    try:
                        storage_config = icechunk.local_filesystem_storage(
                            self.store.store_path)
                        repo = icechunk.Repository.open(storage=storage_config)
                        session = repo.readonly_session(branch)
                        root = zarr.open(session.store, mode='r')

                        # Display each site as a separate section
                        sites = list(root.group_keys())
                        if sites:
                            for site in sites:
                                html_parts.append('<div class="site-group">')

                                # Site header with basic info
                                try:
                                    site_group = root[site]
                                    arrays = list(site_group.array_keys())
                                    obs_count = "Unknown"
                                    if 'epoch' in arrays:
                                        try:
                                            obs_count = (
                                                f"{site_group['epoch'].shape[0]:,}"
                                            )
                                        except Exception:
                                            pass

                                    html_parts.append(
                                        f'<div class="site-header">')
                                    html_parts.append(f'<span>🏢 {site}</span>')
                                    html_parts.append(
                                        '<span class="site-info">'
                                        f"{len(arrays)} arrays • "
                                        f"{obs_count} observations</span>"
                                    )
                                    html_parts.append('</div>')
                                except Exception:
                                    html_parts.append(
                                        f'<div class="site-header">🏢 {site}</div>'
                                    )

                                # Site tree
                                tree_html = self._build_tree_html(
                                    root[site], max_depth=3, site_name=site)
                                if tree_html:
                                    html_parts.append(tree_html)

                                html_parts.append('</div>')  # site-group
                        else:
                            html_parts.append(
                                '<div class="tree-item">📭 No sites in branch</div>'
                            )

                    except Exception as e:
                        html_parts.append(
                            '<div class="error-message">Error accessing '
                            f"branch {branch}: {e}</div>"
                        )

                    html_parts.append('</div>')  # branch-content
                    html_parts.append('</div>')  # branch-section

        except Exception as e:
            html_parts.append(
                f'<div class="error-message">Error loading store: {e}</div>')

        html_parts.append('</div>')  # store-content

        # Enhanced summary footer
        html_parts.append('<div class="store-summary">')
        html_parts.append('<div class="summary-grid">')
        if 'error' in summary:
            html_parts.append(
                f'<div class="summary-item">⚠️ Error: {summary["error"]}</div>'
            )
        else:
            html_parts.append(
                '<div class="summary-item">📊 '
                f'<strong>{summary["branches"]}</strong> branches</div>'
            )
            html_parts.append(
                '<div class="summary-item">📍 '
                f'<strong>{summary["sites"]}</strong> observation sites</div>'
            )
            html_parts.append(
                '<div class="summary-item">📊 '
                f'<strong>{summary["arrays"]}</strong> data arrays</div>'
            )
            html_parts.append(
                '<div class="summary-item">📡 '
                f'<strong>{summary["observations"]:,}</strong> '
                "total observations</div>"
            )
        html_parts.append('</div>')
        html_parts.append('</div>')

        html_parts.append('</div>')  # rinex-store

        return ''.join(html_parts)


# Enhanced monkey patch for RINEX stores
def add_rich_display_to_store(store_class: type) -> type:
    """Add rich HTML display capabilities for RINEX Icechunk stores."""

    def _repr_html_(self) -> str:
        """Rich HTML representation for RINEX stores."""
        viewer = RinexStoreViewer(self)
        return viewer._repr_html_()

    def show_tree(self, max_depth=3):
        """Display interactive tree view."""
        viewer = RinexStoreViewer(self)
        display(HTML(viewer._repr_html_()))

    def preview(self):
        """Show store preview in notebook."""
        display(HTML(self._repr_html_()))

    # Add methods to the class
    store_class._repr_html_ = _repr_html_
    store_class.show_tree = show_tree
    store_class.preview = preview

    return store_class


if __name__ == "__main__":
    print("🛰️ Enhanced RINEX Store Viewer ready!")
    print("📝 Apply @add_rich_display_to_store decorator to your store class")
    print(
        "📊 RINEX stores will display with enhanced metadata and organization")
