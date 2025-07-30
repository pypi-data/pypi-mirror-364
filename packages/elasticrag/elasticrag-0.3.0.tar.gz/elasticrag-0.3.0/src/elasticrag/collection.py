import asyncio
import logging
import base64
from functools import partial
from typing import Dict, List, Optional
from elasticsearch import NotFoundError
from elasticsearch.helpers import bulk

from .utils import rrf


class Collection:
    """Collection (knowledge base) abstraction, corresponding to an ES index"""
    
    def __init__(self, client, name: str, user, model=None):
        self.client = client
        self.name = name
        self.user = user
        self.model = model
        
        # Index naming convention
        if model:
            self.index_name = f"{model.model_id}__{user.username}__{name}"
        else:
            self.index_name = f"{user.username}__{name}"
    
    def add(self, document_id: str, name: str, file_content: Optional[bytes] = None,
            text_content: Optional[str] = None, metadata: Optional[Dict] = None,
            chunks: Optional[List[Dict]] = None,
            timeout: int = 600) -> Dict:
        """
        Add a document to the collection using parent/child structure
        
        Args:
            document_id: Document ID
            name: Document name
            file_content: File content (binary)
            text_content: Text content
            metadata: Metadata
            chunks: Pre-processed chunks of text with embeddings (optional)
            timeout: Timeout
        """
        # Ensure at least one content source is provided
        if not file_content and not text_content and not chunks:
            raise ValueError("Must provide file_content, text_content, or chunks")

        # If chunks are not provided, process the content to generate chunks
        if not chunks:
            chunks = self._process_content(file_content, text_content)

        # Use bulk operation to add the parent and chunks
        return self._add_with_chunks(document_id, name, chunks, metadata, timeout)
    
    def _process_content(self, file_content: Optional[bytes] = None, text_content: Optional[str] = None) -> List[Dict]:
        """Process content (file or text) to generate chunks using unified pipeline"""
        if not file_content and not text_content:
            raise ValueError("Must provide either file_content or text_content")
        
        try:
            # Prepare source data based on content type
            if file_content:
                # For file content, use 'data' field for attachment processor
                source_data = {
                    "data": base64.b64encode(file_content).decode()
                }
            else:
                # For text content, use 'attachment.content' field directly
                source_data = {
                    "attachment": {
                        "content": text_content
                    }
                }
            
            # Use unified pipeline with both attachment and split processors
            response = self.client.client.ingest.simulate(
                body={
                    "pipeline": {
                        "processors": [
                            {
                                "attachment": {
                                    "field": "data",
                                    "target_field": "attachment",
                                    "indexed_chars": -1,  # Process entire content
                                    "properties": ["content", "title", "content_type"],
                                    "remove_binary": True,
                                    "ignore_missing": True  # Ignore if 'data' field doesn't exist
                                }
                            },
                            self.client.splitter.get_processor()
                        ]
                    },
                    "docs": [{"_source": source_data}]
                }
            )
            
            chunks = response['docs'][0]['doc']['_source'].get('chunks', [])
            content_length = len(source_data.get('data', '')) if file_content else len(text_content)
            logging.debug(f"Processed content ({content_length} chars) into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logging.error(f"Failed to process content: {e}")
            raise
    
    def _add_with_chunks(self, document_id: str, name: str, chunks: List[Dict], 
                        metadata: Optional[Dict] = None, timeout: int = 600) -> Dict:
        """Add document using parent/child structure with bulk operations"""
        actions = []
        
        # Add parent document
        actions.append({
            "_op_type": "index",
            "_index": self.index_name,
            "_id": document_id,
            "_source": {
                "doc_chunk_relation": "document",
                "name": name,
                "document_metadata": metadata or {},
                "chunks": len(chunks)  # Store the number of chunks
            }
        })
        
        # Add child chunks (embedding will be handled by default pipeline)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_{i}"
            chunk_source = {
                "doc_chunk_relation": {"name": "chunk", "parent": document_id},
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {})
            }
            
            # If embedding is already provided, include it
            if "embedding" in chunk:
                chunk_source["embedding"] = chunk["embedding"]
            
            actions.append({
                "_op_type": "index",
                "_index": self.index_name,
                "_id": chunk_id,
                "routing": document_id,
                "_source": chunk_source
            })
        
        try:
            success, failed = bulk(
                self.client.client,
                actions,
                refresh='wait_for',
                request_timeout=timeout,
                chunk_size=200,
                max_retries=2,
                initial_backoff=2,
                raise_on_error=False
            )
            
            if failed:
                logging.error(f"Add failed for doc {document_id}: {failed}")
                raise Exception(f"Failed to add some chunks: {failed}")
            
            return {"result": "created", "chunks_added": len(chunks)}
            
        except Exception as e:
            logging.error(f"Failed to add document with chunks: {e}")
            raise
    
    async def _build_query_prompt(self, query_text: str, terminology: Optional[List[str]] = None,
                                 k_hop_entities: Optional[List[List[str]]] = None) -> str:
        """
        构建用于向量搜索的增强prompt
        Args:
            query_text: 原始查询文本
            terminology: 相关术语列表
            k_hop_entities: k-hop实体匹配结果，格式为 [[1-hop], [2-hop], ...]

        Returns:
            str: 格式化后的查询文本
        """
        prompt_parts = [f"Query: {query_text}"]

        if terminology:
            prompt_parts.append(f"Related terms: {', '.join(terminology[:5])}")

        if k_hop_entities:
            # Flatten the list of entities from all hops and take the top unique ones
            all_entities = [entity for hop in k_hop_entities for entity in hop]
            # Get unique entities while preserving order (for Python 3.7+)
            unique_entities = list(dict.fromkeys(all_entities))
            if unique_entities:
                prompt_parts.append(f"Related entities: {', '.join(unique_entities[:5])}")

        return " | ".join(prompt_parts)

    async def build_query(self, query_text: str, metadata_filter: Optional[Dict] = None, 
                         size: int = 5, terminology: Optional[List[str]] = None,
                         k_hop_entities: Optional[List[List[str]]] = None,
                         boost_config: Optional[Dict] = None):
        """
        构建增强查询体，集成术语库和实体扩展

        Args:
            query_text: 查询文本
            metadata_filter: 元数据过滤条件
            size: 返回结果数量
            terminology: 术语库匹配列表
            k_hop_entities: k-hop实体匹配结果，格式为 [[1-hop], [2-hop], ...]
            boost_config: 权重配置，包含 terminology_boost, entity_base_boost, entity_decay_factor

        Returns:
            tuple: (text_search_body, vector_search_body)
        """
        # 默认权重配置
        default_boost = {
            "terminology_boost": 0.6,      # 术语权重提升至60%
            "entity_base_boost": 0.4,      # 实体基础权重降至40%
            "entity_decay_factor": 0.6     # 实体衰减因子调整为0.6
        }
        
        boost_config = boost_config or default_boost
        terminology_boost = boost_config.get("terminology_boost", default_boost["terminology_boost"])
        entity_base_boost = boost_config.get("entity_base_boost", default_boost["entity_base_boost"])
        entity_decay_factor = boost_config.get("entity_decay_factor", default_boost["entity_decay_factor"])

        # Build parent filters
        parent_filters = []
        if metadata_filter:
            for key, value in metadata_filter.items():
                if isinstance(value, list):
                    parent_filters.append({
                        "terms": {f"document_metadata.{key}": value}
                    })
                else:
                    parent_filters.append({
                        "term": {f"document_metadata.{key}": value}
                    })
        
        # Child filter based on parent
        chunk_filter = {
            "has_parent": {
                "parent_type": "document",
                "query": {"bool": {"filter": parent_filters}} if parent_filters else {"match_all": {}}
            }
        }

        # 构建增强的文本查询
        text_queries = []

        # 基础查询
        text_queries.append({
            "match": {
                "content": {
                    "query": query_text,
                    "boost": 1.0
                }
            }
        })

        # 术语扩展查询 - 权重提升
        if terminology:
            for term in terminology:
                text_queries.append({
                    "match_phrase_prefix": {
                        "content": {
                            "query": term,
                            "boost": terminology_boost
                        }
                    }
                })

        # k-hop实体扩展查询 - 动态权重计算
        if k_hop_entities:
            for hop_level, entities_at_level in enumerate(k_hop_entities):
                if entities_at_level:
                    # 权重随跳数衰减，但起始权重降低
                    level_boost = entity_base_boost * (entity_decay_factor ** hop_level)
                    text_queries.append({
                        "terms": {
                            "metadata.entities": entities_at_level,
                            "boost": level_boost
                        }
                    })

        text_search_body = {
            "query": {
                "bool": {
                    "should": text_queries,
                    "filter": [chunk_filter],
                    "minimum_should_match": 1
                }
            },
            "size": size * 2,
            "_source": ["content", "metadata"]
        }

        # Vector search body (if model is available)
        vector_search_body = None
        if self.model:
            # 构建增强的查询文本
            enhanced_query_text = await self._build_query_prompt(
                query_text, terminology, k_hop_entities
            )

            vector_search_body = {
                "knn": {
                    "field": "embedding",
                    "query_vector_builder": {
                        "text_embedding": {
                            "model_id": self.model.inference_id,
                            "model_text": enhanced_query_text,
                        }
                    },
                    "k": size * 2,
                    "num_candidates": size * 10,
                    "filter": [chunk_filter]
                },
                "size": size * 2,
                "_source": ["content", "metadata"]
            }

        return text_search_body, vector_search_body
    
    async def query_and_rrf(self, query_bodies: List[tuple], size: int = 5) -> List[Dict]:
        """
        执行多个查询并使用 RRF 算法合并结果
        
        Args:
            query_bodies: 查询体列表，每个元素为 (query_body, search_type)
            size: 最终返回结果数量
            
        Returns:
            List[Dict]: 合并后的查询结果
        """
        if not query_bodies:
            return []
        
        # 准备并发查询任务
        tasks = []
        search_types = []
        
        for query_body, search_type in query_bodies:
            if query_body is not None:
                search_task = partial(self.client.async_client.search, index=self.index_name, body=query_body)
                tasks.append(search_task())
                search_types.append(search_type)
        
        if not tasks:
            return []
        
        # 使用 asyncio.gather 并发执行查询
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and prepare for RRF merging
        search_results = []
        all_chunk_data = {}
        max_vector_score = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logging.warning(f"Search execution failed: {response}")
                continue
            
            search_type = search_types[i]
            chunk_results = []
            
            for hit in response['hits']['hits']:
                chunk_key = hit['_id']
                chunk_results.append((chunk_key, hit['_score']))
                if search_type == "vector" and hit['_score'] > max_vector_score:
                    max_vector_score = hit['_score']
                # Store detailed information for the chunk
                if chunk_key not in all_chunk_data:
                    all_chunk_data[chunk_key] = {
                        'document_id': hit.get('_routing', chunk_key.split('_')[0]),
                        'chunk_content': hit['_source'].get('content', ''),
                        'metadata': hit['_source'].get('metadata', {}),
                        'score': [{
                            'search_type': search_type,
                            'score': hit['_score'],
                        }]
                    }
                else:
                    all_chunk_data[chunk_key]['score'].append({
                        'search_type': search_type,
                        'score': hit['_score'],
                    })
            
            search_results.append(chunk_results)
        
        # Merge results using RRF algorithm
        if len(search_results) == 1:
            merged_results = search_results[0]
        elif len(search_results) > 1:
            merged_results = rrf(*search_results, k=60)
        else:
            merged_results = []
        
        # Get parent documents for final results
        parent_ids = list(set(all_chunk_data[chunk_key]['document_id'] for chunk_key, _ in merged_results[:size]))
        parent_docs = {}
        
        if parent_ids:
            try:
                docs_response = self.client.client.mget(index=self.index_name, body={"ids": parent_ids})
                parent_docs = {doc['_id']: doc['_source'] for doc in docs_response['docs'] if doc['found']}
            except Exception as e:
                logging.warning(f"Failed to get parent documents: {e}")
        
        # Build final results
        final_results = []
        max_rrf_score = merged_results[0][1] if merged_results else 1
        for chunk_key, rrf_score in merged_results[:size]:
            if chunk_key in all_chunk_data:
                result = all_chunk_data[chunk_key].copy()
                result['rrf_score'] = rrf_score
                result['final_score'] = rrf_score / max_rrf_score * max_vector_score
                # Add parent document information
                parent_id = result['document_id']
                if parent_id in parent_docs:
                    result['document_name'] = parent_docs[parent_id].get('name', '')
                    result['document_metadata'] = parent_docs[parent_id].get('document_metadata', {})
                else:
                    result['document_name'] = ''
                    result['document_metadata'] = {}
                
                final_results.append(result)
        
        return final_results
    
    async def query(self, query_text: str, metadata_filter: Optional[Dict] = None, 
                   size: int = 5, terminology: Optional[List[str]] = None,
                   k_hop_entities: Optional[List[List[str]]] = None,
                   boost_config: Optional[Dict] = None) -> List[Dict]:
        """
        使用增强查询进行检索，支持术语库和知识图谱扩展

        Args:
            query_text: 查询文本
            metadata_filter: 元数据过滤条件
            size: 返回结果数量
            terminology: 术语库匹配的相关术语列表
            k_hop_entities: k-hop实体扩展结果，格式为 [[1-hop entities], [2-hop entities], ...]
            boost_config: 权重配置字典

        Returns:
            List[Dict]: 查询结果列表
        """
        # Build enhanced queries
        text_search_body, vector_search_body = await self.build_query(
            query_text, metadata_filter, size, terminology, k_hop_entities, boost_config
        )

        # Prepare query bodies for execution
        query_bodies = [
            (text_search_body, "text")
        ]
        
        if vector_search_body is not None:
            query_bodies.append((vector_search_body, "vector"))

        # Execute queries and merge results using RRF
        return await self.query_and_rrf(query_bodies, size)
    
    def get(self, document_id: str) -> Optional[Dict]:
        """Get the specified document (parent only)"""
        try:
            response = self.client.client.get(
                index=self.index_name,
                id=document_id
            )
            return response['_source']
        except NotFoundError:
            return None
        except Exception as e:
            logging.error(f"Failed to get document: {e}")
            raise
    
    def delete(self, document_id: str) -> bool:
        """Delete the specified document and all its chunks"""
        try:
            # Delete all child chunks first
            self.client.client.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "has_parent": {
                            "parent_type": "document",
                            "query": {"term": {"_id": document_id}}
                        }
                    }
                },
                refresh=True,
                conflicts='proceed'
            )
            
            # Delete parent document
            self.client.client.delete(
                index=self.index_name,
                id=document_id,
                refresh='wait_for'
            )
            return True
        except NotFoundError:
            return False
        except Exception as e:
            logging.error(f"Failed to delete document: {e}")
            raise
    
    def list_documents(self, offset: int = 0, limit: int = 10) -> Dict:
        """List documents in the collection (parent documents only)"""
        try:
            response = self.client.client.search(
                index=self.index_name,
                body={
                    "query": {
                        "term": {"doc_chunk_relation": "document"}
                    },
                    "_source": ["name", "document_metadata"],
                    "from": offset,
                    "size": limit
                }
            )            
            return {
                "total": response['hits']['total']['value'],
                "documents": [
                    {
                        "id": hit['_id'],
                        "name": hit['_source'].get('name', ''),
                        "metadata": hit['_source'].get('document_metadata', {})
                    }
                    for hit in response['hits']['hits']
                ]
            }
        except NotFoundError:
            return {"total": 0, "documents": []}
        except Exception as e:
            logging.error(f"Failed to list documents: {e}")
            raise
    
    def drop(self):
        """Delete the entire collection"""
        try:
            if self.client.client.indices.exists(index=self.index_name):
                self.client.client.indices.delete(index=self.index_name)
                logging.debug(f"Deleted index successfully: {self.index_name}")
        except Exception as e:
            logging.error(f"Failed to delete collection: {e}")
            raise