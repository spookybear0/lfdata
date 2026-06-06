from lfdata.importer.normalizer import GameTypeNormalizer


def test_game_type_normalizer_sm5() -> None:
    normalizer = GameTypeNormalizer()
    assert normalizer.normalize('Space Marines 5') == 'SM5'
    assert normalizer.normalize('SpaceMarines5') == 'SM5'
    assert normalizer.normalize('Space   Marines   5') == 'SM5'
    assert normalizer.normalize('Space Marines 5 Tournament Edition') == 'SM5'
    assert normalizer.normalize('SM5') == 'SM5'
    assert normalizer.normalize('SM5 Tournament') == 'SM5'


def test_game_type_normalizer_laserball() -> None:
    normalizer = GameTypeNormalizer()
    assert normalizer.normalize('Laser ball') == 'Laserball'
    assert normalizer.normalize('Laserball') == 'Laserball'
    assert normalizer.normalize('Laser Ball') == 'Laserball'
    assert normalizer.normalize('LaserBall') == 'Laserball'
    assert normalizer.normalize('Laser  ball  pro') == 'Laserball'


def test_game_type_normalizer_unmatched() -> None:
    normalizer = GameTypeNormalizer()
    assert normalizer.normalize('Standard TDF') is None
    assert normalizer.normalize('Unknown Game Type') is None
