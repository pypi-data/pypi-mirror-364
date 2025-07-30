# YAML Tkinter

A utility for building Tkinter widget trees from YAML files.

This module provides the `Builder` class, which reads a YAML file describing the 
widget hierarchy and properties, then instantiates and configures Tkinter widgets 
accordingly. It supports custom branch classes, variable binding, and flexible 
widget configuration, making it easy to define complex GUIs declaratively.

YAML files should specify the widget structure, options, and variables. See the 
example YAML and widget classes for details.

## Install

`pip install yamltk`

## Demo

```python
import tkinter as tk
import yamltk

class Demo(tk.Tk):
    yaml_file = 'demo.yaml'

root = yamltk.build(Demo)
root.mainloop()
```

demo.yaml:

```yaml
Demo:
    title: Demo application
    geometry: 300x200
    children:
        - Label:
            text: Hello world!
            pack: top
```

For more details, see the example folder.