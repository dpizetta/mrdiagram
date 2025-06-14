#!/usr/bin/env python3
"""
MRI Pulse Shape SVG Icon Generator

This script reads the shapes.json configuration file, instantiates the corresponding
shape classes from shapes.py, and generates SVG icons organized by category.
"""

import json
import os
import numpy as np
from pathlib import Path
import importlib.util

# Import the shapes module
def load_shapes_module(shapes_py_path):
    """Dynamically load the shapes.py module"""
    spec = importlib.util.spec_from_file_location("shapes", shapes_py_path)
    shapes_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shapes_module)
    return shapes_module

def create_svg_from_shape(shape_data, width=200, height=200, stroke_width=2):
    """
    Convert shape data points to SVG path

    Args:
        shape_data: numpy array of normalized shape values [-1, 1]
        width: SVG width in pixels
        height: SVG height in pixels
        stroke_width: Line thickness
    """
    if len(shape_data) == 0:
        return ""

    # Create coordinate pairs
    x_coords = np.linspace(10, width-10, len(shape_data))
    # Map from [-1,1] to [height-10, 10] (flipped for SVG coordinates)
    y_coords = ((-shape_data + 1) / 2) * (height - 20) + 10

    # Create SVG path
    path_data = f"M {x_coords[0]:.1f},{y_coords[0]:.1f}"
    for x, y in zip(x_coords[1:], y_coords[1:]):
        path_data += f" L {x:.1f},{y:.1f}"

    # Color scheme based on shape characteristics
    colors = {
        'RF': '#2563eb',        # Blue for RF pulses
        'Signal': '#dc2626',    # Red for signals
        'Gradient': '#16a34a',  # Green for gradients
        'Trigger and Flag': '#ca8a04',   # Yellow for triggers
        'Flag': '#7c3aed'       # Purple for flags
    }

    return path_data, colors

def generate_svg_icon(shape_info, shape_data, output_path):
    """Generate complete SVG file for a shape"""

    width, height = 200, 100
    stroke_width = 2

    path_data, colors = create_svg_from_shape(shape_data, width, height, stroke_width)
    color = colors.get(shape_info['type'], '#374151')
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  <!-- Shape path -->
  <path d="{path_data}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

    # Write SVG file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def main():
    # Paths - make them configurable
    json_path = 'shapes.json'
    shapes_py_path = 'shapes.py'
    output_base_dir = 'svg_icons'

    # Check if files exist
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found!")
        return
    if not os.path.exists(shapes_py_path):
        print(f"Error: {shapes_py_path} not found!")
        return

    # Load shapes module
    print("Loading shapes module...")
    try:
        shapes_module = load_shapes_module(shapes_py_path)
        print("✓ Shapes module loaded successfully")
    except Exception as e:
        print(f"Error loading shapes module: {e}")
        return

    # Load JSON configuration
    print("Loading shape configurations...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✓ Loaded {len(config['shapes'])} shape configurations")
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    # Create output directory structure
    os.makedirs(output_base_dir, exist_ok=True)

    # Group shapes by type for organization
    shapes_by_type = {}
    for shape_info in config['shapes']:
        shape_type = shape_info['type']
        if shape_type not in shapes_by_type:
            shapes_by_type[shape_type] = []
        shapes_by_type[shape_type].append(shape_info)

    print(f"\nProcessing {len(config['shapes'])} shapes in {len(shapes_by_type)} categories...")
    print(f"Categories: {', '.join(shapes_by_type.keys())}")

    # Process each shape
    total_generated = 0
    errors = []

    for shape_type, shapes in shapes_by_type.items():
        print(f"\n=== {shape_type} Shapes ({len(shapes)} items) ===")

        # Create category directory
        type_dir = Path(output_base_dir) / shape_type.lower()
        type_dir.mkdir(exist_ok=True)

        for shape_info in shapes:
            try:
                # Get the class from the shapes module
                class_name = shape_info['class']
                if not hasattr(shapes_module, class_name):
                    raise AttributeError(f"Class {class_name} not found in shapes module")

                shape_class = getattr(shapes_module, class_name)

                # Get arguments for instantiation
                args = shape_info.get('args', {})

                # Instantiate the shape
                shape_instance = shape_class(**args)

                # Get the shape data
                shape_data = shape_instance.generate()

                # Validate shape data
                if shape_data is None or len(shape_data) == 0:
                    raise ValueError("Shape generated empty data")

                # Generate SVG
                svg_filename = f"{shape_info['id']}.svg"
                svg_path = type_dir / svg_filename

                generate_svg_icon(shape_info, shape_data, svg_path)

                print(f"  ✓ Generated {svg_filename}")
                total_generated += 1

            except Exception as e:
                error_msg = f"Error generating {shape_info['name']}: {str(e)}"
                print(f"  ✗ {error_msg}")
                errors.append(error_msg)

    print(f"\n=== Summary ===")
    print(f"Successfully generated {total_generated} SVG icons")
    print(f"Errors: {len(errors)}")
    if errors:
        print("Error details:")
        for error in errors:
            print(f"  - {error}")

    print(f"\nFiles saved in: {output_base_dir}/")

    # Print directory structure
    print(f"\nDirectory structure:")
    for shape_type in shapes_by_type.keys():
        type_dir = Path(output_base_dir) / shape_type.lower()
        svg_files = list(type_dir.glob("*.svg"))
        print(f"  📁 {shape_type.lower()}/  ({len(svg_files)} files)")
        for svg_file in sorted(svg_files)[:3]:  # Show first 3 files
            print(f"    📄 {svg_file.name}")
        if len(svg_files) > 3:
            print(f"    ... and {len(svg_files) - 3} more")

if __name__ == "__main__":
    main()
