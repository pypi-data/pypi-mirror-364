"""Template reader for analyzing existing templates."""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class TemplateReader:
    """Reads and analyzes template structures and content."""
    
    def __init__(self, templates_dir: Path):
        """Initialize the template reader.
        
        Args:
            templates_dir: Path to the templates directory
        """
        self.templates_dir = templates_dir
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a template.
        
        Args:
            template_name: Name of the template to analyze
            
        Returns:
            Dictionary containing template structure and metadata
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template {template_name} not found")
        
        return {
            "name": template_name,
            "path": str(template_path),
            "structure": self._analyze_structure(template_path),
            "config": self._read_copier_config(template_path),
            "files": self._analyze_files(template_path),
            "patterns": self._extract_patterns(template_path)
        }
    
    def _analyze_structure(self, template_path: Path) -> Dict[str, Any]:
        """Analyze the directory structure of a template."""
        structure = {}
        
        for item in template_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                relative_path = item.relative_to(template_path)
                parts = relative_path.parts
                
                current = structure
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                current[parts[-1]] = {
                    "type": "file",
                    "size": item.stat().st_size,
                    "is_template": item.suffix == ".jinja"
                }
        
        return structure
    
    def _read_copier_config(self, template_path: Path) -> Dict[str, Any]:
        """Read the copier.yml configuration."""
        config_path = template_path / "copier.yml"
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error reading copier config: {e}")
            return {}
    
    def _analyze_files(self, template_path: Path) -> List[Dict[str, Any]]:
        """Analyze individual files in the template."""
        files = []
        
        for file_path in template_path.rglob("*.py.jinja"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                files.append({
                    "path": str(file_path.relative_to(template_path)),
                    "type": "python",
                    "content_preview": content[:500],
                    "imports": self._extract_imports(content),
                    "classes": self._extract_classes(content),
                    "functions": self._extract_functions(content),
                    "jinja_variables": self._extract_jinja_variables(content)
                })
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")
        
        return files
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code."""
        import re
        imports = []
        
        # Find import statements
        import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s*]+$'
        for line in content.split('\n'):
            if re.match(import_pattern, line.strip()):
                imports.append(line.strip())
        
        return imports
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class definitions from Python code."""
        import re
        classes = []
        
        class_pattern = r'^class\s+(\w+).*:$'
        for line in content.split('\n'):
            match = re.match(class_pattern, line.strip())
            if match:
                classes.append(match.group(1))
        
        return classes
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function definitions from Python code."""
        import re
        functions = []
        
        func_pattern = r'^def\s+(\w+)\s*\('
        for line in content.split('\n'):
            match = re.match(func_pattern, line.strip())
            if match:
                functions.append(match.group(1))
        
        return functions
    
    def _extract_jinja_variables(self, content: str) -> List[str]:
        """Extract Jinja2 variables from template content."""
        import re
        variables = set()
        
        # Find {{ variable }} patterns
        var_pattern = r'\{\{\s*(\w+)(?:\.\w+)*(?:\s*\|\s*\w+)*\s*\}\}'
        variables.update(re.findall(var_pattern, content))
        
        # Find {% if variable %} patterns
        if_pattern = r'\{\%\s*if\s+(\w+)'
        variables.update(re.findall(if_pattern, content))
        
        # Find {% for item in variable %} patterns
        for_pattern = r'\{\%\s*for\s+\w+\s+in\s+(\w+)'
        variables.update(re.findall(for_pattern, content))
        
        return list(variables)
    
    def _extract_patterns(self, template_path: Path) -> Dict[str, Any]:
        """Extract common patterns from the template."""
        patterns = {
            "file_naming": [],
            "directory_structure": [],
            "configuration_patterns": [],
            "code_patterns": []
        }
        
        # Analyze file naming patterns
        for file_path in template_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(template_path)
                patterns["file_naming"].append(str(relative_path))
        
        # Analyze directory structure patterns
        for dir_path in template_path.rglob("*"):
            if dir_path.is_dir():
                relative_path = dir_path.relative_to(template_path)
                if relative_path.parts:  # Skip root
                    patterns["directory_structure"].append(str(relative_path))
        
        return patterns
    
    def get_all_templates(self) -> List[str]:
        """Get list of all available templates."""
        templates = []
        
        for item in self.templates_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                templates.append(item.name)
        
        return templates
    
    def read_file_content(self, template_name: str, file_path: str) -> str:
        """Read the content of a specific file in a template.
        
        Args:
            template_name: Name of the template
            file_path: Relative path to the file within the template
            
        Returns:
            File content as string
        """
        full_path = self.templates_dir / template_name / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File {file_path} not found in template {template_name}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
