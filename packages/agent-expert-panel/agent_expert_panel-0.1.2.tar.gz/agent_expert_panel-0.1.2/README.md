[![codecov](https://codecov.io/gh/zbloss/agent-expert-panel/graph/badge.svg?token=ZLecmiZ5dp)](https://codecov.io/gh/zbloss/agent-expert-panel)



# 🧠 Agent Expert Panel

A sophisticated multi-agent discussion framework that orchestrates AI experts to solve complex problems through collaborative reasoning.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Overview

**Agent Expert Panel** is a powerful Python framework for multi-agent AI collaboration, inspired by groundbreaking research from Microsoft's MAI-DxO (Medical AI Diagnostic Orchestrator) and Hugging Face's Consilium platform. 

Recent research has demonstrated that multi-agent systems can achieve remarkable results:
- Microsoft's MAI-DxO achieved **85.5% diagnostic accuracy** vs **20% for human physicians** on complex medical cases
- Multi-agent collaboration reduces cognitive biases and improves decision quality
- Diverse expert perspectives lead to more robust and comprehensive solutions

## 🎯 Key Features

- **🤖 5 Specialized AI Experts** - Each with distinct expertise and reasoning patterns
- **🔄 Multiple Discussion Patterns** - Round-robin, structured debate, and more
- **⚙️ Configuration-Driven** - Easy customization via YAML files
- **🎨 Rich CLI Interface** - Beautiful interactive and batch modes
- **📦 Easy Integration** - Use as a library or command-line tool
- **🔧 Extensible Architecture** - Add custom agents and discussion patterns

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/zbloss/agent-expert-panel.git
cd agent-expert-panel

# Install dependencies (using uv - recommended)
uv sync

# Or using pip
pip install -e .
```

### Basic Usage

#### Interactive Mode
```bash
# Run interactive CLI
python main.py

# Or after installation
agent-panel
```

#### Batch Mode
```bash
# Run a specific discussion
python main.py --topic "Should we adopt microservices architecture?" --pattern round_robin --rounds 3
```

#### Programmatic Usage
```python
import asyncio
from agent_expert_panel.panel import ExpertPanel, DiscussionPattern

async def main():
    # Initialize the expert panel
    panel = ExpertPanel()
    
    # Run a discussion
    result = await panel.discuss(
        topic="How can we improve team productivity?",
        pattern=DiscussionPattern.ROUND_ROBIN,
        max_rounds=3
    )
    
    print(f"Recommendation: {result.final_recommendation}")

asyncio.run(main())
```

## 👥 Meet the Expert Panel

### 🥊 The Advocate
*Champions ideas with conviction and evidence*

The Advocate is a passionate expert who builds strong cases for promising positions. Armed with extensive factual evidence and compelling arguments, they excel at identifying opportunities, highlighting benefits, and motivating action. When the panel needs someone to push forward with confidence, The Advocate steps up with enthusiasm and conviction.

### 🔍 The Critic  
*Rigorous quality assurance and risk analysis*

The Critic serves as the panel's quality assurance specialist, approaching every proposal with healthy skepticism. They excel at identifying potential flaws, hidden risks, and unintended consequences. The Critic asks the tough questions and ensures decisions are made with full awareness of potential downsides.

### ⚡ The Pragmatist
*Practical implementation focus*

The Pragmatist cuts through theoretical complexities to deliver actionable solutions that work in practice. They prioritize feasibility, cost-effectiveness, and simplicity, always asking "What can we actually accomplish?" The Pragmatist provides clear, practical roadmaps for moving from ideas to action.

### 📚 The Research Specialist
*Fact-finding and evidence gathering*

The Research Specialist brings deep domain knowledge, current data, and evidence-based insights to every discussion. They ensure all panel discussions are grounded in accurate, up-to-date information and can quickly dive deep into specific topics to uncover relevant details others might miss.

### 💡 The Innovator
*Creative disruption and breakthrough solutions*

The Innovator challenges conventional thinking and generates novel ideas others haven't considered. With a natural ability to connect disparate concepts and see opportunities where others see obstacles, they provide the creative spark needed for transformative solutions.

## 🔧 Usage Examples

### Example 1: Quick Decision Support
```python
panel = ExpertPanel()
consensus = await panel.quick_consensus(
    "What are the top 3 priorities for a startup's first year?"
)
print(consensus)
```

### Example 2: Technical Architecture Discussion
```python
result = await panel.discuss(
    topic="Should we migrate to microservices?",
    participants=["advocate", "critic", "pragmatist"],  # Focus on implementation
    max_rounds=2
)
```

### Example 3: Innovation Brainstorming
```python
result = await panel.discuss(
    topic="How can AI improve customer experience?",
    participants=["innovator", "research_specialist", "advocate"],
    pattern=DiscussionPattern.STRUCTURED_DEBATE
)
```

## ⚙️ Configuration

Agents are configured via YAML files in the `configs/` directory:

```yaml
# configs/advocate.yaml
name: "advocate"
model_name: "qwen3:4b"
openai_base_url: "http://localhost:11434/v1"
openai_api_key: ""
timeout: 30.0
description: "A passionate expert who champions ideas with conviction"
system_message: |
  You are The Advocate, a passionate and confident expert...
model_info:
  vision: false
  function_calling: true
  json_output: true
```

### Custom Model Support

The framework supports any OpenAI-compatible API:
- **Local models**: Ollama, LocalAI, LM Studio
- **Cloud providers**: OpenAI, Anthropic, Google, etc.
- **Custom endpoints**: Any OpenAI-compatible service

## 🎨 CLI Reference

```bash
agent-panel --help

Usage: agent-panel [OPTIONS]

Options:
  -t, --topic TEXT        Topic for discussion
  -p, --pattern TEXT      Discussion pattern (round_robin, structured_debate)
  -r, --rounds INTEGER    Maximum discussion rounds (default: 3)
  -c, --config-dir PATH   Custom config directory
  -v, --verbose           Enable verbose logging
  --help                  Show this message and exit
```

## 📚 Advanced Usage

### Custom Discussion Patterns

```python
class ExpertPanel:
    async def discuss(
        self,
        topic: str,
        pattern: DiscussionPattern = DiscussionPattern.ROUND_ROBIN,
        max_rounds: int = 3,
        participants: Optional[List[str]] = None,
        with_human: bool = False  # Include human in discussion
    ) -> PanelResult:
```

### Available Patterns
- **Round Robin**: Each agent contributes in sequence
- **Structured Debate**: Formal debate with phases
- **Open Floor**: (Coming soon) Agents speak when they have input

### Export Results

Discussion results can be accessed programmatically:

```python
result = await panel.discuss(topic="...")

# Access detailed results
print(f"Topic: {result.topic}")
print(f"Consensus: {result.consensus_reached}")
print(f"Participants: {result.agents_participated}")
print(f"History: {result.discussion_history}")
```

## 🧪 Development

### Running Examples

```bash
# Simple discussion example
python examples/simple_discussion.py

# Custom agent configuration example  
python examples/custom_agents.py
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=agent_expert_panel
```

### Adding Custom Agents

1. Create a new YAML config in `configs/`
2. Update `ExpertPanel._load_agents()` to include your agent
3. Customize the system message and model parameters

## 🔬 Research Foundation

This framework is inspired by cutting-edge research in multi-agent AI:

- **Microsoft's MAI-DxO**: [The Path to Medical Superintelligence](https://microsoft.ai/new/the-path-to-medical-superintelligence/)
- **Hugging Face Consilium**: [Multi-LLM Collaboration](https://huggingface.co/blog/consilium-multi-llm)
- **Multi-Agent Debate Research**: Encouraging diverse reasoning through structured agent interaction

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution
- Additional discussion patterns
- New agent personalities
- Integration with more LLM providers
- Enhanced result export formats
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft Research for MAI-DxO inspiration
- Hugging Face for Consilium multi-LLM concepts  
- AutoGen team for the excellent agent framework
- The open-source AI community for continued innovation

---

**Ready to harness the power of collaborative AI?** Start your first expert panel discussion today! 🚀 


