"""AI-powered code generation based on user requirements and template analysis."""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from langchain_mistralai import ChatMistralAI
    HAS_MISTRAL = True
except ImportError:
    HAS_MISTRAL = False

from langchain_core.messages import HumanMessage, SystemMessage
from jinja2 import Template

logger = logging.getLogger(__name__)

@dataclass
class CodeGenerationRequest:
    """Request for AI code generation."""
    user_requirements: str
    project_type: str
    file_path: str
    file_purpose: str
    template_patterns: Dict[str, Any]
    project_config: Dict[str, Any]

@dataclass
class GeneratedCode:
    """Generated code result."""
    file_path: str
    content: str
    imports: List[str]
    explanation: str
    dependencies: List[str]

class AICoder:
    """AI-powered code generator that creates custom code based on requirements."""
    
    def __init__(self, provider: str = "mistral"):
        """Initialize the AI coder.
        
        Args:
            provider: AI provider to use for code generation
        """
        self.provider = provider
        self.client = None
        self._initialize_client()
        
        logger.info(f"AI Coder initialized with provider: {provider}")
    
    def _initialize_client(self):
        """Initialize the AI client."""
        if self.provider == "mistral":
            if not HAS_MISTRAL:
                raise ValueError("Mistral AI not available")
            
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                logger.warning("MISTRAL_API_KEY not set")
                return
            
            self.client = ChatMistralAI(
                api_key=api_key,
                model="mistral-large-latest",
                temperature=0.2,  # Lower temperature for more consistent code
                max_tokens=4096
            )
    
    async def generate_file_content(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate custom code content based on requirements.
        
        Args:
            request: Code generation request with all context
            
        Returns:
            Generated code with metadata
        """
        if not self.client:
            raise ValueError("AI client not initialized")
        
        # Create specialized prompt based on file purpose
        prompt = self._create_code_generation_prompt(request)
        
        try:
            # Generate code using AI
            response = await self._call_ai_for_code(prompt)
            
            # Parse and structure the response
            generated_code = self._parse_code_response(response, request)
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            # Return fallback code
            return self._create_fallback_code(request)
    
    def _create_code_generation_prompt(self, request: CodeGenerationRequest) -> str:
        """Create a specialized prompt for code generation."""
        
        prompt_template = Template("""
You are an expert Python developer creating custom AI/ML applications. Generate COMPLETE, WORKING code based on the specific user requirements.

USER REQUIREMENTS: "{{ user_requirements }}"

PROJECT CONTEXT:
- Type: {{ project_type }}
- File: {{ file_path }}
- Purpose: {{ file_purpose }}
- Configuration: {{ project_config }}

TEMPLATE PATTERNS (for reference only):
{{ template_patterns }}

INSTRUCTIONS:
1. Create CUSTOM code tailored to the user's specific requirements
2. Do NOT copy template code - generate new implementation
3. Focus on the user's actual use case and requirements
4. Include proper error handling and logging
5. Add comprehensive docstrings
6. Use modern Python practices

Generate the complete file content with:
- All necessary imports
- Custom classes/functions for the user's requirements  
- Proper configuration handling
- Error handling
- Documentation

Respond with ONLY the Python code, no explanations or markdown:
""")
        
        return prompt_template.render(
            user_requirements=request.user_requirements,
            project_type=request.project_type,
            file_path=request.file_path,
            file_purpose=request.file_purpose,
            project_config=json.dumps(request.project_config, indent=2),
            template_patterns=json.dumps(request.template_patterns, indent=2)
        )
    
    async def _call_ai_for_code(self, prompt: str) -> str:
        """Call AI provider for code generation."""
        messages = [
            SystemMessage(content="You are an expert Python developer. Generate complete, working code based on requirements. Respond with ONLY Python code, no markdown or explanations."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.client.ainvoke(messages)
        return response.content
    
    def _parse_code_response(self, response: str, request: CodeGenerationRequest) -> GeneratedCode:
        """Parse the AI response into structured code."""
        # Clean the response
        code_content = response.strip()
        
        # Remove any markdown if present
        if code_content.startswith("```"):
            code_content = code_content[9:]
        elif code_content.startswith("```"):
            code_content = code_content[3:]

        if code_content.endswith("```"):
            code_content = code_content[:-3]
        
        code_content = code_content.strip()
        
        # Extract imports
        imports = self._extract_imports_from_code(code_content)
        
        # Extract dependencies
        dependencies = self._extract_dependencies_from_imports(imports)
        
        return GeneratedCode(
            file_path=request.file_path,
            content=code_content,
            imports=imports,
            explanation=f"Custom implementation for {request.file_purpose} based on user requirements",
            dependencies=dependencies
        )
    
    def _extract_imports_from_code(self, code: str) -> List[str]:
        """Extract import statements from generated code."""
        imports = []
        
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def _extract_dependencies_from_imports(self, imports: List[str]) -> List[str]:
        """Extract package dependencies from imports."""
        dependencies = set()
        
        for import_stmt in imports:
            # Map common imports to package names
            if 'langchain' in import_stmt:
                dependencies.add('langchain')
            elif 'streamlit' in import_stmt:
                dependencies.add('streamlit')
            elif 'fastapi' in import_stmt:
                dependencies.add('fastapi')
            elif 'pydantic' in import_stmt:
                dependencies.add('pydantic')
            elif 'openai' in import_stmt:
                dependencies.add('openai')
            elif 'anthropic' in import_stmt:
                dependencies.add('anthropic')
            # Add more mappings as needed
        
        return list(dependencies)
    
    def _create_fallback_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Create fallback code when AI generation fails."""
        
        if "config" in request.file_path.lower():
            fallback_content = self._create_config_fallback(request)
        elif "main" in request.file_path.lower() or "app" in request.file_path.lower():
            fallback_content = self._create_app_fallback(request)
        else:
            fallback_content = self._create_generic_fallback(request)
        
        return GeneratedCode(
            file_path=request.file_path,
            content=fallback_content,
            imports=["import logging", "from typing import Dict, Any"],
            explanation="Fallback implementation when AI generation failed",
            dependencies=["pydantic"]
        )
    
    def _create_config_fallback(self, request: CodeGenerationRequest) -> str:
        """Create fallback configuration code."""
        return f'''"""Configuration for {request.project_config.get('project_name', 'AI Project')}."""

import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings."""
    
    # Project settings
    PROJECT_NAME: str = "{request.project_config.get('project_name', 'ai-project')}"
    
    # LLM settings
    LLM_PROVIDER: str = "{request.project_config.get('llm_provider', 'mistral')}"
    
    # Add more configuration based on requirements:
    # {request.user_requirements}
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
'''
    
    def _create_app_fallback(self, request: CodeGenerationRequest) -> str:
        """Create fallback application code."""
        return f'''"""Main application for {request.project_config.get('project_name', 'AI Project')}."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = {json.dumps(request.project_config, indent=8)}
        logger.info("Application initialized")
    
    def run(self):
        """Run the application."""
        logger.info("Starting application...")
        # Implementation based on: {request.user_requirements}
        pass

def main():
    """Main entry point."""
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
'''
    
    def _create_generic_fallback(self, request: CodeGenerationRequest) -> str:
        """Create generic fallback code."""
        return f'''"""Custom implementation for {request.project_config.get('project_name', 'AI Project')}."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CustomImplementation:
    """Custom implementation based on user requirements."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with configuration."""
        self.config = config or {{}}
        logger.info("Custom implementation initialized")
    
    def process(self, input_data: Any) -> Any:
        """Process data according to requirements."""
        # Implementation for: {request.user_requirements}
        logger.info("Processing data...")
        return input_data

# Create instance
implementation = CustomImplementation()
'''

    async def generate_multiple_files(self, requests: List[CodeGenerationRequest]) -> List[GeneratedCode]:
        """Generate multiple files in sequence.
        
        Args:
            requests: List of code generation requests
            
        Returns:
            List of generated code results
        """
        results = []
        
        for request in requests:
            try:
                result = await self.generate_file_content(request)
                results.append(result)
                logger.info(f"Generated code for {request.file_path}")
            except Exception as e:
                logger.error(f"Failed to generate {request.file_path}: {e}")
                # Add fallback
                fallback = self._create_fallback_code(request)
                results.append(fallback)
        
        return results
