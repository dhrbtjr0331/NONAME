# Prompts Directory

This directory contains all AI agent prompts organized by agent type for better maintainability and version control.

## Structure

```
prompts/
├── __init__.py           # Package initialization and common imports
├── base.py               # Shared utilities and common prompt components
├── rfq_assistant.py      # All RFQ Assistant prompts
├── supplier_agent.py     # (Future) Supplier Agent prompts
├── quote_analyzer.py     # (Future) Quote Analyzer prompts
└── README.md            # This file
```

## Benefits of This Structure

### 🧹 **Clean Code Separation**
- Business logic stays in agent files
- Prompts are centralized and easy to find
- No more long prompt strings cluttering code

### 📝 **Easy Maintenance**  
- Update prompts without touching agent logic
- Version control prompt changes independently
- A/B test different prompt versions

### 🔄 **Reusability**
- Share common prompt components across agents
- Standardize prompt formatting and instructions
- Base utilities for consistent prompt generation

### 🎯 **Agent-Specific Organization**
- Each agent has its own prompt file
- Related prompts grouped together
- Clear naming conventions

## Usage Examples

### Basic Import
```python
from app.prompts.rfq_assistant import SYSTEM_PROMPT, get_data_extraction_prompt
```

### Using Base Utilities
```python
from app.prompts.base import format_data_for_prompt, format_json_instruction

# Format data for prompt inclusion
data_str = format_data_for_prompt(rfq_data, "Current RFQ Data")

# Generate consistent JSON instructions
json_instr = format_json_instruction("Extract the following fields...")
```

### Package-Level Imports
```python
from app.prompts import (
    RFQ_SYSTEM_PROMPT,
    get_rfq_extraction_prompt,
    format_conversation_context
)
```

## Prompt Categories

### System Prompts
Define agent personality, role, and core instructions
- `SYSTEM_PROMPT` - Main agent personality

### Data Extraction Prompts  
Extract structured information from user messages
- `get_data_extraction_prompt()` - Extract domain-specific data

### Context Analysis Prompts
Analyze conversation context and user signals
- `get_context_analysis_prompt()` - Understand user intent/urgency

### Question Generation Prompts
Determine next questions to ask users
- `get_next_question_prompt()` - Generate intelligent follow-ups

### Analysis & Summary Prompts
Generate insights and summaries
- `get_next_steps_prompt()` - Suggest actionable next steps
- `get_summary_generation_prompt()` - Create comprehensive summaries

## Adding New Agents

When creating a new agent type:

1. **Create new prompt file**: `prompts/my_agent.py`
2. **Follow the pattern**:
   ```python
   # System prompt constant
   SYSTEM_PROMPT = "..."
   
   # Prompt generation functions
   def get_my_agent_extraction_prompt(message, data):
       return "..."
   ```
3. **Update `__init__.py`** to include new imports
4. **Use base utilities** for consistent formatting

## Best Practices

### ✅ Do
- Use descriptive function names (`get_data_extraction_prompt`)
- Include docstrings for each prompt function
- Leverage base utilities for consistency
- Keep prompts focused and specific
- Version control prompt changes

### ❌ Don't  
- Hardcode prompts directly in agent files
- Create overly complex prompt functions
- Forget to update `__init__.py` imports
- Mix business logic with prompt generation

## Versioning

Each prompt file includes version tracking:
```python
PROMPT_VERSION = "1.0.0"
LAST_UPDATED = "2024-07-19"
```

For major prompt changes:
1. Update version number
2. Consider backward compatibility
3. Test with existing agent implementations
4. Document changes in git commits

## Future Enhancements

- **A/B Testing**: Support multiple prompt versions
- **Dynamic Prompts**: Generate prompts based on context
- **Prompt Analytics**: Track prompt performance
- **Multi-language**: Support for different languages
- **Prompt Validation**: Automated prompt testing