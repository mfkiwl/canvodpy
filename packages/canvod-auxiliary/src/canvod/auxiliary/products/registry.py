"""Product registry for IGS analysis centers and their specifications."""

from dataclasses import dataclass


@dataclass
class ProductSpec:
    """Specification for an IGS product.

    Notes
    -----
    This is a standard dataclass.

    Parameters
    ----------
    agency_code : str
        3-letter code (COD, GFZ, ESA, JPL, IGS, etc.).
    agency_name : str
        Full name of the analysis center.
    product_type : str
        Product type (final, rapid, ultrarapid, predicted).
    prefix : str
        Filename prefix following IGS conventions.
    sampling_rate : str
        Temporal resolution (05M, 15M, 30S, etc.).
    duration : str
        File duration (01D, 03D, etc.).
    available_formats : list[str]
        List of available file formats.
    ftp_path_pattern : str
        URL pattern with placeholders.
    latency_hours : int
        Typical latency in hours from epoch.
    description : str
        Optional description.
    """

    agency_code: str
    agency_name: str
    product_type: str
    prefix: str
    sampling_rate: str
    duration: str
    available_formats: list[str]
    ftp_path_pattern: str
    latency_hours: int
    description: str = ""


# Product Registry
# Format: (AGENCY_CODE, PRODUCT_TYPE) -> ProductSpec
PRODUCT_REGISTRY: dict[tuple[str, str], ProductSpec] = {
    # ========================================
    # CODE (Center for Orbit Determination in Europe)
    # ========================================
    ("COD", "final"): ProductSpec(
        agency_code="COD",
        agency_name="Center for Orbit Determination in Europe",
        product_type="final",
        prefix="COD0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=168,  # ~7 days
        description="CODE final multi-GNSS orbits and clocks",
    ),
    ("COD", "rapid"): ProductSpec(
        agency_code="COD",
        agency_name="Center for Orbit Determination in Europe",
        product_type="rapid",
        prefix="COD0OPSRAP",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=17,  # ~17 hours
        description="CODE rapid multi-GNSS orbits and clocks",
    ),
    # ========================================
    # GFZ (GeoForschungsZentrum Potsdam)
    # Note: GFZ products use different naming conventions by date:
    #   - GPS week <2038 (before Jan 27, 2019): Short name format "gbm"
    #     (not yet supported)
    #   - GPS week >=2038 (Jan 27, 2019+): Long name format "GFZ0MGXRAP" (supported)
    # ========================================
    ("GFZ", "final"): ProductSpec(
        agency_code="GFZ",
        agency_name="GeoForschungsZentrum Potsdam",
        product_type="final",
        prefix="GFZ0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=336,  # ~14 days
        description="GFZ final multi-GNSS orbits and clocks",
    ),
    ("GFZ", "rapid"): ProductSpec(
        agency_code="GFZ",
        agency_name="GeoForschungsZentrum Potsdam",
        product_type="rapid",
        prefix="GFZ0MGXRAP",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=17,  # ~17 hours
        description="GFZ rapid multi-GNSS orbits and clocks",
    ),
    # ========================================
    # ESA (European Space Agency)
    # ========================================
    ("ESA", "final"): ProductSpec(
        agency_code="ESA",
        agency_name="European Space Agency",
        product_type="final",
        prefix="ESA0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=168,  # ~7 days
        description="ESA final multi-GNSS orbits and clocks",
    ),
    ("ESA", "rapid"): ProductSpec(
        agency_code="ESA",
        agency_name="European Space Agency",
        product_type="rapid",
        prefix="ESA0MGXRAP",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=17,  # ~17 hours
        description="ESA rapid multi-GNSS orbits and clocks",
    ),
    # ========================================
    # JPL (Jet Propulsion Laboratory)
    # ========================================
    ("JPL", "final"): ProductSpec(
        agency_code="JPL",
        agency_name="Jet Propulsion Laboratory",
        product_type="final",
        prefix="JPL0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=240,  # ~10 days
        description="JPL final multi-GNSS orbits and clocks",
    ),
    ("JPL", "rapid"): ProductSpec(
        agency_code="JPL",
        agency_name="Jet Propulsion Laboratory",
        product_type="rapid",
        prefix="JPL0MGXRAP",
        sampling_rate="15M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=24,  # ~24 hours
        description="JPL rapid multi-GNSS orbits and clocks",
    ),
    # ========================================
    # IGS (International GNSS Service)
    # ========================================
    ("IGS", "final"): ProductSpec(
        agency_code="IGS",
        agency_name="International GNSS Service",
        product_type="final",
        prefix="IGS0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=336,  # ~14 days
        description="IGS combined final multi-GNSS orbits and clocks",
    ),
    ("IGS", "rapid"): ProductSpec(
        agency_code="IGS",
        agency_name="International GNSS Service",
        product_type="rapid",
        prefix="IGS0MGXRAP",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=17,  # ~17 hours
        description="IGS combined rapid multi-GNSS orbits and clocks",
    ),
    # ========================================
    # WHU (Wuhan University)
    # ========================================
    ("WHU", "final"): ProductSpec(
        agency_code="WHU",
        agency_name="Wuhan University",
        product_type="final",
        prefix="WHU0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=168,  # ~7 days
        description="WHU final multi-GNSS orbits and clocks",
    ),
    # ========================================
    # CNES (Centre National d'Études Spatiales)
    # ========================================
    ("GRG", "final"): ProductSpec(
        agency_code="GRG",
        agency_name="Centre National d'Études Spatiales",
        product_type="final",
        prefix="GRG0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=192,  # ~8 days
        description="CNES/GRG final multi-GNSS orbits and clocks",
    ),
    # ========================================
    # SHA (Shanghai Observatory)
    # ========================================
    ("SHA", "final"): ProductSpec(
        agency_code="SHA",
        agency_name="Shanghai Observatory",
        product_type="final",
        prefix="SHA0MGXFIN",
        sampling_rate="05M",
        duration="01D",
        available_formats=["SP3", "CLK"],
        ftp_path_pattern="/gnss/products/{gps_week}/{file}",
        latency_hours=168,  # ~7 days
        description="SHA final multi-GNSS orbits and clocks",
    ),
}


def get_product_spec(agency: str, product_type: str) -> ProductSpec:
    """
    Get product specification for a given agency and product type.

    Args:
        agency: Agency code (e.g., 'COD', 'GFZ', 'ESA')
        product_type: Product type (e.g., 'final', 'rapid')

    Returns:
        ProductSpec object

    Raises:
        ValueError: If product is not supported

    Example:
        >>> spec = get_product_spec('COD', 'final')
        >>> print(spec.prefix)
        'COD0MGXFIN'
    """
    key = (agency.upper(), product_type.lower())
    if key not in PRODUCT_REGISTRY:
        available = list(PRODUCT_REGISTRY.keys())
        raise ValueError(
            f"Product {agency}/{product_type} not supported.\n"
            f"Available products: {available}"
        )
    return PRODUCT_REGISTRY[key]


def list_available_products() -> list[tuple[str, str]]:
    """
    List all available products in the registry.

    Returns:
        List of (agency_code, product_type) tuples

    Example:
        >>> products = list_available_products()
        >>> print(products[:3])
        [('COD', 'final'), ('COD', 'rapid'), ('GFZ', 'final')]
    """
    return list(PRODUCT_REGISTRY.keys())


def list_agencies() -> list[str]:
    """
    List all available analysis centers.

    Returns:
        Sorted list of unique agency codes

    Example:
        >>> agencies = list_agencies()
        >>> print(agencies)
        ['COD', 'ESA', 'GFZ', 'GRG', 'IGS', 'JPL', 'SHA', 'WHU']
    """
    return sorted(set(agency for agency, _ in PRODUCT_REGISTRY.keys()))


def get_products_for_agency(agency: str) -> list[str]:
    """
    Get all product types available for a specific agency.

    Args:
        agency: Agency code

    Returns:
        List of product types

    Example:
        >>> products = get_products_for_agency('COD')
        >>> print(products)
        ['final', 'rapid']
    """
    agency_upper = agency.upper()
    return [
        product_type
        for (ag, product_type) in PRODUCT_REGISTRY.keys()
        if ag == agency_upper
    ]


if __name__ == "__main__":
    # Example usage
    spec = get_product_spec("COD", "final")
    print(spec)

    products = list_available_products()
    print(products)

    agencies = list_agencies()
    print(agencies)

    cod_products = get_products_for_agency("COD")
    print(cod_products)
