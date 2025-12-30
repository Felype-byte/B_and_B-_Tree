"""
Módulo core - Implementações de estruturas de dados e utilitários.
"""

from .btree import BTree, BTreeNode
from .bplustree import BPlusTree, BPlusTreeNode
from .trace import Tracer, Event, EventType
from .metrics import Metrics
from .validate import validate_btree, validate_bplustree, ValidationError
from .random_ops import (
    generate_unique_random_ints,
    batch_insert,
    choose_existing_keys,
    batch_remove
)

__all__ = [
    'BTree', 'BTreeNode',
    'BPlusTree', 'BPlusTreeNode',
    'Tracer', 'Event', 'EventType',
    'Metrics',
    'validate_btree', 'validate_bplustree', 'ValidationError',
    'generate_unique_random_ints', 'batch_insert',
    'choose_existing_keys', 'batch_remove'
]
