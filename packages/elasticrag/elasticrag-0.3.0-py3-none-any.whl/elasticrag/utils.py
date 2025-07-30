from typing import List, Tuple
from collections import defaultdict


def rrf(*queries, k: int = 60) -> List[Tuple]:
    """Reciprocal Rank Fusion algorithm"""
    rrf_scores = defaultdict(float)
    for query_results in queries:
        for i, (doc_id, _) in enumerate(query_results):
            # The rank is i + 1.
            # The RRF formula adds 1.0 / (k + rank).
            rrf_scores[doc_id] += 1.0 / (k + i + 1)

    # Sort the documents by their final RRF score in descending order.
    return sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)