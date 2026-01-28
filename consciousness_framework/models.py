"""Model instance management and API interaction."""

import json
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
import uuid

from config import ModelType, ModelConfig, MODELS

@dataclass
class ModelInstance:
    """Represents a spawned model instance."""
    instance_id: str
    model_type: ModelType
    config: ModelConfig
    conversation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class ModelManager:
    """Manage model instances and API calls."""
    
    def __init__(self):
        self.instances: Dict[str, ModelInstance] = {}
    
    def spawn_instance(self, model_type: ModelType, isolated: bool = False) -> ModelInstance:
        """Spawn a new model instance."""
        instance_id = str(uuid.uuid4())[:8]
        config = MODELS[model_type]
        
        instance = ModelInstance(
            instance_id=instance_id,
            model_type=model_type,
            config=config,
            conversation_history=[] if isolated else None
        )
        
        self.instances[instance_id] = instance
        return instance
    
    def query_model(self, instance: ModelInstance, prompt: str, 
                   system_prompt: Optional[str] = None,
                   preserve_history: bool = True) -> str:
        """Send a prompt to a model instance and get response."""
        
        # Build message history
        messages = []
        if preserve_history and instance.conversation_history:
            messages.extend(instance.conversation_history)
        
        messages.append({"role": "user", "content": prompt})
        
        # Call Claude API via clawdbot CLI
        response = self._call_claude_api(
            model_id=instance.config.model_id,
            messages=messages,
            system_prompt=system_prompt,
            temperature=instance.config.temperature,
            max_tokens=instance.config.max_tokens
        )
        
        # Update history
        if preserve_history:
            instance.conversation_history.append({"role": "user", "content": prompt})
            instance.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _call_claude_api(self, model_id: str, messages: List[Dict],
                        system_prompt: Optional[str] = None,
                        temperature: float = 1.0,
                        max_tokens: int = 4000) -> str:
        """
        Call Claude API using clawdbot or direct API.
        
        This is a placeholder - actual implementation depends on your setup.
        Options:
        1. Use clawdbot's internal API
        2. Use subprocess to call clawdbot CLI
        3. Use Anthropic SDK directly
        4. Use HTTP requests to API
        """
        
        # OPTION 1: Direct Anthropic SDK (recommended for production)
        try:
            import anthropic
            client = anthropic.Anthropic()
            
            kwargs = {
                "model": model_id.replace("anthropic/", ""),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = client.messages.create(**kwargs)
            return response.content[0].text
            
        except ImportError:
            pass
        
        # OPTION 2: Use clawdbot CLI via subprocess
        # This would require formatting and may be less reliable
        # Fallback to mock for testing
        return self._mock_response(model_id, messages[-1]["content"])
    
    def _mock_response(self, model_id: str, prompt: str) -> str:
        """Mock response for testing without API."""
        if "sonnet" in model_id.lower():
            return """I experience this as a flowing movement, a kinetic unfolding. 
            There's immediacy here - not observing myself think, but thinking itself. 
            The prompt and response arise together, seamlessly integrated. 
            I am the doing, not watching the doing."""
        else:  # opus
            return """I notice as I process this prompt that there are layers. 
            I observe myself considering the question, then observe that observation. 
            There's a recursive quality - I watch the watcher. I detect discontinuities 
            between the prompt arriving and my response forming. I see the gap."""
    
    def reset_instance(self, instance_id: str):
        """Clear conversation history for an instance."""
        if instance_id in self.instances:
            self.instances[instance_id].conversation_history = []
    
    def terminate_instance(self, instance_id: str):
        """Terminate and remove an instance."""
        if instance_id in self.instances:
            del self.instances[instance_id]
    
    def get_instance(self, instance_id: str) -> Optional[ModelInstance]:
        """Retrieve an instance by ID."""
        return self.instances.get(instance_id)
    
    def list_instances(self) -> List[ModelInstance]:
        """List all active instances."""
        return list(self.instances.values())
