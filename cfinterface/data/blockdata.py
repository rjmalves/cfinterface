from typing import TypeVar, Type, Generator, Optional, Union, List, Dict

from cfinterface.components.block import Block


class BlockData:
    """
    Class for a storing, managing and accessing data for a block file.
    """

    __slots__ = ["_items", "_type_index"]

    T = TypeVar("T")

    def __init__(self, root: Block) -> None:
        self._items: List[Block] = [root]
        self._type_index: Dict[Type, List[int]] = {type(root): [0]}
        self._refresh_indices(0)

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, idx: int) -> Block:
        return self._items[idx]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BlockData):
            return False
        if len(self) != len(o):
            return False
        return all(b1 == b2 for b1, b2 in zip(self._items, o._items))

    def _refresh_indices(self, start: int = 0) -> None:
        for i in range(start, len(self._items)):
            self._items[i]._container = self
            self._items[i]._index = i

    def _index_of(self, item: Block) -> int:
        for i, b in enumerate(self._items):
            if b is item:
                return i
        raise ValueError("Block not found in container")

    def _rebuild_type_index(self) -> None:
        self._type_index = {}
        for i, item in enumerate(self._items):
            t = type(item)
            if t not in self._type_index:
                self._type_index[t] = []
            self._type_index[t].append(i)

    def preppend(self, b: Block):
        """
        Appends a block to the beginning of the data.

        :param b: The new block to preppended to the data.
        :type b: Block
        """
        self._items.insert(0, b)
        self._refresh_indices(0)
        self._rebuild_type_index()

    def append(self, b: Block):
        """
        Appends a block to the end of the data.

        :param b: The new block to append to the data
        :type b: Block
        """
        self._items.append(b)
        self._refresh_indices(len(self._items) - 1)
        t = type(b)
        if t not in self._type_index:
            self._type_index[t] = []
        self._type_index[t].append(len(self._items) - 1)

    def add_before(self, before: Block, new: Block):
        """
        Adds a new block to the data before another
        specified block.

        :param before: The existing block which will be preppended
        :type before: Block
        :param new: The new block to add to the data
        :type new: Block
        """
        idx = self._index_of(before)
        self._items.insert(idx, new)
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def add_after(self, after: Block, new: Block):
        """
        Adds a new block to the data after another
        specified block.

        :param after: The existing block which will be appended
        :type after: Block
        :param new: The new block to add to the data
        :type new: Block
        """
        idx = self._index_of(after)
        self._items.insert(idx + 1, new)
        self._refresh_indices(idx + 1)
        self._rebuild_type_index()

    def remove(self, b: Block):
        """
        Removes an existing block in the chain.

        :param b: The block to be removed
        :type b: Block
        """
        idx = self._index_of(b)
        del self._items[idx]
        b._container = None
        b._index = 0
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def of_type(self, t: Type[T]) -> Generator[T, None, None]:
        """
        A block generator that only returns blocks of type T.

        :param t: The block type that is desired
        :type t: Type[T]
        :yield: Blocks filtered by type T
        :rtype: Generator[T, None, None]
        """
        indices: List[int] = []
        for cls, idx_list in self._type_index.items():
            if issubclass(cls, t):
                indices.extend(idx_list)
        indices.sort()
        for idx in indices:
            yield self._items[idx]

    def get_blocks_of_type(
        self, t: Type[T], **kwargs
    ) -> Optional[Union[T, List[T]]]:
        """
        A block or block list that only returns
        blocks of type T that meet
        given filter requirements passed as kwargs.

        :param t: The block type that is desired
        :type t: Type[T]
        :return: Blocks filtered by type T and optional properties
        :rtype: T | list[T] | None
        """

        def __meets(r) -> bool:
            return all(
                getattr(r, k) == v for k, v in kwargs.items() if v is not None
            )

        filtered_blocks = [r for r in self.of_type(t) if __meets(r)]
        if len(filtered_blocks) == 0:
            return None
        elif len(filtered_blocks) == 1:
            return filtered_blocks[0]
        else:
            return filtered_blocks

    def remove_blocks_of_type(self, t: Type[T], **kwargs):
        """
        Removes a set of blocks given a type and an optional group of
        filters, similar to `get_blocks_of_type()`

        :param t: The block type that is desired
        :type t: Type[T]
        """
        filtered_blocks = self.get_blocks_of_type(t, **kwargs)
        if isinstance(filtered_blocks, Block):
            self.remove(filtered_blocks)
        elif isinstance(filtered_blocks, list):
            for b in filtered_blocks:
                if b is not self._items[0]:
                    self.remove(b)

    @property
    def first(self) -> Block:
        return self._items[0]

    @property
    def last(self) -> Block:
        return self._items[-1]
