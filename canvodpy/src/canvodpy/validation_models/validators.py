from pathlib import Path


class YYDOYValidator:
    '''
    Validates the format of a year and day of year YYDOY string.
    '''

    @staticmethod
    def validate(yydoy_str: str) -> bool:
        '''
        The format of a YYDOY string should be as follows:
        - The string should have a length of 5 characters.
        - The string should contain only digits.
        - The last three digits should be between 1 and 367.

        Parameters
        ----------
        yydoy_str : str
            The YYDOY string to validate.

        Returns
        -------
        bool
            True if the string is a valid YYDOY string, False otherwise
    '''

        if len(yydoy_str) != 5:
            return False
        if not yydoy_str.isdigit():
            return False
        if not (1 <= int(yydoy_str[-3:]) <= 367):
            return False
        return True


class RinexFilesPresentValidator:
    ''''
    Validates the presence of RINEX files in a directory.
    '''

    @staticmethod
    def validate(directory: Path) -> bool:
        '''
        Checks if RINEX files are present in the specified directory.
        The current implmentation (like the whole `gnssvodpy` library)\
            checks for files with the extension '.2?o'.\
            as it is used by Septentrio receivers.

        Parameters
        ----------
        directory : str
            The directory to check for RINEX files.

        Returns
        -------
        bool
            True if RINEX files are present in the directory, False otherwise.
        '''

        rnx_files = list(directory.glob('*.2?o'))

        if rnx_files:
            return True
        return False


if __name__ == '__main__':
    pth = Path(
        '/home/nbader/Music/GNSS_Test/01_Rosalia/02_canopy/01_GNSS/01_raw/25003'
    )

    print(RinexFilesPresentValidator.validate(pth))
