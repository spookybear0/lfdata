from lfdata.model.base import Base


def test_base_class() -> None:
    assert issubclass(Base, Base)
