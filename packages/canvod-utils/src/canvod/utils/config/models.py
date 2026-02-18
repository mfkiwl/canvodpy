"""
Pydantic models for canvodpy configuration.

These models provide:
- Type validation for all configuration values
- Serialization support (YAML/JSON/dict)
- API-ready data transfer objects
- IDE autocomplete and type hints
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

# ============================================================================
# Processing Configuration
# ============================================================================


class MetadataConfig(BaseModel):
    """Metadata to be written to processed files.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

    author: str = Field(..., description="Author name")
    email: EmailStr = Field(..., description="Author email")
    institution: str = Field(..., description="Institution name")
    department: str | None = Field(None, description="Department name")
    research_group: str | None = Field(
        None,
        description="Research group name",
    )
    website: str | None = Field(
        None,
        description="Institution/group website",
    )

    def to_attrs_dict(self) -> dict[str, str]:
        """Convert to a dictionary for xarray attributes.

        Returns
        -------
        dict[str, str]
            Metadata as xarray-compatible attributes.
        """
        attrs = {
            "author": self.author,
            "email": self.email,
            "institution": self.institution,
        }
        if self.department:
            attrs["department"] = self.department
        if self.research_group:
            attrs["research_group"] = self.research_group
        if self.website:
            attrs["website"] = self.website
        return attrs


class CredentialsConfig(BaseModel):
    """Credentials for external data services.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

    nasa_earthdata_acc_mail: EmailStr | None = Field(
        None,
        description="NASA Earthdata email for CDDIS authentication (optional)",
    )


class AuxDataConfig(BaseModel):
    """Auxiliary data source configuration.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

    agency: str = Field("COD", description="Analysis center code")
    product_type: Literal["final", "rapid", "ultra-rapid"] = Field(
        "final",
        description="Product type",
    )

    def get_ftp_servers(
        self,
        cddis_mail: str | None,
    ) -> list[tuple[str, str | None]]:
        """Get FTP servers in priority order.

        If cddis_mail is set: NASA first (with auth), ESA fallback (no auth).
        If cddis_mail is None: ESA only (no auth).

        Parameters
        ----------
        cddis_mail : str | None
            Optional CDDIS email for NASA authentication.

        Returns
        -------
        list[tuple[str, str | None]]
            Server URL and optional auth email pairs in priority order.
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
    """Processing parameters.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

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
    """Compression settings.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

    zlib: bool = Field(True, description="Use zlib compression")
    complevel: int = Field(5, ge=0, le=9, description="Compression level")


class ChunkStrategy(BaseModel):
    """Chunking strategy for a dimension.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

    epoch: int = Field(
        34560,
        ge=1,
        description="Chunk size for epoch dimension",
    )
    sid: int = Field(
        -1,
        ge=-1,
        description="Chunk size for sid (-1 = don't chunk)",
    )


class IcechunkConfig(BaseModel):
    """Icechunk storage configuration.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

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
    """Storage strategy configuration.

    Notes
    -----
    This is a Pydantic model for configuration validation.
    """

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
        """Validate stores directory path.

        Parameters
        ----------
        v : Path
            Directory where stores are created.

        Returns
        -------
        Path
            Validated path.
        """
        # Only validate if it looks like a real path (not a placeholder)
        path_str = str(v)
        if path_str.startswith("/path/"):
            # This is a placeholder path from defaults - skip validation
            return v

        # For real paths, create if it doesn't exist
        if not v.exists():
            try:
                v.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                # Warn but don't fail - let user create it manually
                import warnings

                warnings.warn(
                    f"Could not create stores directory {v}: {e}. "
                    "Please create it manually.",
                    UserWarning,
                    stacklevel=2,
                )
        return v

    def get_rinex_store_path(self, site_name: str) -> Path:
        """Get the RINEX store path for a site.

        Parameters
        ----------
        site_name : str
            Site name.

        Returns
        -------
        Path
            Path to the site's RINEX store.
        """
        return self.stores_root_dir / site_name / "rinex"

    def get_vod_store_path(self, site_name: str) -> Path:
        """Get the VOD store path for a site.

        Parameters
        ----------
        site_name : str
            Site name.

        Returns
        -------
        Path
            Path to the site's VOD store.
        """
        return self.stores_root_dir / site_name / "vod"


class ProcessingConfig(BaseModel):
    """Complete processing configuration."""

    metadata: MetadataConfig
    credentials: CredentialsConfig = Field(
        default_factory=CredentialsConfig,
        description="Credentials for external data services",
    )
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

    type: Literal["reference", "canopy"] = Field(
        ...,
        description="Receiver type",
    )
    directory: str = Field(..., description="Subdirectory for receiver data")
    description: str | None = Field(
        None,
        description="Human-readable description",
    )


class VodAnalysisConfig(BaseModel):
    """VOD analysis pair configuration."""

    canopy_receiver: str = Field(..., description="Canopy receiver name")
    reference_receiver: str = Field(..., description="Reference receiver name")
    description: str | None = Field(None, description="Analysis description")


class SiteConfig(BaseModel):
    """Research site configuration."""

    gnss_site_data_root: str = Field(
        ..., description="Root directory for site GNSS data"
    )
    receivers: dict[str, ReceiverConfig] = Field(..., description="Site receivers")
    vod_analyses: dict[str, VodAnalysisConfig] | None = Field(
        None,
        description="VOD analysis pairs",
    )

    def get_base_path(self) -> Path:
        """Get gnss_site_data_root as a Path.

        Returns
        -------
        Path
            Site data root directory as a Path object.
        """
        return Path(self.gnss_site_data_root)


class SitesConfig(BaseModel):
    """All research sites."""

    sites: dict[str, SiteConfig]

    @field_validator("sites")
    @classmethod
    def validate_at_least_one_site(
        cls,
        v: dict[str, "SiteConfig"],
    ) -> dict[str, "SiteConfig"]:
        """Ensure at least one site is defined.

        Parameters
        ----------
        v : dict[str, SiteConfig]
            Sites dictionary to validate.

        Returns
        -------
        dict[str, SiteConfig]
            Validated sites dictionary.
        """
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
    preset: str | None = Field(
        None,
        description="Preset name when mode=preset",
    )
    custom_sids: list[str] = Field(
        default_factory=list,
        description="Custom SID list when mode=custom",
    )

    @field_validator("preset")
    @classmethod
    def validate_preset_when_mode_preset(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Ensure preset is set when mode is preset.

        Parameters
        ----------
        v : str | None
            Preset name.
        info : ValidationInfo
            Pydantic validation info.

        Returns
        -------
        str | None
            Preset value if valid.
        """
        mode = info.data.get("mode")
        if mode == "preset" and not v:
            msg = "preset must be specified when mode is 'preset'"
            raise ValueError(msg)
        return v

    def get_sids(self) -> list[str] | None:
        """Get the effective SID list.

        Returns
        -------
        list[str] | None
            None if mode is "all" (keep all SIDs), otherwise a SID list.
        """
        if self.mode == "all":
            return None
        if self.mode == "preset":
            return self._get_preset_sids()
        # CUSTOM
        return self.custom_sids

    def _get_preset_sids(self) -> list[str]:
        """Load the preset SID list.

        Returns
        -------
        list[str]
            Preset SID list.
        """
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
    def nasa_earthdata_acc_mail(self) -> str | None:
        """Return the configured NASA Earthdata email for CDDIS authentication.

        Returns
        -------
        str | None
            NASA Earthdata email address.
        """
        return self.processing.credentials.nasa_earthdata_acc_mail
