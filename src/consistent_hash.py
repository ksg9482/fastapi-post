import bisect
import hashlib


class ConsistentHash:
    def __init__(self, nodes: list[str], virtual_nodes: int = 100):
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self.ring: dict[str, str] = {}
        self.sorted_keys: list[str] = []
        self._build_ring()

    def _build_ring(self):
        self.ring = {}
        self.sorted_keys = []
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                key = self._hash(f"{node}:{i}")
                self.ring[key] = node
                bisect.insort(self.sorted_keys, key)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_node(self, key: str) -> tuple:
        if not self.ring:
            return None, -1
        hash_key = self._hash(key)
        index = bisect.bisect(self.sorted_keys, hash_key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[index]], self.nodes.index(
            self.ring[self.sorted_keys[index]]
        )

    def set_virtual_nodes(self, virtual_nodes: int):
        self.virtual_nodes = virtual_nodes
        self._build_ring()
