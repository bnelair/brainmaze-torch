

import os
from brainmaze_utils.files import get_files
from brainmaze_torch._config import config

DELIMITER = os.sep

configs_ArtifactEraser = dict([(f.split(DELIMITER)[-1].split('.')[0], config(f)) for f in get_files(DELIMITER.join(__file__.split(DELIMITER)[:-1]), 'yaml') if not '.-' in f.split(DELIMITER)[-1]])





