====================================
Magnetic Resonance Diagram Library
====================================

Under construction!

A Python library for creating, visualizing, and sharing magnetic resonance (MR) pulse sequence diagrams with mathematical precision and graphical flexibility.

Overview
========

This library provides standardized tools for diagramming MR sequences with both mathematical representations and visual components. It enables researchers to create accurate, reproducible sequence documentation.

**Design Principle**: Use parametric flexibility rather than creating multiple similar classes. For example, use one SincShape class with different bandwidth parameters instead of creating separate classes for each variation. Also, use this feature only if you really want to
distinguish between different parameters, check the icon generation within the plot.

**Normalization**: All shapes are normalized to the range [-1, 1] for consistent amplitude representation across different shape types.

Shape Categories
================

RF Shapes
---------

Radiofrequency pulses for spin excitation and manipulation.

**Examples:**

- ``RectangularShape``: Hard pulse for broadband excitation
- ``SincShape``: Sinc pulse for slice selection
- ``GaussianShape``: Gaussian envelope pulse
- ``AdiabaticShape``: Adiabatic hyperbolic secant pulse
- ``SLRShape``: Shinnar-Le Roux optimized pulse
- ``VerseShape``: Variable-rate selective excitation
- ``FermiShape``: Fermi transition pulse
- ``SPSPShape``: Spectral-spatial pulse
- ``CompositeShape``: Multi-component pulse
- ``DanteShape``: Delays alternating with nutations
- ``HammingSincShape``: Hamming-windowed sinc pulse
- ``ChessShape``: Chemical shift selective pulse
- ``HyperbolicSecantShape``: Hyperbolic secant adiabatic pulse
- ``BIRShape``: B1-independent rotation pulse

Gradient Shapes
---------------

Spatial encoding gradients for image formation and slice selection.

**Examples:**

- ``TrapezoidShape``: Standard imaging gradient with configurable rise/plateau/fall
- ``SpiralShape``: For spiral k-space trajectories
- ``RadialShape``: For radial sampling patterns
- ``EPIShape``: Echo planar imaging gradients
- ``BipolarShape``: Bipolar gradient for velocity encoding
- ``CrusherShape``: Spoiler gradient for coherence elimination
- ``RampUpShape``: Linear ramp up gradient
- ``RampDownShape``: Linear ramp down gradient

Signal Shapes
-------------

Detected MR signals including free induction decay and echo formations.

**Examples:**

- ``FIDShape``: Free induction decay with T2* decay
- ``EchoShape``: Spin/gradient echo signals with T2 decay
- ``STIRShape``: Short TI inversion recovery signal

Trigger Shapes
--------------

Hardware synchronization pulses for sequence timing control.

**Examples:**

- ``TriggerShape``: Basic hardware synchronization pulse

Flag Shapes
-----------

Logical markers for sequence events and timing references.

**Examples:**

- ``FlagShape``: Single-point event marker

Shape Definition Structure
==========================

Each shape instance is defined with the following properties in JSON format:

Properties
----------

- **id**: Unique identifier for database and reference purposes
- **name**: Human-readable short name for UI display
- **description**: Detailed explanation of the shape's characteristics and applications
- **type**: Category classification (RF, Gradient, Signal, Trigger, Flag, General)
- **tags**: Keywords for search and categorization (list of words)
- **usage**: Primary application scenarios
- **selectivity**: Spatial selectivity characteristics (Low, Medium, High, Tunable, Not Applicable)
- **duration**: Typical temporal extent (Short, Medium, Long)
- **sar**: Specific Absorption Rate impact (Low, Medium, High, Not Applicable)
- **class**: Python class name in ``shapes.py``
- **args**: Constructor arguments with default values (dictionary)

Usage Examples
==============

Creating a Sinc Pulse
---------------------

.. code-block:: json

    {
        "id": "sinc",
        "name": "Sinc",
        "description": "Sinc pulse for slice-selective excitation",
        "type": "RF",
        "selectivity": "medium",
        "duration": "medium",
        "usage": "Slice-selective excitation, standard imaging",
        "tags": ["selective", "slice selection", "sinc"],
        "sar": "medium",
        "class": "SincShape",
        "args": {
            "num_points": 100,
            "bandwidth": 4
        }
    }

Creating a DANTE Pulse Train
----------------------------

.. code-block:: json

    {
        "id": "dante",
        "name": "DANTE",
        "description": "Delays Alternating with Nutations for Tailored Excitation",
        "type": "RF",
        "selectivity": "high",
        "duration": "long",
        "usage": "Frequency-selective excitation, CSI suppression, flow imaging",
        "tags": ["selective", "multi-pulse", "frequency selective", "small flip"],
        "sar": "low",
        "class": "DanteShape",
        "args": {
            "num_points": 100,
            "num_pulses": 12,
            "pulse_width": 0.08,
            "spacing": 0.32
        }
    }

Creating a Trapezoid Gradient
-----------------------------

.. code-block:: json

    {
        "id": "trapezoid",
        "name": "Trapezoid",
        "description": "Trapezoidal gradient waveform with controlled slew rate",
        "type": "Gradient",
        "selectivity": "not_applicable",
        "duration": "medium",
        "usage": "Readout encoding, phase encoding, slice selection",
        "tags": ["encoding", "trapezoid", "slew rate", "spatial"],
        "sar": "not_applicable",
        "class": "TrapezoidShape",
        "args": {
            "num_points": 100,
            "rise_fraction": 0.2,
            "plateau_fraction": 0.6,
            "fall_fraction": 0.2
        }
    }

Python Usage Examples
=====================

Using Shapes in Python Code
----------------------------

.. code-block:: python

    from shapes import GaussianShape, TrapezoidShape

    # Create a Gaussian RF pulse
    rf_pulse = GaussianShape(num_points=200, sigma=0.4)
    rf_data = rf_pulse.generate()  # Returns normalized data in [-1, 1]

    # Create a trapezoidal gradient
    gradient = TrapezoidShape(
        num_points=150,
        rise_fraction=0.15,
        plateau_fraction=0.7,
        fall_fraction=0.15
    )
    grad_data = gradient.generate()  # Returns normalized data in [-1, 1]

    # All shapes are normalized to [-1, 1] range
    print(f"RF pulse range: [{rf_data.min():.3f}, {rf_data.max():.3f}]")
    print(f"Gradient range: [{grad_data.min():.3f}, {grad_data.max():.3f}]")

Plotting Shapes
---------------

.. code-block:: python

    import matplotlib.pyplot as plt
    import numpy as np
    from shapes import SincShape, EchoShape

    # Create and plot a Sinc pulse
    sinc_pulse = SincShape(num_points=100, bandwidth=5)
    time_axis = np.linspace(0, 1, 100)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(time_axis, sinc_pulse.shape)
    plt.title('Sinc RF Pulse')
    plt.xlabel('Normalized Time')
    plt.ylabel('Amplitude')
    plt.grid(True)

    # Create and plot an Echo signal
    echo_signal = EchoShape(num_points=100, t2=80, echo_time=50)
    plt.subplot(1, 2, 2)
    plt.plot(time_axis, echo_signal.shape)
    plt.title('Echo Signal')
    plt.xlabel('Normalized Time')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

File Structure
==============

::

    mrdiagram/
    ├── plot.py            # GUI application for shape management
    ├── shapes.py          # Core shape classes and mathematical implementations
    ├── shapes.json        # Shape metadata and configuration database
    └── README.rst         # This documentation

GUI Application
===============

The library includes a comprehensive GUI application for managing and visualizing shapes,
which also enables the user to edit the JSON file:

.. code-block:: bash

    python plot.py

Features:

- **Database Management**: View all shapes in a sortable table
- **Parameter Editing**: Edit shape parameters with appropriate input controls
- **Real-time Visualization**: See shape changes immediately
- **64x64/32X32 Icon Preview**: Quality check with miniature shape icon
- **JSON Import/Export**: Load and save shape databases
- **Add/Delete Shapes**: Manage the shape database

Extension Guidelines
====================

Adding New Shapes
-----------------

Before adding new shapes, check if existing parametric shapes can be configured for your needs.
If the shape you want exists but the parameters are not sufficient, try to improve the current one.

1. **Create the class** in ``shapes.py`` inheriting from ``Shape``
2. **Implement the ``generate()`` method** with appropriate mathematical implementation
3. **Use the ``normalize()`` method** to ensure output is in [-1, 1] range
4. **Add metadata** to the JSON configuration file
5. **Use parameters** instead of creating multiple similar classes

Example Shape Implementation
----------------------------

.. code-block:: python

    class MyCustomShape(Shape):
        def __init__(self, num_points: int = 100, custom_param: float = 1.0):
            super().__init__(num_points)
            self.custom_param = custom_param
            self.generate()

        def generate(self):
            t = numpy.linspace(-2, 2, self.num_points)
            raw_shape = numpy.sin(self.custom_param * numpy.pi * t)
            self.shape = self.normalize(raw_shape)  # Normalize to [-1, 1]
            return self.shape

Normalization
=============

All shapes are automatically normalized to the range [-1, 1] using the ``normalize()`` method in the base ``Shape`` class. This ensures:

- **Consistent Amplitude Range**: All shapes have the same amplitude scale
- **Easy Comparison**: Different shapes can be compared directly
- **Standardized Output**: Predictable amplitude range for all applications
- **Mathematical Consistency**: Removes scaling differences between shape types

Contributing
============

When contributing new shapes or features:

1. Follow the existing naming conventions
2. Include comprehensive mathematical documentation
3. Provide realistic default parameters
4. Add appropriate metadata to the JSON configuration
5. Test shape generation across different point counts
6. Ensure all shapes are properly normalized to [-1, 1]
7. Test integration with the GUI application

Dependencies
============

- **numpy**: Mathematical operations and array handling
- **PyQt5**: GUI framework (plot.py)
- **pyqtgraph**: High-performance plotting (for GUI)
- **json**: Database management
- **inspect**: Dynamic class introspection

Installation
============

.. code-block:: bash

    pip install numpy PyQt5 pyqtgraph

License
=======

MIT License

Citation
========

This tool is free to use. Please cite using the Zenodo DOI when publishing work that uses this library.

The repository has a Zenodo identifier which provides a DOI that can be referenced properly in academic publications.
