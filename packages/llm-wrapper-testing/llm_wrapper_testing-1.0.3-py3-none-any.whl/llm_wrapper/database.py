# from abc import ABC, abstractmethod
# from datetime import datetime
# from typing import Dict, Any, Optional
# from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # SQLAlchemy Base
# Base = declarative_base()

# class TokenUsageLog(Base):
#     """SQLAlchemy model for token usage logging"""
#     __tablename__ = 'token_usage_log'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     customer_id = Column(Integer, nullable=False)
#     organization_id = Column(Integer, nullable=False)
#     model_name = Column(String(255), nullable=False)
#     request_params = Column(JSON)
#     response_params = Column(JSON)
#     input_tokens = Column(Integer, nullable=False)
#     output_tokens = Column(Integer, nullable=False)
#     total_tokens = Column(Integer, nullable=False)
#     request_timestamp = Column(DateTime, default=datetime.utcnow)
#     response_time_ms = Column(Integer, nullable=False)
#     status = Column(String(50), default='success')

# class DatabaseError(Exception):
#     pass

# class BaseDatabaseManager(ABC):
    
#     @abstractmethod
#     def create_tables(self) -> None:
#         pass
    
#     @abstractmethod
#     def log_token_usage(
#         self,
#         customer_id: int,
#         organization_id: int,
#         model_name: str,
#         request_params: Dict[str, Any],
#         response_params: Dict[str, Any],
#         input_tokens: int,
#         output_tokens: int,
#         total_tokens: int,
#         response_time_ms: int,
#         status: str = 'success'
#     ) -> None:
#         pass
    
#     @abstractmethod
#     def get_usage_stats(
#         self,
#         customer_id: Optional[int] = None,
#         organization_id: Optional[int] = None,
#         start_date: Optional[datetime] = None,
#         end_date: Optional[datetime] = None
#     ) -> Dict[str, Any]:
#         pass
    
#     @abstractmethod
#     def close(self) -> None:
#         """Close database connection"""
#         pass

# class SQLDatabaseManager(BaseDatabaseManager):
#     """SQL Database Manager using SQLAlchemy"""
    
#     def __init__(self, db_config: Dict[str, Any]):
#         self.db_config = db_config
#         self.engine = None
#         self.Session = None
#         self._initialize_db()
    
#     def _initialize_db(self) -> None:
#         """Initialize database connection"""
#         try:
#             # Build connection string based on database type
#             db_type = self.db_config.get('type', 'postgresql')
            
#             if db_type == 'postgresql':
#                 connection_string = (
#                     f"postgresql://{self.db_config['user']}:"
#                     f"{self.db_config['password']}@{self.db_config['host']}:"
#                     f"{self.db_config['port']}/{self.db_config['dbname']}"
#                 )
#             elif db_type == 'mysql':
#                 connection_string = (
#                     f"mysql+pymysql://{self.db_config['user']}:"
#                     f"{self.db_config['password']}@{self.db_config['host']}:"
#                     f"{self.db_config['port']}/{self.db_config['dbname']}"
#                 )
#             elif db_type == 'sqlite':
#                 connection_string = f"sqlite:///{self.db_config.get('dbname', 'llm_wrapper.db')}"
#             else:
#                 raise DatabaseError(f"Unsupported SQL database type: {db_type}")
            
#             self.engine = create_engine(connection_string, echo=False)
#             self.Session = sessionmaker(bind=self.engine)
#             logger.info(f"Connected to {db_type} database")
            
#         except Exception as e:
#             raise DatabaseError(f"Failed to connect to SQL database: {e}")
    
#     def create_tables(self) -> None:
#         """Create necessary tables"""
#         try:
#             Base.metadata.create_all(self.engine)
#             logger.info("SQL tables created successfully")
#         except Exception as e:
#             raise DatabaseError(f"Failed to create SQL tables: {e}")
    
#     def log_token_usage(
#         self,
#         customer_id: int,
#         organization_id: int,
#         model_name: str,
#         request_params: Dict[str, Any],
#         response_params: Dict[str, Any],
#         input_tokens: int,
#         output_tokens: int,
#         total_tokens: int,
#         response_time_ms: int,
#         status: str = 'success'
#     ) -> None:
#         """Log token usage to SQL database"""
#         session: Session = self.Session()
#         try:
#             log_entry = TokenUsageLog(
#                 customer_id=customer_id,
#                 organization_id=organization_id,
#                 model_name=model_name,
#                 request_params=request_params,
#                 response_params=response_params,
#                 input_tokens=input_tokens,
#                 output_tokens=output_tokens,
#                 total_tokens=total_tokens,
#                 request_timestamp=datetime.utcnow(),
#                 response_time_ms=response_time_ms,
#                 status=status
#             )
#             session.add(log_entry)
#             session.commit()
#             logger.info(f"Token usage logged for customer {customer_id}")
#         except Exception as e:
#             session.rollback()
#             raise DatabaseError(f"Failed to log token usage: {e}")
#         finally:
#             session.close()
    
#     def get_usage_stats(
#         self,
#         customer_id: Optional[int] = None,
#         organization_id: Optional[int] = None,
#         start_date: Optional[datetime] = None,
#         end_date: Optional[datetime] = None
#     ) -> Dict[str, Any]:
#         """Get usage statistics from SQL database"""
#         session: Session = self.Session()
#         try:
#             query = session.query(TokenUsageLog)
            
#             if customer_id:
#                 query = query.filter(TokenUsageLog.customer_id == customer_id)
#             if organization_id:
#                 query = query.filter(TokenUsageLog.organization_id == organization_id)
#             if start_date:
#                 query = query.filter(TokenUsageLog.request_timestamp >= start_date)
#             if end_date:
#                 query = query.filter(TokenUsageLog.request_timestamp <= end_date)
            
#             logs = query.all()
            
#             # Aggregate statistics
#             stats = {
#                 "models": {},
#                 "total_requests": len(logs),
#                 "total_tokens": 0
#             }
            
#             for log in logs:
#                 model_name = log.model_name
#                 if model_name not in stats["models"]:
#                     stats["models"][model_name] = {
#                         "model_name": model_name,
#                         "requests": 0,
#                         "input_tokens": 0,
#                         "output_tokens": 0,
#                         "total_tokens": 0,
#                         "response_times": []
#                     }
                
#                 stats["models"][model_name]["requests"] += 1
#                 stats["models"][model_name]["input_tokens"] += log.input_tokens
#                 stats["models"][model_name]["output_tokens"] += log.output_tokens
#                 stats["models"][model_name]["total_tokens"] += log.total_tokens
#                 stats["models"][model_name]["response_times"].append(log.response_time_ms)
#                 stats["total_tokens"] += log.total_tokens
            
#             # Calculate average response times
#             for model_stats in stats["models"].values():
#                 if model_stats["response_times"]:
#                     model_stats["avg_response_time_ms"] = sum(model_stats["response_times"]) / len(model_stats["response_times"])
#                 else:
#                     model_stats["avg_response_time_ms"] = 0
#                 del model_stats["response_times"]
            
#             stats["models"] = list(stats["models"].values())
#             return stats
            
#         except Exception as e:
#             raise DatabaseError(f"Failed to get usage stats: {e}")
#         finally:
#             session.close()
    
#     def close(self) -> None:
#         """Close database connection"""
#         if self.engine:
#             self.engine.dispose()
#             logger.info("SQL database connection closed")


    
#     def close(self) -> None:
#         """Close MongoDB connection"""
#         if self.client:
#             self.client.close()
#             logger.info("MongoDB connection closed")

# class DatabaseManagerFactory:
#     """Factory class to create appropriate database manager"""
    
#     @staticmethod
#     def create_manager(db_config: Dict[str, Any]) -> BaseDatabaseManager:
#         """Create database manager based on configuration"""
#         db_type = db_config.get('type', '').lower()
        
#         sql_types = ['postgresql', 'mysql', 'sqlite', 'mssql']
        
#         if db_type in sql_types:
#             return SQLDatabaseManager(db_config)
#         else:
#             raise DatabaseError(f"Unsupported database type: {db_type}")

# class DatabaseManager:
#     """Main database manager that uses factory pattern"""
    
#     def __init__(self, db_config: Dict[str, Any]):
#         self.manager = DatabaseManagerFactory.create_manager(db_config)
    
#     def create_tables(self) -> None:
#         """Create necessary tables/collections"""
#         return self.manager.create_tables()
    
#     def log_token_usage(
#         self,
#         customer_id: int,
#         organization_id: int,
#         model_name: str,
#         request_params: Dict[str, Any],
#         response_params: Dict[str, Any],
#         input_tokens: int,
#         output_tokens: int,
#         total_tokens: int,
#         response_time_ms: int,
#         status: str = 'success'
#     ) -> None:
#         """Log token usage"""
#         return self.manager.log_token_usage(
#             customer_id, organization_id, model_name, request_params,
#             response_params, input_tokens, output_tokens, total_tokens,
#             response_time_ms, status
#         )
    
#     def get_usage_stats(
#         self,
#         customer_id: Optional[int] = None,
#         organization_id: Optional[int] = None,
#         start_date: Optional[datetime] = None,
#         end_date: Optional[datetime] = None
#     ) -> Dict[str, Any]:
#         """Get usage statistics"""
#         return self.manager.get_usage_stats(customer_id, organization_id, start_date, end_date)
    
#     def close(self) -> None:
#         """Close database connection"""
#         return self.manager.close()
    
#     def __enter__(self):
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class TokenUsageLog(Base):
    """SQLAlchemy model for token usage logging"""
    __tablename__ = 'token_usage_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    organization_id = Column(Integer, nullable=False)
    model_name = Column(String(255), nullable=False)
    request_params = Column(JSON)
    response_params = Column(JSON)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    request_timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=False)
    status = Column(String(50), default='success')

class DatabaseError(Exception):
    pass

class DatabaseManager:
    """PostgreSQL Database Manager using SQLAlchemy"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.engine = None
        self.Session = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize PostgreSQL database connection"""
        try:
            # Build PostgreSQL connection string
            connection_string = (
                f"postgresql://{self.db_config['user']}:"
                f"{self.db_config['password']}@{self.db_config['host']}:"
                f"{self.db_config['port']}/{self.db_config['dbname']}"
            )
            
            self.engine = create_engine(connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL database")
            
        except Exception as e:
            raise DatabaseError(f"Failed to connect to PostgreSQL database: {e}")
    
    def create_tables(self) -> None:
        """Create necessary tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("PostgreSQL tables created successfully")
        except Exception as e:
            raise DatabaseError(f"Failed to create PostgreSQL tables: {e}")
    
    def log_token_usage(
        self,
        customer_id: int,
        organization_id: int,
        model_name: str,
        request_params: Dict[str, Any],
        response_params: Dict[str, Any],
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        response_time_ms: int,
        status: str = 'success'
    ) -> None:
        """Log token usage to PostgreSQL database"""
        session: Session = self.Session()
        try:
            log_entry = TokenUsageLog(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                request_params=request_params,
                response_params=response_params,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                request_timestamp=datetime.utcnow(),
                response_time_ms=response_time_ms,
                status=status
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"Token usage logged for customer {customer_id}")
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Failed to log token usage: {e}")
        finally:
            session.close()
    
    def get_usage_stats(
        self,
        customer_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get usage statistics from PostgreSQL database"""
        session: Session = self.Session()
        try:
            query = session.query(TokenUsageLog)
            
            if customer_id:
                query = query.filter(TokenUsageLog.customer_id == customer_id)
            if organization_id:
                query = query.filter(TokenUsageLog.organization_id == organization_id)
            if start_date:
                query = query.filter(TokenUsageLog.request_timestamp >= start_date)
            if end_date:
                query = query.filter(TokenUsageLog.request_timestamp <= end_date)
            
            logs = query.all()
            
            # Aggregate statistics
            stats = {
                "models": {},
                "total_requests": len(logs),
                "total_tokens": 0
            }
            
            for log in logs:
                model_name = log.model_name
                if model_name not in stats["models"]:
                    stats["models"][model_name] = {
                        "model_name": model_name,
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "response_times": []
                    }
                
                stats["models"][model_name]["requests"] += 1
                stats["models"][model_name]["input_tokens"] += log.input_tokens
                stats["models"][model_name]["output_tokens"] += log.output_tokens
                stats["models"][model_name]["total_tokens"] += log.total_tokens
                stats["models"][model_name]["response_times"].append(log.response_time_ms)
                stats["total_tokens"] += log.total_tokens
            
            # Calculate average response times
            for model_stats in stats["models"].values():
                if model_stats["response_times"]:
                    model_stats["avg_response_time_ms"] = sum(model_stats["response_times"]) / len(model_stats["response_times"])
                else:
                    model_stats["avg_response_time_ms"] = 0
                del model_stats["response_times"]
            
            stats["models"] = list(stats["models"].values())
            return stats
            
        except Exception as e:
            raise DatabaseError(f"Failed to get usage stats: {e}")
        finally:
            session.close()
    
    def close(self) -> None:
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()