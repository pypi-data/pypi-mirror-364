"""Enhanced AI planner for Phase 4 with code generation integration."""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import os
import re
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_mistralai import ChatMistralAI
    HAS_MISTRAL = True
except ImportError:
    HAS_MISTRAL = False

from pydantic import BaseModel, Field, ValidationError
import yaml
from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class PlannerProvider(Enum):
    """Available AI planner providers."""
    MISTRAL = "mistral"

class PlannerError(Exception):
    """Custom exception for AI planner errors."""
    pass

@dataclass
class ProjectPlan:
    """Represents a generated project plan."""
    project_name: str
    project_type: str
    llm_provider: str
    python_version: str
    type_specific_config: Dict[str, Any]
    reasoning: Dict[str, str]
    explanation: str
    confidence_score: float

@dataclass
class PlannerResult:
    """Result of AI planning operation."""
    success: bool
    plan: Optional[ProjectPlan] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None

class EnhancedProjectPlanModel(BaseModel):
    """Enhanced Pydantic model for AI-generated project plans."""
    project_name: str = Field(..., description="Name of the project")
    project_type: str = Field(..., description="Type of project")
    llm_provider: str = Field(..., description="LLM provider to use")
    python_version: str = Field(default="3.11", description="Python version")
    
    # Enhanced configurations for better AI code generation
    ui_framework: Optional[str] = Field(None, description="UI framework")
    framework: Optional[str] = Field(None, description="Framework choice")
    vector_store: Optional[str] = Field(None, description="Vector store")
    
    # Multi-agent specific
    num_agents: Optional[int] = Field(None, description="Number of agents")
    agents: Optional[List[Dict[str, str]]] = Field(None, description="Agent configurations")
    memory_backend: Optional[str] = Field(None, description="Memory backend")
    
    # Multimodal specific
    modalities: Optional[List[str]] = Field(None, description="Supported modalities")
    image_features: Optional[List[str]] = Field(None, description="Image features")
    audio_features: Optional[List[str]] = Field(None, description="Audio features")
    
    # Core LangChain specific
    app_type: Optional[str] = Field(None, description="Application type")
    chain_types: Optional[List[str]] = Field(None, description="Chain types")
    include_tools: Optional[bool] = Field(None, description="Include tools")
    
    # Enhanced reasoning for code generation
    reasoning: Dict[str, str] = Field(default_factory=dict)
    explanation: str = Field(default="")
    confidence_score: float = Field(default=0.8)
    
    # New fields for better code generation
    key_features: Optional[List[str]] = Field(None, description="Key features to implement")
    technical_requirements: Optional[List[str]] = Field(None, description="Technical requirements")

class AIPlanner:
    """Enhanced AI planner with code generation awareness."""
    
    def __init__(self, provider: str = "mistral"):
        """Initialize the enhanced AI planner."""
        self.provider = PlannerProvider(provider)
        self.client = None
        self._initialize_client()
        self.meta_prompt_template = self._load_enhanced_meta_prompt_template()
        logger.info(f"Enhanced AI Planner initialized with provider: {provider}")
    
    def _initialize_client(self):
        """Initialize the AI client."""
        if self.provider == PlannerProvider.MISTRAL:
            if not HAS_MISTRAL:
                raise PlannerError("LangChain Mistral library not installed")
            
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                logger.warning("MISTRAL_API_KEY not set")
                return
            
            self.client = ChatMistralAI(
                api_key=api_key,
                model="codestral-latest",
                temperature=0.6,
                max_tokens=4096
            )
    
    def _load_enhanced_meta_prompt_template(self) -> Template:
        """Load enhanced meta-prompt for better code generation planning."""
        
        meta_prompt = """You are an expert AI/ML architect specializing in custom code generation. Analyze the user's detailed requirements and create a comprehensive project plan that will guide AI code generation.

USER REQUIREMENTS: "{{ user_description }}"

Available project types:
{% for type_key, blueprint in available_blueprints.items() %}
- {{ type_key }}: {{ blueprint.description }}
{% endfor %}

Your task is to create not just a configuration, but a detailed plan that will help AI generate custom code specifically for the user's needs.

Respond with ONLY this JSON format:
{
  "project_name": "descriptive-kebab-case-name-based-on-requirements",
  "project_type": "most_appropriate_type",
  "llm_provider": "mistral",
  "python_version": "{{ python_version }}",
  "ui_framework": "best_ui_choice",
  "key_features": ["feature1", "feature2", "feature3"],
  "technical_requirements": ["requirement1", "requirement2"],
  "reasoning": {
    "project_type": "Why this type fits the user's specific needs",
    "llm_provider": "Why mistral is suitable",
    "architecture": "How the system will work for this specific use case"
  },
  "explanation": "Detailed explanation of how this architecture will solve the user's specific problem",
  "confidence_score": 0.85
}

For multi-agent, add: "num_agents": N, "agents": [{"name": "specific_agent_name", "role": "specific_role_for_user_case"}], "memory_backend": "appropriate_choice"
For RAG, add: "framework": "langchain", "vector_store": "chroma"
For multimodal, add: "modalities": ["appropriate_modalities"], "image_features": ["relevant_features"]
For core-langchain, add: "app_type": "appropriate_type", "chain_types": ["relevant_chains"], "include_tools": true/false

Focus on the user's SPECIFIC requirements and create a plan for CUSTOM implementation, not generic templates.

JSON only:"""
        
        return Template(meta_prompt)
    
    async def generate_enhanced_project_plan(
        self,
        description: str,
        available_blueprints: Dict[str, Any],
        python_version: str = "3.11"
    ) -> PlannerResult:
        """Generate enhanced project plan for code generation."""
        
        # Try AI first if available
        if self.client:
            try:
                prompt = self.meta_prompt_template.render(
                    user_description=description,
                    available_blueprints=available_blueprints,
                    python_version=python_version
                )
                
                raw_response = await self._call_ai_provider(prompt)
                plan = self._parse_enhanced_ai_response(raw_response)
                
                return PlannerResult(
                    success=True,
                    plan=plan,
                    raw_response=raw_response
                )
                
            except Exception as e:
                logger.warning(f"Enhanced AI planning failed: {e}")
        
        # Enhanced fallback with better analysis
        try:
            fallback_plan = self._create_enhanced_fallback_plan(description)
            return PlannerResult(
                success=True,
                plan=fallback_plan,
                raw_response="ENHANCED_FALLBACK_USED"
            )
        except Exception as e:
            return PlannerResult(
                success=False,
                error=f"Enhanced planning failed: {str(e)}"
            )
    
    def _create_enhanced_fallback_plan(self, description: str) -> ProjectPlan:
        """Create enhanced fallback plan with better requirement analysis."""
        description_lower = description.lower()
        
        # Enhanced keyword analysis
        if any(word in description_lower for word in ['multi-agent', 'multiple agents', 'agent system', 'agents', 'collaborate']):
            project_type = "multi-agent"
            
            # Extract specific agent roles from description
            agents = []
            if 'travel' in description_lower:
                agents = [
                    {"name": "travel_researcher", "role": "Research destinations and activities"},
                    {"name": "itinerary_planner", "role": "Create detailed travel itineraries"},
                    {"name": "budget_manager", "role": "Manage travel budgets and costs"}
                ]
            else:
                agents = [
                    {"name": "coordinator", "role": "Task coordination and management"},
                    {"name": "specialist", "role": "Domain-specific expertise"},
                    {"name": "executor", "role": "Task execution and results"}
                ]
            
            config = {
                "num_agents": len(agents),
                "agents": agents,
                "memory_backend": "in_memory",
                "ui_framework": "streamlit",
                "key_features": ["agent_coordination", "task_distribution", "result_aggregation"],
                "technical_requirements": ["inter_agent_communication", "state_management"]
            }
            explanation = f"Multi-agent system designed specifically for your use case: {description[:100]}..."
            
        elif any(word in description_lower for word in ['document', 'pdf', 'rag', 'retrieval', 'search', 'knowledge', 'analyze']):
            project_type = "rag"
            config = {
                "framework": "langchain",
                "vector_store": "chroma",
                "ui_framework": "streamlit",
                "key_features": ["document_processing", "semantic_search", "context_retrieval"],
                "technical_requirements": ["pdf_parsing", "vector_embeddings", "similarity_search"]
            }
            explanation = f"RAG system tailored for document analysis: {description[:100]}..."
            
        elif any(word in description_lower for word in ['image', 'audio', 'multimodal', 'vision', 'speech', 'media']):
            project_type = "multimodal-chatbot"
            
            modalities = []
            if any(word in description_lower for word in ['image', 'photo', 'picture', 'visual']):
                modalities.append("image")
            if any(word in description_lower for word in ['audio', 'speech', 'voice', 'sound']):
                modalities.append("audio")
            if not modalities:
                modalities = ["image"]
                
            config = {
                "modalities": modalities,
                "image_features": ["analysis"] if "image" in modalities else [],
                "audio_features": ["stt"] if "audio" in modalities else [],
                "ui_framework": "chainlit",
                "key_features": ["multimodal_processing", "media_analysis", "conversational_interface"],
                "technical_requirements": ["media_processing", "format_conversion"]
            }
            explanation = f"Multimodal chatbot for your specific media processing needs: {description[:100]}..."
            
        else:
            project_type = "core-langchain"
            config = {
                "app_type": "qa_system",
                "chain_types": ["llm"],
                "include_tools": True,
                "ui_framework": "streamlit",
                "key_features": ["llm_integration", "custom_chains", "tool_usage"],
                "technical_requirements": ["prompt_management", "response_processing"]
            }
            explanation = f"Custom LangChain application for your requirements: {description[:100]}..."
        
        # Generate better project name
        words = re.findall(r'\w+', description_lower)
        # Filter out common words
        important_words = [w for w in words[:5] if w not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'i', 'want', 'to', 'build', 'create', 'make']]
        project_name = '-'.join(important_words[:3]) if important_words else "my-ai-project"
        project_name += f"-{project_type.replace('_', '-')}"
        
        return ProjectPlan(
            project_name=project_name,
            project_type=project_type,
            llm_provider="mistral",
            python_version="3.11",
            type_specific_config=config,
            reasoning={
                "project_type": f"Analyzed your requirements and identified key patterns indicating {project_type} architecture",
                "llm_provider": "Mistral chosen for reliable performance and cost-effectiveness",
                "architecture": f"System designed to specifically address your stated needs"
            },
            explanation=explanation,
            confidence_score=0.75
        )
    
    async def _call_ai_provider(self, prompt: str) -> str:
        """Call AI provider for enhanced planning."""
        messages = [
            SystemMessage(content="You are an expert AI architect. Respond with ONLY valid JSON for custom code generation planning."),
            HumanMessage(content=prompt)
        ]
        response = await self.client.ainvoke(messages)
        return response.content
    
    def _parse_enhanced_ai_response(self, raw_response: str) -> ProjectPlan:
        """Parse enhanced AI response with additional validation."""
        try:
            # Clean response
            cleaned_response = self._clean_json_response(raw_response)
            
            # Parse JSON
            response_data = json.loads(cleaned_response)
            
            # Validate with enhanced model
            validated_plan = EnhancedProjectPlanModel(**response_data)
            
            # Extract type-specific config including new fields
            type_specific_config = {}
            optional_fields = [
                'framework', 'vector_store', 'ui_framework',
                'num_agents', 'agents', 'memory_backend',
                'modalities', 'image_features', 'audio_features',
                'app_type', 'chain_types', 'include_tools',
                'key_features', 'technical_requirements'  # New enhanced fields
            ]
            
            for field in optional_fields:
                value = getattr(validated_plan, field, None)
                if value is not None:
                    type_specific_config[field] = value
            
            plan = ProjectPlan(
                project_name=validated_plan.project_name,
                project_type=validated_plan.project_type,
                llm_provider=validated_plan.llm_provider,
                python_version=validated_plan.python_version,
                type_specific_config=type_specific_config,
                reasoning=validated_plan.reasoning,
                explanation=validated_plan.explanation,
                confidence_score=validated_plan.confidence_score
            )
            
            # Validate project type
            valid_types = ["rag", "multi-agent", "multimodal-chatbot", "core-langchain"]
            if plan.project_type not in valid_types:
                raise PlannerError(f"Invalid project type: {plan.project_type}")
            
            logger.info(f"Enhanced AI plan generated: {plan.project_name} ({plan.project_type})")
            return plan
            
        except Exception as e:
            raise PlannerError(f"Enhanced AI response parsing failed: {e}")
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response for parsing."""
        # Find JSON object boundaries
        start = response.find('{')
        end = response.rfind('}')
        
        if start == -1 or end == -1:
            raise PlannerError("No JSON object found in response")
        
        json_str = response[start:end+1]
        
        # Fix common issues
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json_str

# Legacy compatibility - keep the old function name
async def generate_plan_from_description(
    description: str,
    provider: str = "mistral",
    blueprints: Optional[Dict[str, Any]] = None
) -> PlannerResult:
    """Legacy compatibility function."""
    if blueprints is None:
        blueprints = {
            "rag": {"name": "RAG System", "description": "Document analysis system"},
            "multi-agent": {"name": "Multi-Agent System", "description": "Collaborative agent system"},
            "multimodal-chatbot": {"name": "Multimodal Chatbot", "description": "Media-aware chatbot"},
            "core-langchain": {"name": "Core LangChain", "description": "Custom LangChain app"}
        }
    
    planner = AIPlanner(provider=provider)
    return await planner.generate_enhanced_project_plan(description, blueprints)
