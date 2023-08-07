from cfinterface.components.section import Section
from cfinterface.data.sectiondata import SectionData


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    @property
    def my_data(self):
        return self.data


def test_sectiondata_eq():
    sd1 = SectionData(DummySection(data=-1))
    sd2 = SectionData(DummySection(data=-1))
    assert sd1 == sd2


def test_sectiondata_not_eq():
    sd1 = SectionData(DummySection(data=-1))
    sd2 = SectionData(DummySection(data=+1))
    assert sd1 != sd2


def test_sectiondata_append():
    sd = SectionData(DummySection(data=-1))
    n_sections = 10
    for i in range(n_sections):
        sd.append(DummySection(data=i))
    assert len(sd) == n_sections + 1
    assert sd.first.data == -1
    assert sd.last.data == n_sections - 1


def test_sectiondata_preppend():
    sd = SectionData(DummySection(data=-1))
    n_sections = 10
    for i in range(n_sections):
        sd.preppend(DummySection(data=i))
    assert len(sd) == n_sections + 1
    assert sd.first.data == n_sections - 1
    assert sd.last.data == -1


def test_sectiondata_add_before():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    s2 = DummySection(data=2)
    sd.add_before(s1, s2)
    assert s1.previous == s2
    assert s2.next == s1
    assert sd.last == s1
    assert len(sd) == 3


def test_sectiondata_add_before_root():
    s1 = DummySection(data=1)
    sd = SectionData(s1)
    s2 = DummySection(data=2)
    sd.add_before(s1, s2)
    assert s1.previous == s2
    assert s2.next == s1
    assert sd.last == s1
    assert len(sd) == 2


def test_sectiondata_add_after():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    s2 = DummySection(data=2)
    sd.add_after(s1, s2)
    assert s1.next == s2
    assert s2.previous == s1
    assert sd.last == s2
    assert len(sd) == 3


def test_sectiondata_add_after_head():
    s1 = DummySection(data=-1)
    sd = SectionData(s1)
    s2 = DummySection(data=2)
    sd.add_after(s1, s2)
    assert s1.next == s2
    assert s2.previous == s1
    assert sd.last == s2
    assert len(sd) == 2


def test_sectiondata_remove():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    assert len(sd) == 2
    sd.remove(s1)
    assert len(sd) == 1


def test_sectiondata_of_type():
    sd = SectionData(DummySection())
    sd.append(Section())
    assert len(sd) == 2
    assert len([b for b in sd.of_type(DummySection)]) == 1


def test_sectiondata_get_sections_of_type_no_filter():
    b1 = DummySection(data=10)
    bd = SectionData(b1)
    bd.append(Section())
    assert bd.get_sections_of_type(DummySection) == b1


def test_sectiondata_get_sections_of_type_filter():
    b1 = DummySection(data=10)
    bd = SectionData(b1)
    bd.append(DummySection())
    bd.append(DummySection(data=11))
    assert len(bd.get_sections_of_type(DummySection)) == 3
    assert bd.get_sections_of_type(DummySection, my_data=10) == b1


def test_sectiondata_remove_sections_of_type_no_filter():
    b1 = DummySection(data=10)
    bd = SectionData(b1)
    bd.append(DummySection())
    bd.append(DummySection(data=11))
    bd.remove_sections_of_type(DummySection)
    assert len(bd) == 1
