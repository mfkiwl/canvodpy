from ftplib import FTP

ftp = FTP("gssc.esa.int")
ftp.login()
ftp.cwd("/gnss/products/2399")

files = ftp.nlst()

with open("esa_gnss_products_2399_files.txt", "w") as f:
    for name in files:
        f.write(name + "\n")

ftp.quit()
