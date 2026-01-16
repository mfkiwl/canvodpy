"""Product registry and specifications for IGS analysis centers."""

from canvod.aux.products.registry import (
    PRODUCT_REGISTRY,
    ProductSpec,
    get_product_spec,
    list_available_products,
    list_agencies,
    get_products_for_agency,
)
from canvod.aux.products.models import (
    Sp3Header,
    ClkHeader,
    ProductRequest,
    FileValidationResult,
)

__all__ = [
    # Registry
    "PRODUCT_REGISTRY",
    "ProductSpec",
    "get_product_spec",
    "list_available_products",
    "list_agencies",
    "get_products_for_agency",
    # Models
    "Sp3Header",
    "ClkHeader",
    "ProductRequest",
    "FileValidationResult",
]
