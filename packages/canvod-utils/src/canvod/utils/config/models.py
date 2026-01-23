"""
Pydantic models for canvodpy configuration.

These models provide:
- Type validation for all configuration values
- Serialization support (YAML/JSON/dict)
- API-ready data transfer objects
- IDE autocomplete and type hints
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================================
# Processing Configuration
# ============================================================================


class CredentialsConfig(BaseModel):
    """Credentials and paths."""

    cddis_mail: Optional[EmailStr] = Field(
        None,
        description="NASA CDDIS email for authentication (optional)",
    )
    gnss_root_dir: Path = Field(
        ...,
        description="Root directory for all GNSS data",
    )

    @field_validator("gnss_root_dir")
    @classmethod
    def validate_root_dir_exists(cls, v: Path) -> Path:
        """Ensure root directory exists."""
        if not v.exists():
            msg = f"GNSS root directory does not exist: {v}"
            raise ValueError(msg)
        return v


class AuxDataConfig(BaseModel):
    """Auxiliary data source configuration."""

    agency: str = Field("COD", description="Analysis center code")
    product_type: Literal["final", "rapid", "ultra-rapid"] = Field(
        "final",
        description="Product type",
    )

    def get_ftp_servers(
        self,
        cddis_mail: Optional[str],
    ) -> list[tuple[str, Optional[str]]]:
        """
        Get FTP servers in priority order.

        If cddis_mail is set: NASA first (with auth), ESA fallback (no auth)
        If cddis_mail is None: ESA only (no auth)

        Args:
            cddis_mail: Optional CDDIS email for NASA authentication

        Returns:
            List of (server_url, auth_email) tuples in priority order
        """
        if cddis_mail:
            # NASA first (requires auth), ESA fallback (no auth)
            return [
                ("ftp://gdc.cddis.eosdis.nasa.gov", cddis_mail),
                ("ftp://gssc.esa.int/gnss", None),
            ]
        # ESA only (no auth required)
        return [("ftp://gssc.esa.int/gnss", None)]


class ProcessingParams(BaseModel):
    """Processing parameters."""

    time_aggregation_seconds: int = Field(
        15,
        ge=1,
        le=300,
        description="Time aggregation window in seconds",
    )
    n_max_threads: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of threads for parallel processing",
    )
    keep_rnx_vars: list[str] = Field(
        default_factory=lambda: ["SNR"],
        description="RINEX variables to keep",
    )
    aggregate_glonass_fdma: bool = Field(
        True,
        description="Treat GLONASS FDMA bands as one band",
    )


class CompressionConfig(BaseModel):
    """Compression settings."""

    zlib: bool = Field(True, description="Use zlib compression")
    complevel: int = Field(5, ge=0, le=9, description="Compression level")


class ChunkStrategy(BaseModel):
    """Chunking strategy for a dimension."""

    epoch: int = Field(34560, ge=1, description="Chunk size for epoch dimension")
    sid: int = Field(-1, ge=-1, description="Chunk size for sid (-1 = don't chunk)")


class IcechunkConfig(BaseModel):
    """Icechunk storage configuration."""

    compression_level: int = Field(5, ge=0, le=22)
    compression_algorithm: Literal["zstd", "lz4", "gzip"] = "zstd"
    inline_threshold: int = Field(512, ge=0)
    get_concurrency: int = Field(1, ge=1)
    chunk_strategies: dict[str, ChunkStrategy] = Field(
        default_factory=lambda: {
            "rinex_store": ChunkStrategy(epoch=34560, sid=-1),
            "vod_store": ChunkStrategy(epoch=34560, sid=-1),
        },
    )


class StorageConfig(BaseModel):
    """Storage strategy configuration."""

    stores_root_dir: Path = Field(
        ...,
        description="Root directory for all IceChunk stores",
    )
    rinex_store_strategy: Literal["skip", "overwrite", "append"] = "skip"
    rinex_store_expire_days: int = Field(2, ge=1)
    vod_store_strategy: Literal["skip", "overwrite", "append"] = "overwrite"

    @field_validator("stores_root_dir")
    @classmethod
    def validate_stores_dir(cls, v: Path) -> Path:
        """Create stores directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_rinex_store_path(self, site_name: str) -> Path:
        """Get RINEX store path for a site."""
        return self.stores_root_dir / site_name / "rinex"

    def get_vod_store_path(self, site_name: str) -> Path:
        """Get VOD store path for a site."""
        return self.stores_root_dir / site_name / "vod"


class ProcessingConfig(BaseModel):
    """Complete processing configuration."""

    credentials: CredentialsConfig
    aux_data: AuxDataConfig = Field(default_factory=AuxDataConfig)
    processing: ProcessingParams = Field(default_factory=ProcessingParams)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    icechunk: IcechunkConfig = Field(default_factory=IcechunkConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)


# ============================================================================
# Sites Configuration
# ============================================================================


class ReceiverConfig(BaseModel):
    """Receiver configuration."""

    type: Literal["reference", "canopy"] = Field(..., description="Receiver type")
    directory: str = Field(..., description="Subdirectory for receiver data")
    description: Optional[str] = Field(None, description="Human-readable description")


class VodAnalysisConfig(BaseModel):
    """VOD analysis pair configuration."""

    canopy_receiver: str = Field(..., description="Canopy receiver name")
    reference_receiver: str = Field(..., description="Reference receiver name")
    description: Optional[str] = Field(None, description="Analysis description")


class SiteConfig(BaseModel):
    """Research site configuration."""

    base_dir: str = Field(..., description="Base directory for site data")
    receivers: dict[str, ReceiverConfig] = Field(..., description="Site receivers")
    vod_analyses: Optional[dict[str, VodAnalysisConfig]] = Field(
        None,
        description="VOD analysis pairs",
    )

    def get_base_path(self) -> Path:
        """Get base_dir as Path object."""
        return Path(self.base_dir)


class SitesConfig(BaseModel):
    """All research sites."""

    sites: dict[str, SiteConfig]

    @field_validator("sites")
    @classmethod
    def validate_at_least_one_site(cls, v: dict) -> dict:
        """Ensure at least one site is defined."""
        if not v:
            msg = "At least one research site must be defined"
            raise ValueError(msg)
        return v


# ============================================================================
# SIDs Configuration
# ============================================================================


class SidsConfig(BaseModel):
    """Signal ID configuration."""

    mode: Literal["all", "preset", "custom"] = Field(
        "all",
        description="SID selection mode",
    )
    preset: Optional[str] = Field(None, description="Preset name when mode=preset")
    custom_sids: list[str] = Field(
        default_factory=list,
        description="Custom SID list when mode=custom",
    )

    @field_validator("preset")
    @classmethod
    def validate_preset_when_mode_preset(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure preset is set when mode is preset."""
        mode = info.data.get("mode")
        if mode == "preset" and not v:
            msg = "preset must be specified when mode is 'preset'"
            raise ValueError(msg)
        return v

    def get_sids(self) -> list[str] | None:
        """
        Get effective SID list.

        Returns:
            None if mode is 'all' (keep all SIDs)
            List of SIDs otherwise
        """
        if self.mode == "all":
            return None
        if self.mode == "preset":
            return self._get_preset_sids()
        # CUSTOM
        return self.custom_sids

    def _get_preset_sids(self) -> list[str]:
        """Load preset SID list."""
        # TODO: Implement preset loading from package defaults
        # For now, return empty list
        return []


# ============================================================================
# Complete Configuration
# ============================================================================


class CanvodConfig(BaseModel):
    """
    Complete canvodpy configuration.

    This is the top-level configuration object that combines all
    configuration sections. It's fully serializable and can be used
    for local development (YAML files) or API-based configuration.
    """

    processing: ProcessingConfig
    sites: SitesConfig
    sids: SidsConfig

    model_config = {"extra": "forbid"}  # Catch typos in config files!

    @property
    def gnss_root_dir(self) -> Path:
        """Shortcut to root directory."""
        return self.processing.credentials.gnss_root_dir

    @property
    def cddis_mail(self) -> Optional[str]:
        """Shortcut to CDDIS mail."""
        return self.processing.credentials.cddis_mail
