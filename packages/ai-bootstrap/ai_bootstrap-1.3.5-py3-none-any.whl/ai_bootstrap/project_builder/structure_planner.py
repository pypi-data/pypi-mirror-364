"""Project structure planning based on requirements and template analysis."""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class StructurePlanner:
    """Plans the complete project structure based on user requirements."""
    
    def __init__(self):
        """Initialize the structure planner."""
        self.file_specifications = []
    
    def plan_project_structure(
        self, 
        user_requirements: str,
        project_config: Dict[str, Any],
        template_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan the complete project structure.
        
        Args:
            user_requirements: User's natural language requirements
            project_config: Project configuration from AI planner
            template_patterns: Patterns extracted from templates
            
        Returns:
            Complete project plan including structure and files
        """
        try:
            # Create base structure
            structure = self._create_base_structure(project_config)
            
            # Plan custom files based on requirements
            custom_files = self._plan_custom_files(
                user_requirements, 
                project_config, 
                template_patterns
            )
            
            # Plan tests
            test_files = self._plan_test_files(custom_files, project_config)
            
            # Combine everything
            complete_plan = {
                "structure": structure,
                "custom_files": custom_files,
                "test_files": test_files,
                "config_files": self._plan_config_files(project_config),
                "dependencies": self._analyze_dependencies(custom_files)
            }
            
            logger.info("Project structure planned successfully")
            return complete_plan
            
        except Exception as e:
            logger.error(f"Failed to plan project structure: {e}")
            raise
    
    def _create_base_structure(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create the base directory structure."""
        project_type = project_config.get('project_type', 'core-langchain')
        
        base_structure = {
            "src": {
                "type": "directory",
                "description": "Main source code directory"
            },
            "tests": {
                "type": "directory", 
                "description": "Test files"
            },
            "data": {
                "type": "directory",
                "description": "Data storage"
            }
        }
        
        # Add project-type specific directories
        if project_type == 'rag':
            base_structure.update({
                "documents": {
                    "type": "directory",
                    "description": "Document storage for RAG"
                },
                "vector_store": {
                    "type": "directory", 
                    "description": "Vector database storage"
                }
            })
        
        elif project_type == 'multi-agent':
            base_structure["src"].update({
                "agents": {
                    "type": "directory",
                    "description": "Agent implementations"
                },
                "tools": {
                    "type": "directory",
                    "description": "Agent tools"
                },
                "memory": {
                    "type": "directory",
                    "description": "Memory management"
                }
            })
        
        elif project_type == 'multimodal-chatbot':
            base_structure["src"].update({
                "processors": {
                    "type": "directory", 
                    "description": "Media processors"
                },
                "chatbot": {
                    "type": "directory",
                    "description": "Chatbot logic"
                }
            })
        
        # Always add common directories
        base_structure.update({
            "notebooks": {
                "type": "directory",
                "description": "Jupyter notebooks"
            },
            ".devcontainer": {
                "type": "directory", 
                "description": "Development container config"
            }
        })
        
        return base_structure
    
    def _plan_custom_files(
        self, 
        user_requirements: str, 
        project_config: Dict[str, Any],
        template_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Plan custom files based on user requirements."""
        
        custom_files = []
        project_type = project_config.get('project_type', 'core-langchain')
        
        # Always needed files
        custom_files.extend([
            {
                "path": "src/config.py",
                "purpose": "Application configuration and settings",
                "priority": "high",
                "dependencies": ["pydantic", "python-dotenv"]
            },
            {
                "path": "src/__init__.py", 
                "purpose": "Package initialization",
                "priority": "high",
                "dependencies": []
            },
            {
                "path": "main.py",
                "purpose": "Main application entry point", 
                "priority": "high",
                "dependencies": []
            }
        ])
        
        # Project type specific files
        if project_type == 'rag':
            custom_files.extend(self._plan_rag_files(user_requirements, project_config))
        elif project_type == 'multi-agent':
            custom_files.extend(self._plan_multi_agent_files(user_requirements, project_config))
        elif project_type == 'multimodal-chatbot':
            custom_files.extend(self._plan_multimodal_files(user_requirements, project_config))
        else:
            custom_files.extend(self._plan_core_langchain_files(user_requirements, project_config))
        
        # UI-specific files
        ui_framework = project_config.get('ui_framework')
        if ui_framework:
            custom_files.extend(self._plan_ui_files(ui_framework, user_requirements, project_config))
        
        return custom_files
    
    def _plan_rag_files(self, user_requirements: str, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan files specific to RAG systems."""
        return [
            {
                "path": "src/document_processor.py",
                "purpose": "Document ingestion and processing for RAG",
                "priority": "high",
                "dependencies": ["langchain", "pypdf"]
            },
            {
                "path": "src/vector_store.py", 
                "purpose": "Vector database management and retrieval",
                "priority": "high",
                "dependencies": ["chromadb", "langchain"]
            },
            {
                "path": "src/retrieval_chain.py",
                "purpose": "RAG chain implementation for question answering", 
                "priority": "high",
                "dependencies": ["langchain"]
            },
            {
                "path": "src/query_engine.py",
                "purpose": "Query processing and response generation",
                "priority": "medium", 
                "dependencies": ["langchain"]
            }
        ]
    
    def _plan_multi_agent_files(self, user_requirements: str, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan files specific to multi-agent systems."""
        files = [
            {
                "path": "src/agent_coordinator.py",
                "purpose": "Coordinates communication between multiple agents",
                "priority": "high",
                "dependencies": ["langgraph", "langchain"]
            },
            {
                "path": "src/state_manager.py",
                "purpose": "Manages shared state between agents",
                "priority": "high", 
                "dependencies": ["langgraph"]
            }
        ]
        
        # Add individual agent files based on configuration
        agents = project_config.get('agents', [])
        for i, agent in enumerate(agents):
            agent_name = agent.get('name', f'agent_{i+1}')
            files.append({
                "path": f"src/agents/{agent_name}.py",
                "purpose": f"Implementation of {agent_name} agent - {agent.get('role', 'general purpose')}",
                "priority": "high",
                "dependencies": ["langchain"]
            })
        
        # Add tools directory
        files.extend([
            {
                "path": "src/tools/search_tool.py",
                "purpose": "Web search capabilities for agents",
                "priority": "medium",
                "dependencies": ["langchain"]
            },
            {
                "path": "src/tools/file_tool.py", 
                "purpose": "File operations for agents",
                "priority": "medium",
                "dependencies": []
            }
        ])
        
        return files
    
    def _plan_multimodal_files(self, user_requirements: str, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan files specific to multimodal chatbots."""
        files = [
            {
                "path": "src/chatbot/engine.py",
                "purpose": "Main chatbot engine handling multimodal inputs",
                "priority": "high",
                "dependencies": ["langchain"]
            },
            {
                "path": "src/chatbot/memory.py",
                "purpose": "Conversation memory management", 
                "priority": "high",
                "dependencies": ["langchain"]
            }
        ]
        
        # Add modality-specific processors
        modalities = project_config.get('modalities', [])
        if 'image' in modalities:
            files.append({
                "path": "src/processors/image_processor.py",
                "purpose": "Image analysis and processing capabilities",
                "priority": "high", 
                "dependencies": ["pillow", "langchain"]
            })
        
        if 'audio' in modalities:
            files.append({
                "path": "src/processors/audio_processor.py",
                "purpose": "Audio processing and speech recognition",
                "priority": "high",
                "dependencies": ["pydub", "langchain"]
            })
        
        return files
    
    def _plan_core_langchain_files(self, user_requirements: str, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan files for core LangChain applications."""
        files = [
            {
                "path": "src/chains.py",
                "purpose": "Custom LangChain chains implementation",
                "priority": "high",
                "dependencies": ["langchain"]
            },
            {
                "path": "src/prompts.py",
                "purpose": "Prompt templates and management",
                "priority": "medium",
                "dependencies": ["langchain"]
            }
        ]
        
        # Add tools if specified
        if project_config.get('include_tools', False):
            files.append({
                "path": "src/tools.py",
                "purpose": "Custom tools for LangChain chains",
                "priority": "medium", 
                "dependencies": ["langchain"]
            })
        
        return files
    
    def _plan_ui_files(self, ui_framework: str, user_requirements: str, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan UI-specific files."""
        if ui_framework == 'streamlit':
            return [{
                "path": "app.py",
                "purpose": "Streamlit web application interface",
                "priority": "high",
                "dependencies": ["streamlit"]
            }]
        
        elif ui_framework == 'fastapi':
            return [
                {
                    "path": "app.py", 
                    "purpose": "FastAPI web service",
                    "priority": "high",
                    "dependencies": ["fastapi", "uvicorn"]
                },
                {
                    "path": "src/api/routes.py",
                    "purpose": "API route definitions",
                    "priority": "medium",
                    "dependencies": ["fastapi"]
                }
            ]
        
        elif ui_framework == 'chainlit':
            return [{
                "path": "app.py",
                "purpose": "Chainlit chat interface",
                "priority": "high", 
                "dependencies": ["chainlit"]
            }]
        
        return []
    
    def _plan_test_files(self, custom_files: List[Dict[str, Any]], project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan test files for the custom files."""
        test_files = []
        
        for file_spec in custom_files:
            file_path = file_spec["path"]
            
            # Skip certain files that don't need tests
            if any(skip in file_path for skip in ["__init__.py", "app.py"]):
                continue
            
            # Convert src/module.py to tests/test_module.py
            if file_path.startswith("src/"):
                test_path = file_path.replace("src/", "tests/test_", 1)
            else:
                test_path = f"tests/test_{Path(file_path).stem}.py"
            
            test_files.append({
                "path": test_path,
                "purpose": f"Tests for {file_path}",
                "priority": "medium",
                "dependencies": ["pytest"],
                "test_target": file_path
            })
        
        # Add main test init file
        test_files.append({
            "path": "tests/__init__.py",
            "purpose": "Test package initialization",
            "priority": "low", 
            "dependencies": []
        })
        
        return test_files
    
    def _plan_config_files(self, project_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan configuration and setup files."""
        return [
            {
                "path": ".env.example",
                "purpose": "Environment variables template",
                "priority": "high",
                "dependencies": []
            },
            {
                "path": ".gitignore", 
                "purpose": "Git ignore patterns",
                "priority": "high",
                "dependencies": []
            },
            {
                "path": "README.md",
                "purpose": "Project documentation",
                "priority": "high",
                "dependencies": []
            },
            {
                "path": "requirements.txt",
                "purpose": "Python dependencies",
                "priority": "high", 
                "dependencies": []
            },
            {
                "path": "pyproject.toml",
                "purpose": "Python project configuration",
                "priority": "medium",
                "dependencies": []
            }
        ]
    
    def _analyze_dependencies(self, custom_files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze dependencies across all files."""
        all_deps = set()
        dep_categories = {
            "core": [],
            "llm": [],
            "ui": [], 
            "data": [],
            "testing": [],
            "development": []
        }
        
        for file_spec in custom_files:
            deps = file_spec.get("dependencies", [])
            all_deps.update(deps)
        
        # Categorize dependencies
        for dep in all_deps:
            if dep in ["langchain", "langgraph"]:
                dep_categories["core"].append(dep)
            elif dep in ["langchain-openai", "langchain-anthropic", "langchain-mistralai"]:
                dep_categories["llm"].append(dep)
            elif dep in ["streamlit", "fastapi", "chainlit"]:
                dep_categories["ui"].append(dep)
            elif dep in ["chromadb", "faiss", "pypdf"]:
                dep_categories["data"].append(dep)
            elif dep in ["pytest"]:
                dep_categories["testing"].append(dep)
            else:
                dep_categories["development"].append(dep)
        
        return dep_categories
    
    def get_file_generation_order(self, custom_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get files ordered by generation priority and dependencies."""
        
        # Sort by priority: high -> medium -> low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        sorted_files = sorted(
            custom_files,
            key=lambda f: (
                priority_order.get(f.get("priority", "medium"), 1),
                f["path"]  # Secondary sort by path for consistency
            )
        )
        
        return sorted_files
