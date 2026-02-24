"""Product registry and specifications for IGS analysis centers."""

from canvod.auxiliary.products.models import (
    ClkHeader,
    FileValidationResult,
    ProductRequest,
    Sp3Header,
)
from canvod.auxiliary.products.registry_config import (
    FtpServerConfig,
    ProductRegistry,
    ProductSpec,
    get_product_spec,
    get_products_for_agency,
    get_registry,
    list_agencies,
    list_products,
)

__all__ = [
    # Registry
    "FtpServerConfig",
    "ProductRegistry",
    "ProductSpec",
    "get_product_spec",
    "get_registry",
    "list_products",
    "list_agencies",
    "get_products_for_agency",
    # Models
    "Sp3Header",
    "ClkHeader",
    "ProductRequest",
    "FileValidationResult",
]
