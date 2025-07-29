import warnings
from itertools import islice, tee
from typing import Iterable, Iterator, Any, Optional, List, Callable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from mockfirestore.aggregation import AggregationQuery

from mockfirestore.document import DocumentSnapshot
from mockfirestore._helpers import T

class StructuredQuery():
    class UnaryFilter():
        class Operator():
            OPERATOR_UNSPECIFIED = 0
            IS_NAN = 2
            IS_NULL = 3
            IS_NOT_NAN = 4
            IS_NOT_NULL = 5


class CompositeFilter():
    def __init__(self, filters: List[Any]):
        self.filters = filters


class Or(CompositeFilter):
    pass


class And(CompositeFilter):
    pass


class Query:
    def __init__(self, parent: 'CollectionReference', projection=None,
                 field_filters=(), orders=(), limit=None, offset=None,
                 start_at=None, end_at=None, all_descendants=False) -> None:
        self.parent = parent
        self.projection = projection
        self._field_filters = []
        self.orders = list(orders)
        self._limit = limit
        self._offset = offset
        self._start_at = start_at
        self._end_at = end_at
        self.all_descendants = all_descendants

        if field_filters:
            for field_filter in field_filters:
                self._add_field_filter(*field_filter)

    def stream(self, transaction=None):
        from mockfirestore import CollectionReference, CollectionGroup, DocumentSnapshot
        parent: Union[CollectionReference, CollectionGroup] = self.parent
        doc_snapshots: Iterator[DocumentSnapshot] = parent.stream(transaction=transaction)

        for field, compare, value in self._field_filters:
            filtered_snapshots = []

            # Handle fieldpath.documentId()
            if field == '__name__':
                for doc_snapshot in doc_snapshots:
                    if compare(doc_snapshot.id, value):
                        filtered_snapshots.append(doc_snapshot)
                doc_snapshots = filtered_snapshots
                continue

            for doc_snapshot in doc_snapshots:
                if field in ["Or", "And"]:
                    # Evaluate composite filters
                    results = []
                    
                    for filter_group in value:
                        # Handle nested And/Or within Or/And
                        if isinstance(filter_group, tuple) and filter_group[0] in ["And", "Or"]:
                            nested_compare = self._compare_func(filter_group[0])
                            nested_results = []
                            
                            for nested_filter in filter_group[2]:
                                f, op, v = nested_filter
                                nested_field_path = doc_snapshot._get_by_field_path(f)
                                nested_field_compare = self._compare_func(op)
                                nested_results.append(nested_field_compare(nested_field_path, v))
                            
                            results.append(nested_compare(nested_results))
                        else:
                            # Handle regular field filters inside composite
                            f, op, v = filter_group
                            field_path = doc_snapshot._get_by_field_path(f)
                            field_compare = self._compare_func(op)
                            results.append(field_compare(field_path, v))
                    
                    if compare(results):
                        filtered_snapshots.append(doc_snapshot)
                else:
                    # Regular field filter
                    field_path = doc_snapshot._get_by_field_path(field)
                    if compare(field_path, value):
                        filtered_snapshots.append(doc_snapshot)

            doc_snapshots = filtered_snapshots

        if self.orders:
            for key, direction in self.orders:
                doc_snapshots = sorted(doc_snapshots,
                                       key=lambda doc: doc.to_dict()[key],
                                       reverse=direction == 'DESCENDING')
        if self._start_at:
            document_fields_or_snapshot, before = self._start_at
            doc_snapshots = self._apply_cursor(
                document_fields_or_snapshot, doc_snapshots, before, True)

        if self._end_at:
            document_fields_or_snapshot, before = self._end_at
            doc_snapshots = self._apply_cursor(
                document_fields_or_snapshot, doc_snapshots, before, False)

        if self._offset:
            doc_snapshots = islice(doc_snapshots, self._offset, None)

        if self._limit:
            doc_snapshots = islice(doc_snapshots, self._limit)

        return iter(doc_snapshots)

    def get(self) -> List[DocumentSnapshot]:
        warnings.warn('Query.get is deprecated, please use Query.stream',
                      category=DeprecationWarning)
        return list(self.stream())

    def _add_field_filter(self, field: str, op: str, value: Any):
        compare = self._compare_func(op)
        self._field_filters.append((field, compare, value))

    def where(self, field: Optional[str] = None, op: Optional[str] = None, value: Any = None, filter=None) -> 'PatchedQuery':
        field, op, value = self.make_field_filter(field, op, value, filter)
        self._add_field_filter(field, op, value)
        return self

    @staticmethod
    def make_field_filter(field: Optional[str], op: Optional[str], value: Any = None, filter=None):
        if bool(filter) and (bool(field) or bool(op)):
            raise ValueError(
                "Can't pass in both the positional arguments and 'filter' at the same time")
        if filter:
            if hasattr(filter, 'filters'):
                filters = [Query.make_field_filter(
                    None, None, None, f) for f in filter.filters]
                return (filter.__class__.__name__, filter.__class__.__name__, filters)

            return (filter.field_path, filter.op_string, filter.value)

        else:
            return (field, op, value)

    def order_by(self, field_path: str, direction: Optional[str] = 'ASCENDING') -> 'Query':
        self.orders.append((field_path, direction))
        return self

    def limit(self, count: int) -> 'Query':
        self._limit = count
        return self

    def offset(self, num_to_skip: int) -> 'Query':
        self._offset = num_to_skip
        return self

    def start_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> 'Query':
        self._start_at = (document_fields_or_snapshot, True)
        return self

    def start_after(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> 'Query':
        self._start_at = (document_fields_or_snapshot, False)
        return self

    def end_at(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> 'Query':
        self._end_at = (document_fields_or_snapshot, True)
        return self

    def end_before(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot]) -> 'Query':
        self._end_at = (document_fields_or_snapshot, False)
        return self

    def select(self, field_paths: Iterable[str]) -> 'Query':
        self._projection = field_paths
        return self
        
    def count(self, alias: Optional[str] = None) -> 'AggregationQuery':
        """Adds a count over the query.
        
        Args:
            alias: Optional name of the field to store the result.
            
        Returns:
            An AggregationQuery with the count aggregation.
        """
        from mockfirestore.aggregation import AggregationQuery
        return AggregationQuery(self, alias).count(alias)
        
    def avg(self, field_ref, alias: Optional[str] = None) -> 'AggregationQuery':
        """Adds an average over the query.
        
        Args:
            field_ref: The field to aggregate across.
            alias: Optional name of the field to store the result.
            
        Returns:
            An AggregationQuery with the average aggregation.
        """
        from mockfirestore.aggregation import AggregationQuery
        return AggregationQuery(self, alias).avg(field_ref, alias)
        
    def sum(self, field_ref, alias: Optional[str] = None) -> 'AggregationQuery':
        """Adds a sum over the query.
        
        Args:
            field_ref: The field to aggregate across.
            alias: Optional name of the field to store the result.
            
        Returns:
            An AggregationQuery with the sum aggregation.
        """
        from mockfirestore.aggregation import AggregationQuery
        return AggregationQuery(self, alias).sum(field_ref, alias)

    def _apply_cursor(self, document_fields_or_snapshot: Union[dict, DocumentSnapshot], doc_snapshot: Iterator[DocumentSnapshot],
                      before: bool, start: bool) -> Iterator[DocumentSnapshot]:
        docs, doc_snapshot = tee(doc_snapshot)
        for idx, doc in enumerate(doc_snapshot):
            index = None
            if isinstance(document_fields_or_snapshot, dict):
                for k, v in document_fields_or_snapshot.items():
                    if doc.to_dict().get(k, None) == v:
                        index = idx
                    else:
                        index = None
                        break
            elif isinstance(document_fields_or_snapshot, DocumentSnapshot):
                if doc.id == document_fields_or_snapshot.id:
                    index = idx
            if index is not None:
                if before and start:
                    return islice(docs, index, None, None)
                elif not before and start:
                    return islice(docs, index + 1, None, None)
                elif before and not start:
                    return islice(docs, 0, index + 1, None)
                elif not before and not start:
                    return islice(docs, 0, index, None)

    def _compare_func(self, op: str) -> Callable[[T, T], bool]:
        if op == '==':
            return lambda x, y: x == y
        elif op == '!=':
            return lambda x, y: x != y
        elif op == '<':
            return lambda x, y: x < y
        elif op == '<=':
            return lambda x, y: x <= y
        elif op == '>':
            return lambda x, y: x > y
        elif op == '>=':
            return lambda x, y: x >= y
        elif op == 'in':
            return lambda x, y: x in y
        elif op == 'array_contains':
            return lambda x, y: y in x
        elif op == 'array_contains_any':
            return lambda x, y: any([val in y for val in x])
        elif op == 'Or':
            return lambda x: any(x)
        elif op == 'And':
            return lambda x: all(x)
        elif op == StructuredQuery.UnaryFilter.Operator.IS_NULL:
            return lambda x, y: x is None
