# Inephany Common Library

The Inephany Common Library (`libinephany`) is a core utility package that provides shared functionality, data models, and utilities used across multiple Inephany packages. It contains essential components for hyperparameter optimization, model observation, data serialization, and common utilities.

## Features

- **Pydantic Data Models**: Comprehensive schemas for hyperparameters, observations, and API communications
- **Utility Functions**: Common utilities for PyTorch, optimization, transforms, and more
- **Observation System**: Tools for collecting and managing model statistics and observations
- **Constants and Enums**: Standardized constants and enumerations for agent types, model families, and module types
- **AWS Integration**: Utilities for AWS services integration
- **Web Application Utilities**: Common web app functionality and endpoints

## Installation

### Prerequisites

- Python 3.12+
- Make (for build automation)

#### Ubuntu / Debian
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 make
```

#### MacOS with brew
```bash
brew install python@3.12
brew install make
```

### For Developers (Monorepo)

If you're working within the Inephany monorepo, the package is already available and will be installed automatically when you run the installation commands in dependent packages.

### For Clients (Standalone Installation)

Since `libinephany` is not yet published on PyPI, you'll need to build and install it manually from source. Follow these steps:

1. **Create a new virtual environment**
   ```bash
   python3.12 -m venv myenv
   ```

2. **Activate the virtual environment**
   ```bash
   source myenv/bin/activate
   ```

3. **Install Build Tools**
   ```bash
   python -m pip install --upgrade pip setuptools build wheel
   ```

4. **Change into the `libinephany` directory**

5. **Build and install `libinephany`**
   ```bash
   python -m build
   pip install dist/libinephany-<version>-py3-none-any.whl
   ```
   Replace `<version>` with the actual version number of the built wheel.

**Note**: Once `libinephany` is published to PyPI, you'll be able to install it with `pip install libinephany`.

## Key Components

### Pydantic Models

The package provides comprehensive data models for:

- **Hyperparameter Configurations**: `HParamConfig`, `HParamConfigs`
- **Observation Models**: `ObservationInputs`, tensor statistics
- **API Schemas**: Request/response models for client-server communication
- **State Management**: Hyperparameter states and update callbacks

### Utility Functions

#### Agent Utilities (`agent_utils.py`)
- Agent ID generation and parsing
- Hyperparameter group management
- Agent type validation

#### Constants (`constants.py`)
- Hyperparameter type constants (learning_rate, weight_decay, etc.)
- Agent prefixes and suffixes
- API key headers and timestamp formats

#### Enums (`enums.py`)
- `AgentTypes`: Learning rate, weight decay, dropout, etc.
- `ModelFamilies`: GPT, BERT, OLMo
- `ModuleTypes`: Convolutional, attention, linear, embedding

#### Optimization Utilities (`optim_utils.py`)
- PyTorch optimizer utilities
- Parameter group management
- Learning rate scheduler utilities

#### PyTorch Utilities (`torch_utils.py`)
- Tensor operations
- Model utilities
- Distributed training helpers

### Observation System

The observation system provides tools for collecting and managing model statistics:

- **StatisticManager**: Centralized statistics collection and management
- **ObserverPipeline**: Configurable observation pipelines
- **PipelineCoordinator**: Coordinates multiple observers
- **StatisticTrackers**: Specialized trackers for different metric types

## Usage Examples

### Basic Import Examples

```python
# Import common constants
from libinephany.utils.constants import LEARNING_RATE, WEIGHT_DECAY, AGENT_PREFIX_LR

# Import enums
from libinephany.utils.enums import AgentTypes, ModelFamilies, ModuleTypes

# Import utility functions
from libinephany.utils import agent_utils, optim_utils, torch_utils

# Import data models
from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig
from libinephany.pydantic_models.schemas.response_schemas import ClientPolicySchemaResponse
```

### Working with Agent Types

```python
from libinephany.utils.enums import AgentTypes

# Check if an agent type is valid
agent_type = "learning_rate"
if agent_type in [agent.value for agent in AgentTypes]:
    print(f"{agent_type} is a valid agent type")

# Get agent type by index
lr_agent = AgentTypes.get_from_index(0)  # LearningRateAgent
```

### Using Constants

```python
from libinephany.utils.constants import AGENT_PREFIX_LR, LEARNING_RATE

# Generate agent ID
agent_id = f"{AGENT_PREFIX_LR}_agent_001"
hyperparam_type = LEARNING_RATE
```

### Working with Pydantic Models

```python
from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig

# Create a hyperparameter configuration
config = HParamConfig(
    name="learning_rate",
    value=0.001,
    min_value=1e-6,
    max_value=1.0
)
```

## Development

### Running Tests
```bash
make execute-unit-tests
```

### Code Quality
```bash
make lint          # Run all linters
make fix-black     # Fix formatting
make fix-isort     # Fix imports
```

### Version Management
```bash
make increment-patch-version    # Increment patch version
make increment-minor-version    # Increment minor version
make increment-major-version    # Increment major version
make increment-pre-release-version # Increment pre-release version
```

## Dependencies

### Core Dependencies
- `pydantic==2.8.2` - Data validation and serialization
- `torch==2.7.1` - PyTorch for tensor operations
- `numpy==1.26.4` - Numerical computing
- `requests==2.32.4` - HTTP client
- `loguru==0.7.2` - Logging

### Optional Dependencies
- `boto3<=1.38.44` - AWS SDK
- `fastapi==0.115.11` - Web framework
- `slack-sdk==3.35.0` - Slack integration
- `transformers==4.52.4` - Hugging Face transformers
- `accelerate==1.4.0` - Hugging Face accelerate
- `gymnasium==1.0.0` - RL environments

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the virtual environment and have installed the package correctly.

2. **Version Conflicts**: If you encounter dependency conflicts, try installing in a fresh virtual environment:
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate
   make install-dev
   ```

3. **Make Command Not Found**: Ensure you have `make` installed on your system.

4. **Python Version Issues**: This package requires Python 3.12+. Ensure you're using the correct version.

### Getting Help

- Check the example scripts in the repository
- Review the test files for usage examples
- Ensure all dependencies are installed correctly
- Verify your Python version is 3.12+

## Contributing

When contributing to `libinephany`:

1. Follow the existing code style (Black, isort, flake8)
2. Add appropriate type hints
3. Include unit tests for new functionality
4. Update documentation for new features
5. Ensure all tests pass before submitting

## License

This package is part of the Inephany ecosystem and is subject to the same licensing terms as other Inephany packages.
