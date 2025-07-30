import logging
import os
from typing import Dict, List, Optional, Union
from elasticsearch import Elasticsearch, AsyncElasticsearch

from .user import User
from .model import Model
from .collection import Collection
from .splitter import Splitter


class Client:
    """Main client for the RAG system, managing ES connections and global configurations"""
    
    def __init__(self, hosts: Union[str, List[str]], force_recreate=None, **kwargs):
        """
        Initialize the client
        
        Args:
            hosts: Elasticsearch host addresses
            **kwargs: Other ES connection parameters
        """
        self.hosts = hosts if isinstance(hosts, list) else [hosts]
        self.client = Elasticsearch(self.hosts, **kwargs).options(ignore_status=404, request_timeout=600)
        self.async_client = AsyncElasticsearch(self.hosts, **kwargs)
        self._collections = {}
        self._predefined_models = {}
        self._user = None
        self.splitter = None
        self.force_recreate = force_recreate if force_recreate is not None else os.getenv("FORCE_RECREATE", "false").lower() == "true"
        self._init_spliter()
        self._load_existing_models()

    def add_user(self, username: str, api_key: str, metadata: Optional[Dict] = None) -> bool:
        """Add or update user credentials"""
        user = User(self, username, api_key)
        return user.create_or_update(metadata)

    def delete_user(self, username: str) -> bool:
        """Delete user credentials"""
        user = User(self, username, "")
        return user.delete()
        
    def authenticate(self, username: str, api_key: str) -> 'User':
        """Authenticate user"""
        user = User(self, username, api_key)
        if user.validate():
            self._user = user
            return self._user
        else:
            raise ValueError(f"User authentication failed: {username}")
    
    def register_model(self, model_id: str, config: Dict) -> 'Model':
        """Register a predefined model"""
        model = Model(
            client=self,
            model_id=model_id,
            config=config
        )
        self._predefined_models[model_id] = model
        return model

    def get_model(self, model_id: str) -> 'Model':
        if model_id not in self._predefined_models:
            raise ValueError(f"Model {model_id} is not predefined")
        return self._predefined_models[model_id]

    def list_models(self) -> List[Dict]:
        """List available models"""
        return [
            {
                "model_id": model_id,
                "config": model.config,
                "dimensions": model.get_dimensions()
            }
            for model_id, model in self._predefined_models.items()
        ]

    def get_collection(self, name: str, model_id: Optional[str] = None) -> 'Collection':
        """Get or create a collection (knowledge base)"""
        if not self._user:
            raise ValueError("Please call authenticate() to authenticate the user first")
        
        # If model_id is specified, use that model; otherwise, use the default model
        if model_id:
            model = self.get_model(model_id)
            collection_key = f"{model_id}__{self._user.username}__{name}"
        else:
            model = None
            collection_key = f"{self._user.username}__{name}"
            
        if collection_key not in self._collections:
            self._collections[collection_key] = Collection(
                client=self,
                name=name,
                user=self._user,
                model=model
            )
        return self._collections[collection_key]
    
    def list_collections(self) -> List[str]:
        """List all collections of the user"""
        if not self._user:
            raise ValueError("Please call authenticate() to authenticate the user first")
        
        try:
            # 使用聚合查询获取准确的集合统计信息
            pattern = f"*__{self._user.username}__*"
            # 一次性获取所有相关索引的健康状态信息
            try:
                all_health_info_list = self.client.cat.indices(
                    index=pattern, 
                    format='json',
                    h='index,health,status,store.size'
                )
                all_health_info = {info['index']: info for info in all_health_info_list}
            except Exception:
                all_health_info = {}

            # 构建聚合查询
            agg_body = {
                "size": 0,  # 不返回具体文档，只返回聚合结果
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "doc_chunk_relation": "document"
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "collections": {
                        "terms": {
                            "field": "_index",
                            "size": 1000  # 假设用户不会有超过1000个集合
                        },
                        "aggs": {
                            "doc_count": {
                                "value_count": {
                                    "field": "doc_chunk_relation"
                                }
                            },
                            "total_chunks": {
                                "sum": {
                                    "field": "chunks"
                                }
                            },
                            "avg_chunks": {
                                "avg": {
                                    "field": "chunks"
                                }
                            },
                            "max_chunks": {
                                "max": {
                                    "field": "chunks"
                                }
                            },
                            "min_chunks": {
                                "min": {
                                    "field": "chunks"
                                }
                            }
                        }
                    }
                }
            }
            
            # 执行聚合查询
            response = self.client.search(
                index=pattern,
                body=agg_body,
                ignore=[404]
            )
            
            collections = []
            if 'aggregations' in response and 'collections' in response['aggregations']:
                for bucket in response['aggregations']['collections']['buckets']:
                    index_name = bucket['key']
                    # 解析索引名称格式
                    # 支持格式: {model_id}__{username}__{collection_name} 或 {username}__{collection_name}
                    if f"__{self._user.username}__" in index_name:
                        parts = index_name.split(f"__{self._user.username}__")
                        if len(parts) == 2:
                            model_part = parts[0]
                            collection_name = parts[1]
                            # 判断是否有模型ID
                            if model_part and model_part in self._predefined_models:
                                model_id = model_part
                            else:
                                model_id = None
                        else:
                            continue  # 跳过无法解析的索引
                    else:
                        continue  # 跳过不符合命名规范的索引
                    # 从预先获取的信息中查找健康状态
                    health_info = all_health_info.get(index_name, {})                    
                    collection_info = {
                        "name": collection_name,
                        "model_id": model_id,
                        "index": index_name,
                        "health": health_info.get('health', 'unknown'),
                        "status": health_info.get('status', 'unknown'),
                        "store_size": health_info.get('store.size', '0b'),
                        "doc_count": int(bucket['doc_count']['value']),
                        "total_chunks": int(bucket['total_chunks']['value'] or 0),
                        "avg_chunks": round(bucket['avg_chunks']['value'] or 0, 2),
                        "max_chunks": int(bucket['max_chunks']['value'] or 0),
                        "min_chunks": int(bucket['min_chunks']['value'] or 0)
                    }
                    collections.append(collection_info)
            # 按集合名称排序
            collections.sort(key=lambda x: x['name'])
            logging.debug(f"Found {len(collections)} collections for user {self._user.username}")
            return collections
        except Exception as e:
            logging.error(f"Failed to list collections: {e}")
            return []

    def _load_existing_models(self):
        """Load all existing model inference service configurations from ES"""
        try:
            # Get all inference services
            response = self.client.inference.get()
            for config in response.get('endpoints', {}):
                inference_id = config.get('inference_id', '')
                if inference_id.endswith('__inference'):
                    model_id = inference_id.replace('__inference', '')
                    # If not in predefined models, rebuild from configuration
                    if model_id not in self._predefined_models:
                        service_config = {
                            "service": config.get('service', 'openai'),
                            "service_settings": config.get('service_settings', {}),
                            "dimensions": config.get('service_settings', {}).get('dimensions', 384)
                        }
                        model = Model(
                            client=self,
                            model_id=model_id,
                            config=service_config
                        )
                        # Mark as existing to avoid repeated initialization
                        model._exists = True
                        self._predefined_models[model_id] = model
            logging.debug(f"Loaded {len(self._predefined_models)} models")
        except Exception as e:
            logging.warning(f"Failed to load existing models: {e}")

    def _init_spliter(self):
        self.splitter = Splitter()
        self.splitter.init_script(self.client, force_recreate=self.force_recreate)
