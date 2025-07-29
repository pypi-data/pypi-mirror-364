import requests
import time
from typing import Dict, Any, Optional
from .database import DatabaseManager
from .utils import TokenCalculator, validate_parameters
from .exceptions import APIError, DatabaseError

class LLMWrapper:
    
    def __init__(
        self,
        service_url: str,
        api_key: str,
        db_config: Dict[str, Any],
        deployment_name: str,
        api_version: str,
        default_model: str = "gpt-4",
        timeout: int = 30,
        auto_create_tables: bool = True
    ):
        self.service_url = service_url.rstrip('/')
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.default_model = default_model
        self.timeout = timeout
        
        # Initialize components
        self.db_manager = DatabaseManager(db_config)
        self.token_calculator = TokenCalculator()
        
        if auto_create_tables:
            self.db_manager.create_tables()
    
    def send_request(
        self,
        input_text: str,
        customer_id: int,
        organization_id: int,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        start_time = time.time()
        model_name = model or self.default_model
        
        # Validate and prepare parameters
        validated_params = validate_parameters(kwargs)
        
        # Prepare request payload for Azure OpenAI
        request_params = {
            "messages": [
                {"role": "user", "content": input_text}
            ],
            **validated_params
        }
        
        try:
            # Send request to Azure OpenAI API
            response = self._make_api_request(request_params)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response and calculate tokens
            result = self._process_response(
                response,
                input_text,
                customer_id,
                organization_id,
                model_name,
                request_params,
                response_time_ms
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Log failed request
            self._log_failed_request(
                customer_id,
                organization_id,
                model_name,
                request_params,
                str(e),
                response_time_ms
            )
            
            raise APIError(f"Request failed: {e}")
    
    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Azure OpenAI API"""
        # Azure OpenAI headers
        headers = {
            "api-key": self.api_key,  # Azure uses api-key instead of Authorization
            "Content-Type": "application/json"
        }
        
        # Construct Azure OpenAI URL
        url = f"{self.service_url}/openai/deployments/{self.deployment_name}/chat/completions"
        
        # Add API version as query parameter
        params_with_version = {
            "api-version": self.api_version
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                params=params_with_version,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get("message", response.text)
                except ValueError:
                    error_detail = response.text
                
                raise APIError(f"Azure OpenAI API request failed with status {response.status_code}: {error_detail}")
                
        except requests.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")
    
    def _process_response(
        self,
        response_data: Dict[str, Any],
        input_text: str,
        customer_id: int,
        organization_id: int,
        model_name: str,
        request_params: Dict[str, Any],
        response_time_ms: int
    ) -> Dict[str, Any]:
        """Process Azure OpenAI API response and log usage"""
        
        # Extract output text from Azure OpenAI response format
        output_text = ""
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice:
                output_text = choice["message"].get("content", "")
            elif "text" in choice:
                output_text = choice.get("text", "")
        
        # Get token usage from Azure OpenAI response
        usage = response_data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        
        # Fallback to manual calculation if usage not provided
        if not usage:
            input_tokens = self.token_calculator.count_tokens(input_text, model_name)
            output_tokens = self.token_calculator.count_tokens(output_text, model_name)
            total_tokens = input_tokens + output_tokens
        
        # Log to database
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                request_params=request_params,
                response_params=response_data,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                status="success"
            )
        except DatabaseError as e:
            # Log database error but don't fail the request
            print(f"Warning: Failed to log to database: {e}")
        
        return {
            "output_text": output_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "response_time_ms": response_time_ms,
            "model": model_name,
            "full_response": response_data
        }
    
    def _log_failed_request(
        self,
        customer_id: int,
        organization_id: int,
        model_name: str,
        request_params: Dict[str, Any],
        error_message: str,
        response_time_ms: int
    ):
        """Log failed request to database"""
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                request_params=request_params,
                response_params={"error": error_message},
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                response_time_ms=response_time_ms,
                status="failed"
            )
        except DatabaseError:
            pass  # Don't fail on logging errors
    
    def get_usage_stats(
        self,
        customer_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage statistics"""
        from datetime import datetime
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        return self.db_manager.get_usage_stats(
            customer_id=customer_id,
            organization_id=organization_id,
            start_date=start_dt,
            end_date=end_dt
        )
    
    def close(self):
        """Close database connections"""
        self.db_manager.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()