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


class DefaultSection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data


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


def test_sectiondata_getitem():
    root = DummySection(data=0)
    sd = SectionData(root)
    s1 = DummySection(data=1)
    s2 = DummySection(data=2)
    s3 = DummySection(data=3)
    sd.append(s1)
    sd.append(s2)
    sd.append(s3)
    assert sd[0] is root
    assert sd[3] is s3


def test_sectiondata_getitem_negative():
    root = DummySection(data=0)
    sd = SectionData(root)
    s1 = DummySection(data=1)
    s2 = DummySection(data=2)
    sd.append(s1)
    sd.append(s2)
    assert sd[-1] is s2


def test_sectiondata_getitem_out_of_bounds():
    sd = SectionData(DummySection(data=0))
    try:
        _ = sd[100]
        assert False, "Expected IndexError was not raised"
    except IndexError:
        pass


def test_sectiondata_remove_updates_pointers():
    root = DummySection(data=0)
    sd = SectionData(root)
    s1 = DummySection(data=1)
    s2 = DummySection(data=2)
    s3 = DummySection(data=3)
    sd.append(s1)
    sd.append(s2)
    sd.append(s3)
    sd.remove(s2)
    assert s1.next is s3
    assert s3.previous is s1


def test_sectiondata_remove_head():
    root = DummySection(data=0)
    sd = SectionData(root)
    s1 = DummySection(data=1)
    sd.append(s1)
    sd.remove(s1)
    assert sd.last is root
    assert root.next is None


def test_sectiondata_computed_previous_next():
    root = DummySection(data=0)
    s1 = DummySection(data=1)
    s2 = DummySection(data=2)
    sd = SectionData(root)
    sd.append(s1)
    sd.append(s2)
    assert s1.previous is root
    assert s1.next is s2
    assert root.previous is None
    assert s2.next is None


def test_sectiondata_computed_after_remove():
    root = DummySection(data=0)
    s1 = DummySection(data=1)
    s2 = DummySection(data=2)
    sd = SectionData(root)
    sd.append(s1)
    sd.append(s2)
    sd.remove(s1)
    assert root.next is s2
    assert s2.previous is root
    assert s1._container is None


def test_sectiondata_of_type_with_mixed_types():
    root = DummySection(data=0)
    sd = SectionData(root)
    dummies = []
    for i in range(1, 6):
        d = DummySection(data=i)
        sd.append(d)
        sd.append(DefaultSection(data=i))
        dummies.append(d)
    dummy_results = list(sd.of_type(DummySection))
    assert len(dummy_results) == 6
    assert dummy_results[0] is root
    for expected, actual in zip(dummies, dummy_results[1:]):
        assert actual is expected
    default_results = list(sd.of_type(DefaultSection))
    assert len(default_results) == 5
    assert all(type(s) is DefaultSection for s in default_results)


def test_sectiondata_of_type_base_class():
    root = DummySection(data=0)
    sd = SectionData(root)
    for i in range(1, 6):
        sd.append(DummySection(data=i))
        sd.append(DefaultSection(data=i))
    all_results = list(sd.of_type(Section))
    assert len(all_results) == 11
    items_from_iter = list(sd)
    assert all_results == items_from_iter


def test_sectiondata_type_index_after_remove():
    root = DummySection(data=0)
    s1 = DummySection(data=1)
    s2 = DefaultSection(data=2)
    sd = SectionData(root)
    sd.append(s1)
    sd.append(s2)
    sd.remove(s1)
    dummy_results = list(sd.of_type(DummySection))
    assert len(dummy_results) == 1
    assert dummy_results[0] is root
    default_results = list(sd.of_type(DefaultSection))
    assert len(default_results) == 1
    assert default_results[0] is s2
    assert sd._type_index[DefaultSection] == [1]


def test_sectiondata_type_index_after_preppend():
    root = DummySection(data=0)
    sd = SectionData(root)
    sd.append(DefaultSection(data=1))
    new = DummySection(data=2)
    sd.preppend(new)
    dummy_results = list(sd.of_type(DummySection))
    assert len(dummy_results) == 2
    assert dummy_results[0] is new
    assert dummy_results[1] is root
    assert sd._type_index[DummySection] == [0, 1]
    assert sd._type_index[DefaultSection] == [2]
