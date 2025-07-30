"""
Base module for processing components in the SEC pipeline. Provides common functionality for error handling,
directory management, and process tracking used by all processing modules.
"""

import datetime
import os
from pathlib import Path
from typing import List


class ErrorEntry:
    def __init__(self, adsh: str, error_info: str, error: str):
        self.adsh = adsh
        self.error_info = error_info
        self.error = error

    def printentry(self):
        print(self.adsh, " - ", self.error_info, " - ", self.error)


class ProcessBase:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.processdate = datetime.date.today().isoformat()

        self.data_dir = self._ensure_trailing_slash(data_dir)

        self.error_log_dir = self.data_dir + "error/"

        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.isdir(self.error_log_dir):
            os.makedirs(self.error_log_dir)

        self.data_path = Path(self.data_dir)
        self.error_path = Path(self.error_log_dir)

    def _log_error(self, adsh: str, file_type: str, error_list: List[ErrorEntry]):
        if len(error_list) > 0:
            error_file_name = self.error_log_dir + file_type + "_" + adsh + ".txt"
            with open(error_file_name, "w", encoding="utf-8") as f:
                for error in error_list:
                    f.write(error.error_info + " - " + error.error + "\n")

    @staticmethod
    def _ensure_trailing_slash(directory: str) -> str:
        """Ensure the directory path ends with a slash."""
        if directory and directory[-1] != "/" and directory[-1] != "\\":
            return directory + "/"
        return directory
