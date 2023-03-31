from typing import Dict, Any
from pathlib import Path
from slugify import slugify
from papercast.types import PathLike
import subprocess
import sys

from papercast.base import BaseProcessor
from papercast.production import Production


class SayProcessor(BaseProcessor):
    def __init__(self, txt_dir, mp3_dir) -> None:
        super().__init__()

        self._check_osx()

        self.txt_dir = Path(txt_dir)
        self.mp3_dir = Path(mp3_dir)

    def _check_osx(self):
        if not sys.platform.startswith("darwin"):
            raise OSError("This processor only works on Mac OS X")

    def input_types(self) -> Dict[str, Any]:
        return {
            "text": str,
            "title": str,
        }

    def output_types(self) -> Dict[str, Any]:
        return {
            "mp3_path": str,
        }

    def _narrate(self, txtpath: PathLike, mp3path: PathLike):
        txtpath = str(txtpath)
        mp3path = str(mp3path)
        aiffpath = txtpath.replace("txt", "aiff")
        cmd1 = [
            "say",
            "-f",
            txtpath,
            "-o",
            aiffpath,
        ]
        cmd2 = ["lame", aiffpath, mp3path]
        self.logger.info(f"Starting conversion: {' '.join(cmd1)}")
        subprocess.call(cmd1)
        subprocess.call(cmd2)

    def process(self, input: Production, **kwargs) -> Production:
        file_stem = slugify(input.title)
        txt_path = self.txt_dir / (file_stem + ".txt")
        mp3_path = self.mp3_dir / (file_stem + ".mp3")

        with open(txt_path, "w") as f:
            f.write(input.text)

        self._narrate(txt_path, mp3_path)

        setattr(input, "mp3_path", mp3_path)
        return input
