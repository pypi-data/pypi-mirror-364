import tiktoken
from typing import Optional, Dict, Any
from .exceptions import TokenizationError

class TokenCalculator:
    """Handles token calculation for different models"""
    
    def __init__(self, default_encoding: str = "cl100k_base"):
        self.default_encoding = default_encoding
        self._encoders: Dict[str, tiktoken.Encoding] = {}
    
    def get_encoder(self, model_name: Optional[str] = None) -> tiktoken.Encoding:
        """Get appropriate encoder for model"""
        if model_name and model_name not in self._encoders:
            try:
                # Try to get model-specific encoding
                if "gpt-4" in model_name.lower():
                    self._encoders[model_name] = tiktoken.encoding_for_model("gpt-4")
                elif "gpt-3.5" in model_name.lower():
                    self._encoders[model_name] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                else:
                    # Use default encoding for other models
                    self._encoders[model_name] = tiktoken.get_encoding(self.default_encoding)
            except Exception:
                # Fallback to default encoding
                self._encoders[model_name] = tiktoken.get_encoding(self.default_encoding)
        
        return self._encoders.get(model_name) or tiktoken.get_encoding(self.default_encoding)
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        """Count tokens in text"""
        try:
            encoder = self.get_encoder(model_name)
            return len(encoder.encode(text))
        except Exception as e:
            raise TokenizationError(f"Failed to count tokens: {e}")

def validate_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize parameters"""
    validated = {}
    
    # Define valid parameter ranges
    param_ranges = {
        "temperature": (0.0, 2.0),
        "top_p": (0.0, 1.0),
        "frequency_penalty": (-2.0, 2.0),
        "presence_penalty": (-2.0, 2.0),
        "max_tokens": (1, 8000)
    }
    
    for key, value in params.items():
        if key in param_ranges:
            min_val, max_val = param_ranges[key]
            if isinstance(value, (int, float)):
                validated[key] = max(min_val, min(max_val, value))
            else:
                validated[key] = value
        else:
            validated[key] = value
    
    return validated