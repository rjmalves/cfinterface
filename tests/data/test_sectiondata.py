from cfinterface.components.section import Section
from cfinterface.data.sectiondata import SectionData


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data


def test_blockdata_eq():
    sd1 = SectionData(DummySection(data=-1))
    sd2 = SectionData(DummySection(data=-1))
    assert sd1 == sd2


def test_blockdata_not_eq():
    sd1 = SectionData(DummySection(data=-1))
    sd2 = SectionData(DummySection(data=+1))
    assert sd1 != sd2


def test_blockdata_append():
    sd = SectionData(DummySection(data=-1))
    n_sections = 10
    for i in range(n_sections):
        sd.append(DummySection(data=i))
    assert len(sd) == n_sections + 1
    assert sd.first.data == -1
    assert sd.last.data == n_sections - 1


def test_blockdata_preppend():
    sd = SectionData(DummySection(data=-1))
    n_sections = 10
    for i in range(n_sections):
        sd.preppend(DummySection(data=i))
    assert len(sd) == n_sections + 1
    assert sd.first.data == n_sections - 1
    assert sd.last.data == -1


def test_blockdata_add_before():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    s2 = DummySection(data=2)
    sd.add_before(s1, s2)
    assert s1.previous == s2
    assert s2.next == s1


def test_blockdata_add_after():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    s2 = DummySection(data=2)
    sd.add_after(s1, s2)
    assert s1.next == s2
    assert s2.previous == s1


def test_blockdata_remove():
    sd = SectionData(DummySection(data=-1))
    s1 = DummySection(data=1)
    sd.append(s1)
    assert len(sd) == 2
    sd.remove(s1)
    assert len(sd) == 1


def test_blockdata_of_type():
    sd = SectionData(DummySection())
    sd.append(Section())
    assert len(sd) == 2
    assert len([b for b in sd.of_type(DummySection)]) == 1
