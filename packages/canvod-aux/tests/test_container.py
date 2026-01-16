"""
Tests for container module.

Tests GnssData dataclass and FileDownloader protocol.
"""
import pytest
from datetime import datetime
from canvod.aux.container import GnssData, FileMetadata, FtpDownloader


class TestFileMetadata:
    """Tests for FileMetadata dataclass."""
    
    def test_create_metadata(self):
        """Test creating FileMetadata instance."""
        metadata = FileMetadata(
            filename="test.sp3",
            agency="COD",
            product_type="final"
        )
        
        assert metadata.filename == "test.sp3"
        assert metadata.agency == "COD"
        assert metadata.product_type == "final"


class TestGnssData:
    """Tests for GnssData dataclass."""
    
    def test_create_gnss_data_minimal(self):
        """Test creating GnssData with minimal fields."""
        data = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01"
        )
        
        assert data.timestamp == datetime(2024, 1, 15, 12, 0, 0)
        assert data.satellite_id == "G01"
    
    def test_create_gnss_data_with_position(self):
        """Test creating GnssData with position data."""
        data = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01",
            x=1234567.89,
            y=9876543.21,
            z=5555555.55
        )
        
        assert data.x == 1234567.89
        assert data.y == 9876543.21
        assert data.z == 5555555.55
    
    def test_create_gnss_data_with_velocity(self):
        """Test creating GnssData with velocity data."""
        data = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01",
            vx=100.0,
            vy=200.0,
            vz=300.0
        )
        
        assert data.vx == 100.0
        assert data.vy == 200.0
        assert data.vz == 300.0
    
    def test_create_gnss_data_with_clock(self):
        """Test creating GnssData with clock correction."""
        data = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01",
            clock_offset=1.23e-6
        )
        
        assert data.clock_offset == 1.23e-6


class TestFtpDownloader:
    """Tests for FtpDownloader class."""
    
    def test_create_ftp_downloader(self):
        """Test creating FtpDownloader instance."""
        downloader = FtpDownloader()
        assert downloader is not None
    
    def test_create_ftp_downloader_with_email(self):
        """Test creating FtpDownloader with user email."""
        downloader = FtpDownloader(user_email="test@example.com")
        assert downloader.user_email == "test@example.com"
    
    def test_ftp_downloader_implements_protocol(self):
        """Test that FtpDownloader implements FileDownloader protocol."""
        downloader = FtpDownloader()
        
        # Should have download method
        assert hasattr(downloader, 'download')
        assert callable(getattr(downloader, 'download'))
    
    @pytest.mark.skip(reason="Requires network access and FTP server")
    def test_download_file(self):
        """Test downloading a file (skipped by default)."""
        # This test would require actual FTP server access
        # and would be slow, so we skip it by default
        pass


class TestDataclassFeatures:
    """Tests for dataclass-specific features."""
    
    def test_gnss_data_equality(self):
        """Test GnssData equality comparison."""
        data1 = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01",
            x=1000.0
        )
        data2 = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01",
            x=1000.0
        )
        
        assert data1 == data2
    
    def test_gnss_data_inequality(self):
        """Test GnssData inequality."""
        data1 = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G01"
        )
        data2 = GnssData(
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            satellite_id="G02"
        )
        
        assert data1 != data2
    
    def test_file_metadata_repr(self):
        """Test FileMetadata string representation."""
        metadata = FileMetadata(
            filename="test.sp3",
            agency="COD",
            product_type="final"
        )
        
        repr_str = repr(metadata)
        assert "FileMetadata" in repr_str
        assert "test.sp3" in repr_str
