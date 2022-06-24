from datetime import datetime

from cfinterface.components.datetimefield import DatetimeField


def test_datetimefield_read_error():
    data = "2020/01"
    format = "%Y/%m/%d"
    field = DatetimeField(10, 0, format=format)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value is None


def test_datetimefield_read():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    field = DatetimeField(10, 0, format=format)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == datetime.strptime(data, format)


def test_datetimefield_write():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    line_before = f"field-{data}-else"
    date_data = datetime.strptime(data, format)
    field = DatetimeField(10, 6, format=format, value=date_data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_datetimefield_write_empty():
    field = DatetimeField(5, 0)
    assert len(field.write("")) == 5


def test_datetimefield_write_short_line():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    date_data = datetime.strptime(data, format)
    field = DatetimeField(10, 6, format=format, value=date_data)
    line_after = field.write("    ")
    assert date_data == datetime.strptime(line_after[6:], format)
