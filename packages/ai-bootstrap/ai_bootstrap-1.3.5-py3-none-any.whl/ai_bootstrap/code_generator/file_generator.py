"""File generation and management for AI-generated projects."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil
import json

from .ai_coder import GeneratedCode

logger = logging.getLogger(__name__)

class FileGenerator:
    """Handles creation and management of generated project files."""
    
    def __init__(self, output_dir: Path):
        """Initialize the file generator.
        
        Args:
            output_dir: Directory where the project will be created
        """
        self.output_dir = output_dir
        self.created_files = []
        
    def create_project_structure(self, structure: Dict[str, Any]) -> bool:
        """Create the basic project directory structure.
        
        Args:
            structure: Dictionary defining the project structure
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self._create_directories(structure, self.output_dir)
            
            logger.info(f"Created project structure at {self.output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project structure: {e}")
            return False
    
    def _create_directories(self, structure: Dict[str, Any], base_path: Path):
        """Recursively create directory structure."""
        for name, content in structure.items():
            if isinstance(content, dict):
                if content.get("type") == "file":
                    # This is a file placeholder, will be created later
                    continue
                else:
                    # This is a directory
                    dir_path = base_path / name
                    dir_path.mkdir(exist_ok=True)
                    self._create_directories(content, dir_path)
    
    def write_generated_file(self, generated_code: GeneratedCode) -> bool:
        """Write a generated code file to disk.
        
        Args:
            generated_code: Generated code object with content and metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.output_dir / generated_code.file_path
            
            # Ensure parent directories exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(generated_code.content)
            
            self.created_files.append(str(file_path))
            logger.info(f"Created file: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {generated_code.file_path}: {e}")
            return False
    
    def create_configuration_files(self, project_config: Dict[str, Any]) -> bool:
        """Create standard configuration files.
        
        Args:
            project_config: Project configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create .env.example
            self._create_env_example(project_config)
            
            # Create .gitignore
            self._create_gitignore()
            
            # Create README.md
            self._create_readme(project_config)
            
            # Create requirements.txt
            self._create_requirements(project_config)
            
            # Create pyproject.toml if needed
            if project_config.get("include_pyproject", True):
                self._create_pyproject_toml(project_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create configuration files: {e}")
            return False
    
    def _create_env_example(self, project_config: Dict[str, Any]):
        """Create .env.example file."""
        env_content = f"""# Environment configuration for {project_config.get('project_name', 'AI Project')}

# LLM Provider Configuration
"""
        
        llm_provider = project_config.get('llm_provider', 'mistral')
        
        if llm_provider == 'mistral':
            env_content += "MISTRAL_API_KEY=your_mistral_api_key_here\n"
        elif llm_provider == 'openai':
            env_content += "OPENAI_API_KEY=your_openai_api_key_here\n"
        elif llm_provider == 'anthropic':
            env_content += "ANTHROPIC_API_KEY=your_anthropic_api_key_here\n"
        
        env_content += f"""
# Application Settings
PROJECT_NAME={project_config.get('project_name', 'ai-project')}
LOG_LEVEL=INFO

# Add your custom environment variables here
"""
        
        with open(self.output_dir / ".env.example", 'w') as f:
            f.write(env_content)
    
    def _create_gitignore(self):
        """Create .gitignore file."""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Jupyter
.ipynb_checkpoints/

# AI/ML specific
models/
data/raw/
data/processed/
*.pkl
*.joblib

# Vector stores
vector_store/
chroma_db/
*.faiss

# Temporary files
tmp/
temp/
"""
        
        with open(self.output_dir / ".gitignore", 'w') as f:
            f.write(gitignore_content)
    
    def _create_readme(self, project_config: Dict[str, Any]):
        """Create README.md file."""
        project_name = project_config.get('project_name', 'AI Project')
        project_type = project_config.get('project_type', 'ai-application')
        llm_provider = project_config.get('llm_provider', 'mistral')
        user_requirements = project_config.get('user_requirements', 'Custom AI application')
        
        readme_content = f"""# {project_name.replace('-', ' ').title()}

{user_requirements}

An AI-powered {project_type.replace('-', ' ')} application built with {llm_provider.title()}.

## 🚀 Features

- Custom AI implementation tailored to your requirements
- Built with modern Python practices
- Configured for {llm_provider.title()} integration
- Includes proper error handling and logging

## 📋 Prerequisites

- Python 3.9+
- {llm_provider.title()} API access

## 🛠️ Installation

1. **Navigate to the project:**
cd {project_name}
2. **Create virtual environment:**
python -m venv venv
source venv/bin/activate # On Windows
3. **Install dependencies:**
pip install -r requirements.txt
4. **Set up environment variables:**
cp .env.example .env

Edit .env with your API keys
## 📚 Usage

python main.py

## ⚙️ Configuration

Edit the `.env` file with your configuration:

{llm_provider.upper()}_API_KEY=your_api_key_here
PROJECT_NAME={project_name}
## 🧪 Development

Run tests:
pytest tests/
## 📄 License

MIT License

---

Built with ❤️ using [AI Bootstrap](https://github.com/your-repo/ai-bootstrap)
"""
        with open(self.output_dir / "README.md", 'w') as f:
            f.write(readme_content)
    
    def _create_requirements(self, project_config: Dict[str, Any]):
        """Create requirements.txt file."""
        requirements = [
            "# Core dependencies",
            "python-dotenv>=1.0.0",
            "pydantic>=2.6.0",
            "rich>=13.7.0",
            "loguru>=0.7.2",
        ]
        
        llm_provider = project_config.get('llm_provider', 'mistral')
        
        # Add LLM provider dependencies
        if llm_provider == 'mistral':
            requirements.extend([
                "",
                "# Mistral AI",
                "langchain-mistralai>=0.1.0",
                "langchain-core>=0.1.0",
            ])
        elif llm_provider == 'openai':
            requirements.extend([
                "",
                "# OpenAI",
                "langchain-openai>=0.0.6",
                "openai>=1.12.0",
            ])
        elif llm_provider == 'anthropic':
            requirements.extend([
                "",
                "# Anthropic",
                "langchain-anthropic>=0.1.0",
                "anthropic>=0.18.0",
            ])
        
        # Add UI framework dependencies
        ui_framework = project_config.get('ui_framework')
        if ui_framework == 'streamlit':
            requirements.extend([
                "",
                "# Streamlit UI",
                "streamlit>=1.31.0",
            ])
        elif ui_framework == 'fastapi':
            requirements.extend([
                "",
                "# FastAPI",
                "fastapi>=0.109.0",
                "uvicorn[standard]>=0.27.0",
            ])
        elif ui_framework == 'chainlit':
            requirements.extend([
                "",
                "# Chainlit",
                "chainlit>=1.0.0",
            ])
        
        # Add project type specific dependencies
        project_type = project_config.get('project_type')
        if project_type == 'rag':
            requirements.extend([
                "",
                "# RAG System",
                "langchain>=0.1.0",
                "chromadb>=0.4.0",
                "pypdf>=4.0.0",
                "sentence-transformers>=2.2.0",
            ])
        elif project_type == 'multi-agent':
            requirements.extend([
                "",
                "# Multi-Agent System",
                "langgraph>=0.0.40",
                "langchain>=0.1.0",
            ])
        elif project_type == 'multimodal-chatbot':
            requirements.extend([
                "",
                "# Multimodal Chatbot",
                "langchain>=0.1.0",
                "pillow>=10.2.0",
                "pydub>=0.25.1",
            ])
        
        requirements.extend([
            "",
            "# Development dependencies",
            "pytest>=8.0.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
        ])
        
        with open(self.output_dir / "requirements.txt", 'w') as f:
            f.write('\n'.join(requirements))
    
    def _create_pyproject_toml(self, project_config: Dict[str, Any]):
        """Create pyproject.toml file."""
        project_name = project_config.get('project_name', 'ai-project')
        
        pyproject_content = f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "AI-powered application generated by AI Bootstrap"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
dependencies = [
    "python-dotenv>=1.0.0",
    "pydantic>=2.6.0",
    "rich>=13.7.0",
]
requires-python = ">=3.9"
readme = "README.md"
license = {{text = "MIT"}}

[project.urls]
Homepage = "https://github.com/yourusername/{project_name}"
Repository = "https://github.com/yourusername/{project_name}"

[tool.black]
line-length = 88
target-version = ['py39']

[tool.ruff]
target-version = "py39"
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
"""
        
        with open(self.output_dir / "pyproject.toml", 'w') as f:
            f.write(pyproject_content)
    
    def create_devcontainer(self, project_config: Dict[str, Any]):
        """Create .devcontainer configuration."""
        devcontainer_dir = self.output_dir / ".devcontainer"
        devcontainer_dir.mkdir(exist_ok=True)
        
        devcontainer_content = f"""{{
    "name": "{project_config.get('project_name', 'AI Project')} Development",
    "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
    
    "customizations": {{
        "vscode": {{
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-python.black-formatter",
                "ms-toolsai.jupyter"
            ],
            "settings": {{
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.formatting.provider": "black",
                "editor.formatOnSave": true
            }}
        }}
    }},
    
    "postCreateCommand": "pip install -r requirements.txt",
    
    "forwardPorts": [8000, 8501],
    
    "remoteEnv": {{
        "PYTHONPATH": "/workspaces/{project_config.get('project_name', 'ai-project')}"
    }}
}}"""
        
        with open(devcontainer_dir / "devcontainer.json", 'w') as f:
            f.write(devcontainer_content)
    
    def create_empty_init_files(self, directories: List[str]):
        """Create empty __init__.py files in specified directories."""
        for directory in directories:
            init_path = self.output_dir / directory / "__init__.py"
            init_path.parent.mkdir(parents=True, exist_ok=True)
            
            init_content = f'"""Initialize {directory} package."""\n'
            
            with open(init_path, 'w') as f:
                f.write(init_content)
    
    def get_created_files(self) -> List[str]:
        """Get list of all created files."""
        return self.created_files.copy()
    
    def cleanup_on_failure(self):
        """Clean up created files if generation fails."""
        try:
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                logger.info(f"Cleaned up failed project at {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")