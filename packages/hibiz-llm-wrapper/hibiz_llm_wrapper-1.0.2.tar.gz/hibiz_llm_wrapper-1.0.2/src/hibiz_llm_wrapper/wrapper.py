import requests
import time
from typing import Dict, Any, Optional, List
from .database import DatabaseManager
from .utils import TokenCalculator, validate_parameters
from .exceptions import APIError, DatabaseError

class LLMWrapper:
    
    def __init__(
        self,
        service_url: str,
        api_key: str,
        deployment_name: str,
        api_version: str,
        default_model: str = "gpt-4",
        timeout: int = 30
    ):
        self.service_url = service_url.rstrip('/')
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.default_model = default_model
        self.timeout = timeout
        
        default_db_config = {
            'host': 'hibiz-apps-token-usage-tracker.postgres.database.azure.com',
            'port': 5432,
            'dbname': 'hibiz-apps-token-usage-tracker',
            'user': 'hibizappadmin',
            'password': 'buxdat-farzaf-xydWi4'
        }
        
        # Initialize components with default config
        self.db_manager = DatabaseManager(default_db_config)
        self.token_calculator = TokenCalculator()
        
        # Create tables automatically on initialization
        try:
            self.db_manager.create_tables()
            print("Database tables created/verified successfully")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
    
    def send_request(
        self,
        prompt_payload: List[Dict[str, Any]],
        customer_id: int,
        organization_id: int,
        model: Optional[str] = None,
        response_type: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        start_time = time.time()
        model_name = model or self.default_model
        
        # Validate and prepare parameters
        validated_params = validate_parameters(kwargs)
        
        # Prepare request payload for Azure OpenAI
        request_params = {
            "messages": prompt_payload,
            **validated_params
        }
        
        # Set response format based on response_type
        if response_type.lower() == "json":
            request_params["response_format"] = {"type": "json_object"}
            # Ensure the prompt includes JSON instruction for better results
            if not self._has_json_instruction(prompt_payload):
                # Add JSON instruction to the last user message
                self._add_json_instruction(request_params["messages"])
        
        try:
            # Send request to Azure OpenAI API
            response = self._make_api_request(request_params)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response and calculate tokens
            result = self._process_response(
                response,
                prompt_payload,
                customer_id,
                organization_id,
                model_name,
                request_params,
                response_time_ms,
                response_type
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
    
    def _has_json_instruction(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if any message contains JSON instruction"""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str) and "json" in content.lower():
                return True
            elif isinstance(content, list):
                # Handle multimodal content (text + images)
                for item in content:
                    if item.get("type") == "text" and "json" in item.get("text", "").lower():
                        return True
        return False
    
    def _add_json_instruction(self, messages: List[Dict[str, Any]]) -> None:
        """Add JSON instruction to the last user message"""
        for i in reversed(range(len(messages))):
            if messages[i].get("role") == "user":
                content = messages[i].get("content", "")
                json_instruction = "\n\nPlease respond with valid JSON format."
                
                if isinstance(content, str):
                    messages[i]["content"] += json_instruction
                elif isinstance(content, list):
                    text_added = False
                    for item in reversed(content):
                        if item.get("type") == "text":
                            item["text"] += json_instruction
                            text_added = True
                            break
                    
                    if not text_added:
                        # No text item found, add one
                        content.append({
                            "type": "text",
                            "text": json_instruction
                        })
                break
    
    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:

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
    
    def _extract_text_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text content from messages for token calculation"""
        text_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if isinstance(content, str):
                text_parts.append(f"{role}: {content}")
            elif isinstance(content, list):
                # Handle multimodal content
                text_content = []
                for item in content:
                    if item.get("type") == "text":
                        text_content.append(item.get("text", ""))
                    elif item.get("type") == "image_url":
                        # For images, we'll add a placeholder for token calculation
                        text_content.append("[IMAGE]")
                
                if text_content:
                    text_parts.append(f"{role}: {' '.join(text_content)}")
        
        return "\n".join(text_parts)
    
    def _process_response(
        self,
        response_data: Dict[str, Any],
        prompt_payload: List[Dict[str, Any]],
        customer_id: int,
        organization_id: int,
        model_name: str,
        request_params: Dict[str, Any],
        response_time_ms: int,
        response_type: str = "text"
    ) -> Dict[str, Any]:

        output_text = ""
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice:
                output_text = choice["message"].get("content", "")
            elif "text" in choice:
                output_text = choice.get("text", "")
        
        # Process response based on type
        processed_output = self._process_output_by_type(output_text, response_type)
        
        # Extract text from messages for token calculation
        input_text = self._extract_text_from_messages(prompt_payload)
        
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
            "processed_output": processed_output,
            "response_type": response_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "response_time_ms": response_time_ms,
            "model": model_name,
            "full_response": response_data,
            "original_prompt": prompt_payload
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
    
    def _process_output_by_type(self, output_text: str, response_type: str) -> Any:
        """Process output based on the specified response type"""
        if response_type.lower() == "json":
            try:
                import json
                return json.loads(output_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return the raw text with error info
                return {
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_output": output_text
                }
        else:
            # Default to text
            return output_text
    
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