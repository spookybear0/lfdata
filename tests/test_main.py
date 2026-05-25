from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from lfdata.__main__ import main


def test_main_no_args() -> None:
    with patch.object(sys, 'argv', ['lfdata']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_print_replay(capsys) -> None:
    real_path = Path(__file__).parent.parent / 'assets' / 'sm5_sanitized.tdf'
    with patch.object(
        sys,
        'argv',
        ['lfdata', '--input_tdf', str(real_path), '--print_replay'],
    ):
        main()
        captured = capsys.readouterr()
        assert '* Mission Start *' in captured.out
        assert 'completes an achievement!' in captured.out
