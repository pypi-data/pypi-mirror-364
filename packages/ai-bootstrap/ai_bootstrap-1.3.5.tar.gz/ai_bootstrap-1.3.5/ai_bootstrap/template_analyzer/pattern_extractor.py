"""Pattern extraction from templates for AI code generation."""

import re
from typing import Dict, List, Any, Set
from pathlib import Path
import ast
import logging

logger = logging.getLogger(__name__)

class PatternExtractor:
    """Extracts reusable patterns from template analysis."""
    
    def __init__(self):
        """Initialize the pattern extractor."""
        pass
    
    def extract_architectural_patterns(self, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract architectural patterns from template analysis.
        
        Args:
            template_info: Template information from TemplateReader
            
        Returns:
            Dictionary of architectural patterns
        """
        patterns = {
            "project_structure": self._analyze_project_structure(template_info),
            "dependency_patterns": self._analyze_dependencies(template_info),
            "configuration_patterns": self._analyze_configuration(template_info),
            "code_organization": self._analyze_code_organization(template_info),
            "integration_patterns": self._analyze_integrations(template_info)
        }
        
        return patterns
    
    def _analyze_project_structure(self, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project structure patterns."""
        structure = template_info.get("structure", {})
        
        return {
            "has_src_dir": "src" in structure,
            "has_tests_dir": "tests" in structure,
            "has_notebooks": "notebooks" in structure,
            "has_data_dir": "data" in structure,
            "has_devcontainer": ".devcontainer" in structure,
            "config_files": self._find_config_files(structure),
            "main_modules": self._find_main_modules(structure)
        }
    
    def _analyze_dependencies(self, template_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze dependency patterns from files."""
        dependencies = {
            "core_frameworks": [],
            "llm_providers": [],
            "ui_frameworks": [],
            "data_processing": [],
            "testing": [],
            "development": []
        }
        
        for file_info in template_info.get("files", []):
            imports = file_info.get("imports", [])
            
            for import_stmt in imports:
                self._categorize_import(import_stmt, dependencies)
        
        return dependencies
    
    def _analyze_configuration(self, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze configuration patterns."""
        config = template_info.get("config", {})
        
        patterns = {
            "uses_pydantic": False,
            "uses_environment_vars": False,
            "has_multiple_providers": False,
            "configurable_components": []
        }
        
        # Analyze copier configuration
        for key, value in config.items():
            if isinstance(value, dict):
                if value.get("type") == "str" and "choices" in value:
                    patterns["configurable_components"].append({
                        "name": key,
                        "type": "choice",
                        "options": value["choices"]
                    })
        
        return patterns
    
    def _analyze_code_organization(self, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code organization patterns."""
        organization = {
            "separation_of_concerns": [],
            "abstraction_layers": [],
            "design_patterns": [],
            "naming_conventions": []
        }
        
        for file_info in template_info.get("files", []):
            path = file_info["path"]
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            
            # Analyze separation of concerns
            if "config" in path.lower():
                organization["separation_of_concerns"].append("configuration")
            elif "agent" in path.lower():
                organization["separation_of_concerns"].append("agent_logic")
            elif "tool" in path.lower():
                organization["separation_of_concerns"].append("tools")
            elif "chain" in path.lower():
                organization["separation_of_concerns"].append("chains")
            
            # Analyze design patterns
            for class_name in classes:
                if class_name.endswith("Manager"):
                    organization["design_patterns"].append("manager_pattern")
                elif class_name.endswith("Builder"):
                    organization["design_patterns"].append("builder_pattern")
                elif class_name.endswith("Factory"):
                    organization["design_patterns"].append("factory_pattern")
        
        return organization
    
    def _analyze_integrations(self, template_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze integration patterns."""
        integrations = {
            "llm_integrations": [],
            "vector_store_integrations": [],
            "ui_integrations": [],
            "tool_integrations": [],
            "memory_integrations": []
        }
        
        for file_info in template_info.get("files", []):
            imports = file_info.get("imports", [])
            
            for import_stmt in imports:
                if "langchain_openai" in import_stmt:
                    integrations["llm_integrations"].append("openai")
                elif "langchain_anthropic" in import_stmt:
                    integrations["llm_integrations"].append("anthropic")
                elif "streamlit" in import_stmt:
                    integrations["ui_integrations"].append("streamlit")
                elif "chainlit" in import_stmt:
                    integrations["ui_integrations"].append("chainlit")
                elif "chroma" in import_stmt:
                    integrations["vector_store_integrations"].append("chroma")
                elif "faiss" in import_stmt:
                    integrations["vector_store_integrations"].append("faiss")
        
        return integrations
    
    def _find_config_files(self, structure: Dict[str, Any]) -> List[str]:
        """Find configuration files in structure."""
        config_files = []
        
        def search_structure(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}/{key}" if path else key
                    
                    if isinstance(value, dict) and value.get("type") == "file":
                        if any(config_name in key.lower() for config_name in ["config", "settings", ".env"]):
                            config_files.append(current_path)
                    else:
                        search_structure(value, current_path)
        
        search_structure(structure)
        return config_files
    
    def _find_main_modules(self, structure: Dict[str, Any]) -> List[str]:
        """Find main module files."""
        main_modules = []
        
        def search_structure(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}/{key}" if path else key
                    
                    if isinstance(value, dict) and value.get("type") == "file":
                        if key in ["main.py", "app.py", "__init__.py"]:
                            main_modules.append(current_path)
                    else:
                        search_structure(value, current_path)
        
        search_structure(structure)
        return main_modules
    
    def _categorize_import(self, import_stmt: str, dependencies: Dict[str, List[str]]):
        """Categorize an import statement."""
        import_lower = import_stmt.lower()
        
        # Core frameworks
        if any(fw in import_lower for fw in ["langchain", "llamaindex"]):
            dependencies["core_frameworks"].append(import_stmt)
        
        # LLM providers
        elif any(provider in import_lower for provider in ["openai", "anthropic", "ollama"]):
            dependencies["llm_providers"].append(import_stmt)
        
        # UI frameworks
        elif any(ui in import_lower for ui in ["streamlit", "chainlit", "flask", "fastapi"]):
            dependencies["ui_frameworks"].append(import_stmt)
        
        # Data processing
        elif any(dp in import_lower for dp in ["pandas", "numpy", "chroma", "faiss"]):
            dependencies["data_processing"].append(import_stmt)
        
        # Testing
        elif any(test in import_lower for test in ["pytest", "unittest"]):
            dependencies["testing"].append(import_stmt)
        
        # Development
        elif any(dev in import_lower for dev in ["pydantic", "rich", "typer"]):
            dependencies["development"].append(import_stmt)
    
    def generate_pattern_summary(self, patterns: Dict[str, Any]) -> str:
        """Generate a human-readable summary of patterns.
        
        Args:
            patterns: Extracted patterns dictionary
            
        Returns:
            Formatted summary string
        """
        summary = []
        
        # Project structure summary
        structure = patterns.get("project_structure", {})
        summary.append("Project Structure:")
        summary.append(f"- Uses src/ directory: {structure.get('has_src_dir', False)}")
        summary.append(f"- Has tests: {structure.get('has_tests_dir', False)}")
        summary.append(f"- Includes notebooks: {structure.get('has_notebooks', False)}")
        summary.append(f"- Has development container: {structure.get('has_devcontainer', False)}")
        
        # Dependencies summary
        deps = patterns.get("dependency_patterns", {})
        summary.append("\nKey Dependencies:")
        for category, items in deps.items():
            if items:
                summary.append(f"- {category.replace('_', ' ').title()}: {len(items)} imports")
        
        # Code organization summary
        org = patterns.get("code_organization", {})
        summary.append("\nCode Organization:")
        concerns = org.get("separation_of_concerns", [])
        if concerns:
            summary.append(f"- Separates: {', '.join(set(concerns))}")
        
        patterns_found = org.get("design_patterns", [])
        if patterns_found:
            summary.append(f"- Design patterns: {', '.join(set(patterns_found))}")
        
        return "\n".join(summary)
