# Use AI to automatically plan and generate your project
ai-bootstrap create --chat

# Specify AI provider (default is OpenAI)
ai-bootstrap create --chat --planner-provider anthropic



# Test the AI planner functionality
ai-bootstrap test-ai-planner --description "I want to build a PDF analysis chatbot"

# Test with different provider
ai-bootstrap test-ai-planner --provider anthropic --description "Create a multi-agent research system"


# Use the traditional interactive wizard
ai-bootstrap create

# Or specify options manually
ai-bootstrap create --type rag --name my-rag-system
