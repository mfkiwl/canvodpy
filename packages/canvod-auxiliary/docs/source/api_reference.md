# API Reference

Complete API documentation for canvod-auxiliary.

## File Handlers

### Sp3File

```{eval-rst}
.. autoclass:: canvod.aux.Sp3File
   :members:
   :undoc-members:
   :show-inheritance:
```

### ClkFile

```{eval-rst}
.. autoclass:: canvod.aux.ClkFile
   :members:
   :undoc-members:
   :show-inheritance:
```

## Preprocessing

### preprocess_aux_for_interpolation

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.preprocess_aux_for_interpolation
```

### prep_aux_ds

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.prep_aux_ds
```

### map_aux_sv_to_sid

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.map_aux_sv_to_sid
```

### pad_to_global_sid

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.pad_to_global_sid
```

### normalize_sid_dtype

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.normalize_sid_dtype
```

### strip_fillvalue

```{eval-rst}
.. autofunction:: canvod.aux.preprocessing.strip_fillvalue
```

## Interpolation

### Sp3InterpolationStrategy

```{eval-rst}
.. autoclass:: canvod.aux.interpolation.Sp3InterpolationStrategy
   :members:
   :undoc-members:
   :show-inheritance:
```

### ClockInterpolationStrategy

```{eval-rst}
.. autoclass:: canvod.aux.interpolation.ClockInterpolationStrategy
   :members:
   :undoc-members:
   :show-inheritance:
```

### Sp3Config

```{eval-rst}
.. autoclass:: canvod.aux.interpolation.Sp3Config
   :members:
   :undoc-members:
```

### ClockConfig

```{eval-rst}
.. autoclass:: canvod.aux.interpolation.ClockConfig
   :members:
   :undoc-members:
```

## Position & Coordinates

### ECEFPosition

```{eval-rst}
.. autoclass:: canvod.aux.ECEFPosition
   :members:
   :undoc-members:
   :show-inheritance:
```

### GeodeticPosition

```{eval-rst}
.. autoclass:: canvod.aux.GeodeticPosition
   :members:
   :undoc-members:
   :show-inheritance:
```

### compute_spherical_coordinates

```{eval-rst}
.. autofunction:: canvod.aux.position.compute_spherical_coordinates
```

### add_spherical_coords_to_dataset

```{eval-rst}
.. autofunction:: canvod.aux.position.add_spherical_coords_to_dataset
```

## Products

### get_product_spec

```{eval-rst}
.. autofunction:: canvod.aux.products.get_product_spec
```

### list_available_products

```{eval-rst}
.. autofunction:: canvod.aux.products.list_available_products
```

### list_agencies

```{eval-rst}
.. autofunction:: canvod.aux.products.list_agencies
```

### ProductSpec

```{eval-rst}
.. autoclass:: canvod.aux.products.ProductSpec
   :members:
   :undoc-members:
```

## Dataset Matching

### DatasetMatcher

```{eval-rst}
.. autoclass:: canvod.aux.DatasetMatcher
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- [Overview](overview.md) for usage examples
- [Preprocessing Guide](preprocessing.md) for detailed workflow
- [Interpolation](interpolation.md) for interpolation strategies
