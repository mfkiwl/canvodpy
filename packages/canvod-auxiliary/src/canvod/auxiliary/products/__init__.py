"""Product registry and specifications for IGS analysis centers."""

from canvod.auxiliary.products.models import (
    ClkHeader,
    FileValidationResult,
    ProductRequest,
    Sp3Header,
)
from canvod.auxiliary.products.registry import (
    PRODUCT_REGISTRY,
    ProductSpec,
    get_product_spec,
    get_products_for_agency,
    list_agencies,
    list_available_products,
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
