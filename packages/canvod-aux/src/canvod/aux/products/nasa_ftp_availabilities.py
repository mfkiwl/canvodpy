from ftplib import FTP_TLS, error_perm
from pathlib import Path

HOST = "gdc.cddis.eosdis.nasa.gov"
REMOTE_DIR = "/gnss/products/2399"

EARTHDATA_USER = "nfb2024"
EARTHDATA_PASS = "UebungGnss2024$"

OUT_FILE = Path("cddis_gnss_products_2399_LIST.txt")


def list_dir_to_file(host: str, remote_dir: str, user: str, password: str,
                     out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)

    ftps = FTP_TLS(host=host, timeout=60)
    try:
        # Login + protect data channel (explicit FTPS)
        ftps.login(user=user, passwd=password)
        ftps.prot_p()
        ftps.set_pasv(True)

        # Change into the target directory
        ftps.cwd(remote_dir)

        # Get a detailed listing (like `ls -l`)
        lines: list[str] = []
        ftps.retrlines("LIST", lines.append)

        # Write to file
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"Wrote {len(lines)} lines to: {out_file.resolve()}")

    except error_perm as e:
        raise RuntimeError(f"FTP permission/auth error: {e}") from e
    finally:
        try:
            ftps.quit()
        except Exception:
            ftps.close()


if __name__ == "__main__":
    list_dir_to_file(HOST, REMOTE_DIR, EARTHDATA_USER, EARTHDATA_PASS,
                     OUT_FILE)
