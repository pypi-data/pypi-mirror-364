"""Project assembler that coordinates the entire project generation process."""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

from ..template_analyzer import TemplateReader, PatternExtractor
from .structure_planner import StructurePlanner

from ..code_generator import AICoder, FileGenerator
from ..code_generator.ai_coder import CodeGenerationRequest


logger = logging.getLogger(__name__)

class ProjectAssembler:
    """Assembles complete AI projects by coordinating all generation components."""
    
    def __init__(self, templates_dir: Path):
        """Initialize the project assembler.
        
        Args:
            templates_dir: Path to the templates directory
        """
        self.templates_dir = templates_dir
        self.template_reader = TemplateReader(templates_dir)
        self.pattern_extractor = PatternExtractor()
        self.structure_planner = StructurePlanner()
        self.ai_coder = AICoder()
        
        logger.info("Project assembler initialized")
    
    async def generate_complete_project(
        self,
        user_requirements: str,
        project_config: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Generate a complete project based on user requirements.
        
        Args:
            user_requirements: User's natural language requirements
            project_config: Project configuration from AI planner
            output_dir: Directory where project will be created
            
        Returns:
            Generation result with success status and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting project generation: {project_config.get('project_name')}")
            
            # Step 1: Analyze reference template
            template_analysis = await self._analyze_reference_template(project_config)
            
            # Step 2: Plan project structure
            project_plan = self._plan_project_structure(
                user_requirements, 
                project_config,
                template_analysis
            )
            
            # Step 3: Generate all files
            generation_results = await self._generate_all_files(
                user_requirements,
                project_config, 
                project_plan,
                template_analysis,
                output_dir
            )
            
            # Step 4: Create project structure and files
            assembly_result = await self._assemble_project(
                generation_results,
                project_plan,
                project_config,
                output_dir
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = {
                "success": True,
                "project_name": project_config.get('project_name'),
                "output_dir": str(output_dir),
                "generation_time": generation_time,
                "files_created": assembly_result.get("files_created", []),
                "template_used": project_config.get('project_type'),
                "ai_generated": True,
                "custom_requirements": user_requirements,
                "stats": {
                    "total_files": len(assembly_result.get("files_created", [])),
                    "custom_files": len(generation_results.get("custom_files", [])),
                    "config_files": len(generation_results.get("config_files", [])),
                    "test_files": len(generation_results.get("test_files", []))
                }
            }
            
            logger.info(f"Project generated successfully in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Project generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_name": project_config.get('project_name'),
                "output_dir": str(output_dir)
            }
    
    async def _analyze_reference_template(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the reference template for patterns and structure."""
        project_type = project_config.get('project_type', 'core-langchain')
        template_name = project_type.replace('-', '_')  # Convert to template directory name
        
        try:
            # Get template information
            template_info = self.template_reader.get_template_info(template_name)
            
            # Extract patterns
            patterns = self.pattern_extractor.extract_architectural_patterns(template_info)
            
            analysis = {
                "template_info": template_info,
                "patterns": patterns,
                "available": True
            }
            
            logger.info(f"Analyzed template: {template_name}")
            return analysis
            
        except Exception as e:
            logger.warning(f"Could not analyze template {template_name}: {e}")
            return {
                "template_info": {},
                "patterns": {},
                "available": False
            }
    
    def _plan_project_structure(
        self,
        user_requirements: str,
        project_config: Dict[str, Any], 
        template_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan the complete project structure."""
        
        template_patterns = template_analysis.get("patterns", {})
        
        project_plan = self.structure_planner.plan_project_structure(
            user_requirements,
            project_config,
            template_patterns
        )
        
        logger.info("Project structure planned")
        return project_plan
    
    async def _generate_all_files(
        self,
        user_requirements: str,
        project_config: Dict[str, Any],
        project_plan: Dict[str, Any],
        template_analysis: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Generate all project files using AI."""
        
        # Prepare code generation requests
        custom_files = project_plan.get("custom_files", [])
        test_files = project_plan.get("test_files", [])
        
        # Get ordered list for generation
        ordered_files = self.structure_planner.get_file_generation_order(custom_files)
        
        # Generate custom files
        custom_results = []
        for file_spec in ordered_files:
            request = CodeGenerationRequest(
                user_requirements=user_requirements,
                project_type=project_config.get('project_type', 'core-langchain'),
                file_path=file_spec["path"],
                file_purpose=file_spec["purpose"],
                template_patterns=template_analysis.get("patterns", {}),
                project_config=project_config
            )
            
            try:
                generated_code = await self.ai_coder.generate_file_content(request)
                custom_results.append(generated_code)
                logger.info(f"Generated: {file_spec['path']}")
            except Exception as e:
                logger.error(f"Failed to generate {file_spec['path']}: {e}")
                # Continue with other files
        
        # Generate test files (simpler generation)
        test_results = []
        for test_spec in test_files:
            test_request = CodeGenerationRequest(
                user_requirements=f"Write tests for {test_spec.get('test_target', 'the module')}",
                project_type=project_config.get('project_type'),
                file_path=test_spec["path"],
                file_purpose=test_spec["purpose"],
                template_patterns={},
                project_config=project_config
            )
            
            try:
                generated_test = await self.ai_coder.generate_file_content(test_request)
                test_results.append(generated_test)
                logger.info(f"Generated test: {test_spec['path']}")
            except Exception as e:
                logger.error(f"Failed to generate test {test_spec['path']}: {e}")
        
        return {
            "custom_files": custom_results,
            "test_files": test_results,
            "config_files": project_plan.get("config_files", [])
        }
    
    async def _assemble_project(
        self,
        generation_results: Dict[str, Any],
        project_plan: Dict[str, Any],
        project_config: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Assemble the final project by creating all files and directories."""
        
        file_generator = FileGenerator(output_dir)
        created_files = []
        
        try:
            # Create project structure
            structure = project_plan.get("structure", {})
            file_generator.create_project_structure(structure)
            
            # Write custom generated files
            for generated_code in generation_results.get("custom_files", []):
                success = file_generator.write_generated_file(generated_code)
                if success:
                    created_files.append(generated_code.file_path)
            
            # Write test files
            for generated_test in generation_results.get("test_files", []):
                success = file_generator.write_generated_file(generated_test)
                if success:
                    created_files.append(generated_test.file_path)
            
            # Create configuration files
            enhanced_config = project_config.copy()
            enhanced_config["user_requirements"] = enhanced_config.get("user_requirements", "AI-generated project")
            
            file_generator.create_configuration_files(enhanced_config)
            
            # Create development container
            file_generator.create_devcontainer(enhanced_config)
            
            # Create __init__.py files
            init_dirs = ["src", "tests"]
            if project_config.get('project_type') == 'multi-agent':
                init_dirs.extend(["src/agents", "src/tools"])
            elif project_config.get('project_type') == 'multimodal-chatbot':
                init_dirs.extend(["src/processors", "src/chatbot"])
            
            file_generator.create_empty_init_files(init_dirs)
            
            # Get all created files
            all_created_files = file_generator.get_created_files()
            
            logger.info(f"Project assembled with {len(all_created_files)} files")
            
            return {
                "success": True,
                "files_created": all_created_files,
                "structure_created": True,
                "config_created": True
            }
            
        except Exception as e:
            logger.error(f"Project assembly failed: {e}")
            # Cleanup on failure
            file_generator.cleanup_on_failure()
            raise
    
    def get_supported_project_types(self) -> List[str]:
        """Get list of supported project types based on available templates."""
        return self.template_reader.get_all_templates()
    
    async def validate_requirements(self, user_requirements: str) -> Dict[str, Any]:
        """Validate user requirements and suggest improvements."""
        
        validation_result = {
            "valid": True,
            "suggestions": [],
            "estimated_complexity": "medium",
            "estimated_files": 0
        }
        
        # Basic validation
        if len(user_requirements.strip()) < 10:
            validation_result["valid"] = False
            validation_result["suggestions"].append(
                "Please provide more detailed requirements (at least 10 characters)"
            )
        
        # Estimate complexity based on keywords
        complexity_keywords = {
            "simple": ["simple", "basic", "minimal"],
            "medium": ["chatbot", "api", "web", "database"],
            "complex": ["multi-agent", "multimodal", "distributed", "scalable"]
        }
        
        req_lower = user_requirements.lower()
        for complexity, keywords in complexity_keywords.items():
            if any(keyword in req_lower for keyword in keywords):
                validation_result["estimated_complexity"] = complexity
                break
        
        # Estimate file count
        file_estimates = {
            "simple": 5,
            "medium": 10,
            "complex": 20
        }
        validation_result["estimated_files"] = file_estimates.get(
            validation_result["estimated_complexity"], 10
        )
        
        return validation_result
