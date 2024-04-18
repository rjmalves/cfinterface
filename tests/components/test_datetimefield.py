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


def test_datetimefield_read_format_list():
    data = "2020/01/10"
    formats = ["%Y-%m-%d", "%Y/%m/%d"]
    field = DatetimeField(10, 0, format=formats)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == datetime.strptime(data, formats[1])


def test_datetimefield_write():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    line_before = f"field-{data}-else"
    date_data = datetime.strptime(data, format)
    field = DatetimeField(10, 6, format=format, value=date_data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_datetimefield_write_format_list():
    data = "2020/01/10"
    formats = ["%Y-%m-%d", "%Y/%m/%d"]
    line_before = f"field-{data}-else"
    date_data = datetime.strptime(data, formats[1])
    field = DatetimeField(10, 6, format=formats, value=date_data)
    line_after = field.write(line_before)
    assert line_before.replace("/", "-") == line_after


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


def test_datetimefield_read_error_binary():
    format = "%Y/%m/%d"
    field = DatetimeField(10, 0, format=format)
    line = b"2020/01-something-else"
    field.read(line)
    assert field.value is None


def test_datetimefield_read_binary():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    field = DatetimeField(10, 0, format=format)
    line = b"2020/01/10-something-else"
    field.read(line)
    assert field.value == datetime.strptime(data, format)


def test_datetimefield_write_binary():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    line_before = b"field-2020/01/10-else"
    date_data = datetime.strptime(data, format)
    field = DatetimeField(10, 6, format=format, value=date_data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_datetimefield_write_empty_binary():
    field = DatetimeField(5, 0)
    assert len(field.write(b"")) == 5


def test_datetimefield_write_short_line_binary():
    data = "2020/01/10"
    format = "%Y/%m/%d"
    date_data = datetime.strptime(data, format)
    field = DatetimeField(10, 6, format=format, value=date_data)
    line_after = field.write(b"    ")
    assert date_data == datetime.strptime(line_after.decode()[6:], format)
