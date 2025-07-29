"""
Copyright (c) 2025 Mirasurf
Copyright (c) 2023-2025 morphik/morphik-core
Original code from https://github.com/morphik/morphik-core
"""

from typing import List, Optional, Union

from FlagEmbedding import FlagAutoReranker

from cogent_base.models.chunk import ObjectChunk
from cogent_base.reranker.base_reranker import BaseReranker


class FlagReranker(BaseReranker):
    """Reranker implementation using FlagEmbedding"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-gemma",
        query_max_length: int = 256,
        passage_max_length: int = 512,
        use_fp16: bool = True,
        device: Optional[str] = None,
    ):
        """Initialize flag reranker"""
        devices = [device] if device else None
        self.reranker = FlagAutoReranker.from_finetuned(
            model_name_or_path=model_name,
            query_max_length=query_max_length,
            passage_max_length=passage_max_length,
            use_fp16=use_fp16,
            devices=devices,
        )

    async def rerank(
        self,
        query: str,
        chunks: List[ObjectChunk],
    ) -> List[ObjectChunk]:
        """Rerank chunks based on their relevance to the query"""
        if not chunks:
            return []

        # Get scores for all chunks
        passages = [chunk.content for chunk in chunks]
        scores = await self.compute_score(query, passages)

        # Update scores and sort chunks
        for chunk, score in zip(chunks, scores):
            chunk.score = float(score)

        return sorted(chunks, key=lambda x: x.score, reverse=True)

    async def compute_score(
        self,
        query: str,
        text: Union[str, List[str]],
    ) -> Union[float, List[float]]:
        """Compute relevance scores between query and text"""
        if isinstance(text, str):
            text = [text]
            scores = self.reranker.compute_score([[query, t] for t in text], normalize=True)
            return scores[0] if len(scores) == 1 else scores
        else:
            return self.reranker.compute_score([[query, t] for t in text], normalize=True)
