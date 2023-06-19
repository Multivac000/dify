from flask import current_app
from langchain.embeddings import OpenAIEmbeddings

from core.embedding.cached_embedding import CacheEmbedding
from core.index.keyword_table_index.keyword_table_index import KeywordTableIndex, KeywordTableConfig
from core.index.vector_index.vector_index import VectorIndex
from core.llm.llm_builder import LLMBuilder
from models.dataset import Dataset


class IndexBuilder:
    @classmethod
    def get_index(cls, dataset: Dataset, high_quality: str):
        if high_quality == "high_quality":
            if dataset.indexing_technique != 'high_quality':
                return None

            model_credentials = LLMBuilder.get_model_credentials(
                tenant_id=dataset.tenant_id,
                model_provider=LLMBuilder.get_default_provider(dataset.tenant_id),
                model_name='text-embedding-ada-002'
            )

            embeddings = CacheEmbedding(OpenAIEmbeddings(
                **model_credentials
            ))

            return VectorIndex(
                dataset=dataset,
                config=current_app.config,
                embeddings=embeddings
            )
        elif high_quality == "economy":
            return KeywordTableIndex(
                dataset=dataset,
                config=KeywordTableConfig(
                    max_keywords_per_chunk=10
                )
            )
        else:
            raise ValueError('Unknown indexing technique')