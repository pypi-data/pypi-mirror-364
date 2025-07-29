import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.retrievers import VectorStoreRetriever

logger = logging.getLogger(__name__)


class S3VectorsStore(VectorStore):
    """
    LangChain VectorStore implementation using AWS S3 Vectors service.

    Example:
        # create bucket and index
        S3VectorsStore.create_bucket_and_index(
            bucket_name="my-vectors-bucket",
            index_name="my-text-index",
            dimension=1536,
            distance="cosine",
            region_name="us-east-1",
        )

        # init store
        store = S3VectorsStore(
            bucket_name="my-vectors-bucket",
            index_name="my-text-index",
            dimension=1536,
            region_name="us-east-1",
        )

        # add documents
        ids = store.add_texts(
            texts=["Hello world", "LangChain + S3 Vectors"],
            embeddings=[[...], [...]],
            metadatas=[{"page":1}, {"page":2}],
            ids=["doc1", "doc2"],
        )

        # as retriever
        retriever = store.as_retriever(search_kwargs={"k": 5})
        docs = retriever.get_relevant_documents("What is LangChain?")
    """

    def __init__(
        self,
        bucket_name: str,
        index_name: str,
        dimension: int,
        distance: str = "cosine",
        region_name: Optional[str] = None,
        boto3_session: Optional[boto3.Session] = None,
    ):
        self.bucket = bucket_name
        self.index = index_name
        self.dimension = dimension
        self.distance = distance
        session = boto3_session or boto3.Session(region_name=region_name)
        self.client = session.client("s3vectors")

    @classmethod
    def create_bucket_and_index(
        cls,
        bucket_name: str,
        index_name: str,
        dimension: int,
        distance: str = "cosine",
        region_name: Optional[str] = None,
        boto3_session: Optional[boto3.Session] = None,
    ) -> None:
        """
        Create the S3 Vectors bucket and index configuration.
        """
        session = boto3_session or boto3.Session(region_name=region_name)
        client = session.client("s3vectors")
        try:
            client.create_vector_bucket(vectorBucketName=bucket_name)
            client.create_index(
                vectorBucketName=bucket_name,
                indexName=index_name,
                dimension=dimension,
                distanceMetric=distance,
                dataType="float32",
                metadataConfiguration={
                    "nonFilterableMetadataKeys": [],
                },
            )
            logger.info(f"Created bucket '{bucket_name}' and index '{index_name}'")
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error creating bucket or index: {e}")
            raise

    def add_texts(
        self,
        texts: Sequence[str],
        embeddings: Sequence[List[float]],
        metadatas: Optional[Sequence[Dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
        batch_size: int = 500,
    ) -> List[str]:
        """
        Embed and upload texts in batches. Returns the list of vector IDs.
        """
        vector_ids = []
        vectors = []
        for idx, embed in enumerate(embeddings):
            key = ids[idx] if ids else str(idx)
            metadata = metadatas[idx] if metadatas else {}
            vectors.append({"key": key, "data": {"float32": embed}, "metadata": metadata})
            vector_ids.append(key)

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            try:
                self.client.put_vectors(
                    vectorBucketName=self.bucket,
                    indexName=self.index,
                    vectors=batch,
                )
            except (ClientError, BotoCoreError) as e:
                logger.error(f"Failed to upload vectors batch {i}-{i+batch_size}: {e}")
                raise

        return vector_ids

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search top-k similar vectors and return LangChain Documents.
        """
        params: Dict[str, Any] = {
            "vectorBucketName": self.bucket,
            "indexName": self.index,
            "queryVector": {"float32": query_embedding},
            "topK": k,
            "returnMetadata": True,
            "returnDistance": True,
        }
        if filter:
            params["filter"] = filter

        try:
            resp = self.client.query_vectors(**params)
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Query failed: {e}")
            raise

        docs: List[Document] = []
        for v in resp.get("vectors", []):
            docs.append(
                Document(
                    page_content="",
                    metadata={**v.get("metadata", {}), "score": v.get("distance")},
                    lookup_str=v.get("key"),
                )
            )
        return docs

    def get_vectors_by_ids(
        self,
        ids: List[str],
    ) -> List[Document]:
        """
        Retrieve documents by their vector keys.
        """
        try:
            resp = self.client.get_vectors(
                vectorBucketName=self.bucket,
                indexName=self.index,
                ids=ids,
                returnMetadata=True,
                returnData=True,
            )
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Get vectors failed: {e}")
            raise

        docs: List[Document] = []
        for v in resp.get("vectors", []):
            docs.append(
                Document(
                    page_content="",
                    metadata={**v.get("metadata", {}), "vector": v.get("data")},
                    lookup_str=v.get("key"),
                )
            )
        return docs

    def as_retriever(
        self,
        search_kwargs: Optional[Dict[str, Any]] = None,
    ) -> VectorStoreRetriever:
        """
        Return a LangChain Retriever wrapping this VectorStore.

        Args:
            search_kwargs: passed to similarity_search as override (e.g., {"k": 10, "filter": {...}}).
        """
        return VectorStoreRetriever(
            vectorstore=self,
            search_kwargs=search_kwargs or {"k": 5},
        )