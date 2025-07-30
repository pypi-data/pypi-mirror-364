# Paramorph Client Library

Paramorph is a client library that provides automated hyperparameter tuning for neural network training. It integrates seamlessly with Hugging Face Transformers and other PyTorch-based training frameworks to dynamically adjust learning rates, weight decay, and other hyperparameters during training.

## Features

- **Automated Hyperparameter Tuning**: Dynamically adjusts learning rates, weight decay, and other optimizer parameters
- **Hugging Face Integration**: Built-in support for Hugging Face Transformers with minimal code changes
- **Multi-Agent Architecture**: Uses specialized agents for different parameter groups (embeddings, attention, linear layers, convolutions)
- **Real-time Monitoring**: Integrates with Weights & Biases for experiment tracking
- **Flexible Configuration**: Easy-to-use YAML configuration system

## Installation

### Prerequisites

- Python 3.12+
- PyTorch
- Hugging Face Transformers (for HF integration)
- [Optional] Weights & Biases account and API key (for experiment tracking and logging)

### Setup

Paramorph depends on the `libinephany` package, which provides core utilities and data models. Installation instructions differ based on your use case:

Ensure that python3.12 and make is installed:

#### Ubuntu / Debian
```commandline
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 make
```

#### MacOS with brew
```commandline
brew install python@3.12
brew install make
```

#### For Developers (Monorepo)
If you're working within the Inephany monorepo, the `libinephany` package is already available and will be installed into the venv created for this package when you run `make install-dev`.

#### For Clients (Standalone Installation)
Since `libinephany` is not yet published on PyPI, you'll need to build and install both `libinephany` and `paramorph` manually from source. Follow these steps:

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

6. **Change into the `paramorph` directory**

7. **Build and install `paramorph`**
   ```bash
   python -m build
   pip install dist/paramorph-<version>-py3-none-any.whl
   ```
   Replace `<version>` with the actual version number of the built wheel.

**Note:**
- If you update either package, repeat the build and install steps for the updated package.

Then generate an API key in the portal and export it:
```commandline
export PARAMORPH_API_KEY=YOUR_API_KEY
```

## Quick Start with Hugging Face Transformers

Here's a complete example of using Paramorph with a GPT-2 model:

First - with your venv active - ensure `datasets` is installed with:
```bash
python -m pip install datasets
```

### Optional: Set up Weights & Biases for Experiment Tracking

For enhanced monitoring and experiment tracking, you can integrate with Weights & Biases:

1. **Install wandb** (if not already installed):
   ```bash
   python -m pip install wandb
   ```

2. **Login to wandb**:
   ```bash
   wandb login
   ```

Then you can use the script:
```python
from paramorph.build import build_for_huggingface
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import transformers
import torch.optim as optim

try:
    import wandb  # Optional!
except ImportError:
    wandb = None

if wandb is not None:
    # Optional, if you installed and configured Weights & Biases: Initialize wandb run
    wandb.init(
        project="paramorph-experiment",
        name="gpt2-paramorph-tuning",
        config={
            "model": "gpt2",
            "initial_lr": 0.0003,
            "initial_weight_decay": 0.01,
        }
    )

# Load and prepare dataset
dataset = load_dataset("wikimedia/wikipedia", "20231101.simple", split="train", streaming=True)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Create model
config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_ctx=512,
    n_embd=768,
    n_layer=3,
    n_head=4,
)
model = GPT2LMHeadModel(config)

# Build Paramorph components
callbacks, optimizer, lr_scheduler, trainer_cls = build_for_huggingface(
    model=model,
    optimizer_type=optim.AdamW,
    paramorph_config_path="./config.yaml",
    initial_learning_rate=0.0003,
    initial_weight_decay=0.01,
)

# Configure training arguments
args = TrainingArguments(
    output_dir="./hf_test_models",
    max_steps=10000,
    num_train_epochs=1,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=0.0003,
    weight_decay=0.01,
    lr_scheduler_type="constant",  # Required for Paramorph when using learning rate agents
    max_grad_norm=-1,              # Required for Paramorph when using gradient clipping agents
    disable_tqdm=False,
    dataloader_num_workers=2,
    dataloader_pin_memory=True,
    dataloader_prefetch_factor=2,
    fp16=True,
    gradient_checkpointing=False,
)

# Create and run trainer
trainer = trainer_cls(
    model=model,
    args=args,
    train_dataset=tokenized_dataset,
    eval_dataset=None,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    processing_class=tokenizer,
    optimizers=(optimizer, lr_scheduler),
    callbacks=[callbacks],
)

trainer.train()

# Optional: Finish wandb run
if wandb is not None and wandb.run is not None:
    wandb.finish()
```

**What wandb provides with Paramorph:**
- Real-time hyperparameter tracking for each parameter group
- Training metrics and loss curves
- Model performance comparisons across different hyperparameter settings
- Experiment organization and collaboration features
- Automatic logging of Paramorph's internal statistics and agent decisions

## Configuration

Create a `config.yaml` file to configure Paramorph:

```yaml
# Model identifier for the Inephany backend
inephany_model_id: alpha-v1

# Map model layers to agent types. There are four types currently: embedding, linear, convolution, attention
agent_modules:
    transformer.wte: embedding
    transformer.wpe: embedding
    transformer.h.0: attention
    transformer.h.1: attention
    transformer.h.2: attention
    transformer.ln_f: linear

# SDK configuration for backend communication
sdk_config:
  max_retries: 10
  backoff_factor: 0.5
  max_backoff: 15.0
  url_override: null

# Scheduling and tuning configuration
scheduling_config:
  nn_family: gpt
  tuning_frequency: 100  # How often to update hyperparameters (steps)

  # Statistics collection settings
  can_nullify_gradients: true
  max_statistic_cache_size: 3
  tensor_stats_downsample_percentage: 0.01
  statistic_sample_frequency: 10

  # Logging settings
  log_to_wandb: true  # Set to false if not using wandb
  force_wandb_log_on_all_ranks: false
```

## Generating the Agent Modules List

The `agent_modules` section in your `config.yaml` maps your model's named modules to agent types. This mapping tells Paramorph which parts of your model should be tuned by our agents.

### Understanding Module Types

Paramorph supports four module types:

- **`embedding`**: For embedding layers (e.g., `nn.Embedding`)
- **`attention`**: For attention/transformer layers (e.g., `nn.MultiheadAttention`, transformer blocks)
- **`linear`**: For linear/feedforward layers (e.g., `nn.Linear`, `nn.LayerNorm`)
- **`convolutional`**: For convolutional layers (e.g., `nn.Conv2d`, `nn.Conv1d`)

### How to Generate the Modules List

1. **Print your model's named modules** to see the structure:

```python
import torch.nn as nn
from transformers import GPT2LMHeadModel

# Create your model
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Print only modules with parameters
print("\nModules with parameters:")
for name, module in model.named_modules():
    if list(module.parameters()):
        print(f"{name}: {type(module).__name__}")

# To explore granularity options, you can also print the hierarchy:
print("\nModule hierarchy (for granularity decisions):")
for name, module in model.named_modules():
    if list(module.parameters()):
        depth = name.count('.')
        indent = "  " * depth
        print(f"{indent}{name}: {type(module).__name__}")
```

2. **Categorize each module** based on its type and create the mapping:

```python
def categorize_module(module_name: str, module: nn.Module) -> str:
    """Categorize a module based on its type."""
    module_type = type(module).__name__

    if module_type == "Embedding":
        return "embedding"
    elif module_type in ["Linear", "LayerNorm"]:
        return "linear"
    elif module_type in ["Conv1d", "Conv2d", "Conv3d"]:
        return "convolutional"
    elif "attention" in module_name.lower() or "attn" in module_name.lower():
        return "attention"
    else:
        # Default to linear for other types
        return "linear"

# Generate the agent_modules dictionary
agent_modules = {}
for name, module in model.named_modules():
    if list(module.parameters()):  # Only include modules with parameters
        agent_modules[name] = categorize_module(name, module)

print("Generated agent_modules:")
for name, module_type in agent_modules.items():
    print(f"  {name}: {module_type}")

# Example: Filter for different granularity levels
print("\nLayer-level modules (recommended):")
layer_level = {name: module_type for name, module_type in agent_modules.items()
               if name.count('.') <= 2}  # transformer.h.0, transformer.ln_f, etc.
for name, module_type in layer_level.items():
    print(f"  {name}: {module_type}")

print("\nComponent-level modules:")
component_level = {name: module_type for name, module_type in agent_modules.items()
                   if name.count('.') <= 3}  # transformer.h.0.attn, transformer.h.0.mlp, etc.
for name, module_type in component_level.items():
    print(f"  {name}: {module_type}")
```

### Choosing the Right Granularity

The granularity of your `agent_modules` mapping determines how fine-grained your hyperparameter tuning will be. You have several options:

#### Option 1: Layer-Level Granularity (Recommended)
Map entire transformer layers or major components:

```yaml
agent_modules:
  transformer.wte: embedding
  transformer.wpe: embedding
  transformer.h.0: attention    # Entire transformer block 0
  transformer.h.1: attention    # Entire transformer block 1
  transformer.h.2: attention    # Entire transformer block 2
  transformer.ln_f: linear
```

**Pros**: Simpler configuration, fewer agents to manage, expected form. Paramorph was trained at this level of granularity.
**Cons**: Less fine-grained control.

#### Option 2: Component-Level Granularity
Map individual components within layers:

```yaml
agent_modules:
  transformer.wte: embedding
  transformer.wpe: embedding
  transformer.h.0.attn: attention      # Just the attention component
  transformer.h.0.mlp: linear          # Just the MLP component
  transformer.h.0.ln_1: linear         # Just the layer norm
  transformer.h.1.attn: attention
  transformer.h.1.mlp: linear
  transformer.h.1.ln_1: linear
  transformer.ln_f: linear
```

**Pros**: More precise control over different components
**Cons**: More complex configuration, more agents. Paramorph was NOT trained at this level of granularity.

#### Option 3: Parameter-Level Granularity (Not Recommended)
Map individual parameters:

```yaml
agent_modules:
  transformer.wte.weight: embedding
  transformer.wte.bias: embedding
  transformer.h.0.attn.c_attn.weight: attention
  transformer.h.0.attn.c_attn.bias: attention
  transformer.h.0.attn.c_proj.weight: attention
  transformer.h.0.attn.c_proj.bias: attention
  # ... many more entries
```

**Pros**: Maximum control
**Cons**: Extremely complex, usually unnecessary, may hurt performance. Paramorph was NOT trained at this level of granularity.

### How to Decide

1. **Start with layer-level granularity** - This works well for most models and is easier to manage.

2. **Consider your model size**:
   - **Small models** (< 100M parameters): Layer-level is usually sufficient
   - **Medium models** (100M - 1B parameters): Layer-level or component-level
   - **Large models** (> 1B parameters): Component-level may be beneficial

3. **Consider your tuning goals**:
   - **General optimization**: Layer-level is fine
   - **Fine-grained control**: Component-level
   - **Research/experimentation**: Component-level for insights

4. **Consider computational overhead**: More granular = more agents = more computational cost

### Best Practices

1. **Include all parameter-containing modules**: Only modules with trainable parameters should be included in the mapping.

2. **Use appropriate module types**:
   - Use `embedding` for token/position embeddings
   - Use `attention` for attention/transformer layers (e.g., `nn.MultiheadAttention`, transformer blocks)
   - Use `linear` for linear/feedforward layers (e.g., `nn.Linear`, `nn.LayerNorm`)
   - Use `convolutional` for convolutional layers (e.g., `nn.Conv2d`, `nn.Conv1d`)
   - Use `null` for any other layers or do not mention them at all.

3. **Be consistent with naming**: The module names must exactly match those returned by `model.named_modules()`.

4. **Test your configuration**: After generating the config, verify it works by running a short training session.

5. **Customize for your model**: The automated script provides a good starting point, but you may need to adjust the categorization logic for custom model architectures.

6. **Start simple, then refine**: Begin with layer-level granularity and only increase granularity if you need more control.

### Troubleshooting

- **Missing modules**: If you see warnings about parameters not being assigned to any group, this means no Paramorph agents will act on them and their hyperparameters will remain constant throughout training.

- **Incorrect module types**: While incorrect module types won't cause errors, they may affect the effectiveness of the tuning agents. Use the most appropriate type for each module.

- **Model architecture changes**: If you modify your model architecture, regenerate the `agent_modules` mapping to ensure it matches the new structure.

### Configuration Options

#### Agent Modules
Map your model's parameter groups to agent types:
- `embedding`: For embedding layers
- `attention`: For attention/transformer layers
- `linear`: For linear/feedforward layers
- `convolution`: For convolutional layers
- `null`: For any other layers

#### Scheduling Config
- `tuning_frequency`: Steps between hyperparameter updates
- `nn_family`: Model family (gpt, bert, olmo, etc.)
- `log_to_wandb`: Enable W&B logging
- `can_nullify_gradients`: Allow gradient nullification for statistics collection
- `max_statistic_cache_size`: Maximum number of cached statistics
- `tensor_stats_downsample_percentage`: Percentage of tensor statistics to collect
- `statistic_sample_frequency`: How often to sample statistics

#### Agent Config
Enable/disable specific hyperparameter agents:
- `use_learning_rate_agents`: Tune learning rates
- `use_weight_decay_agents`: Tune weight decay
- `use_dropout_agents`: Tune dropout rates
- `use_grad_clip_agents`: Tune gradient clipping
- `use_adam_beta_one_agents`: Tune Adam β₁
- `use_adam_beta_two_agents`: Tune Adam β₂
- `use_adam_eps_agents`: Tune Adam ε

## Advanced Usage

### Custom Training Loop

For non-Hugging Face training, use the core Paramorph class:

```python
from paramorph.build import build
from paramorph.core import Paramorph

# Build optimizer and Paramorph instance
optimizer, paramorph = build(
    model=model,
    optimizer_type=optim.AdamW,
    paramorph_config_path="./config.yaml",
    initial_learning_rate=0.0003,
    initial_weight_decay=0.01,
)

# Custom training loop
for epoch in range(num_epochs):
    for batch in dataloader:
        optimizer.zero_grad()
        loss = model(batch)
        loss.backward()
        optimizer.step()

        # Update hyperparameters
        paramorph.step()
```

### Custom Callbacks

Subclass `ParamorphCallbacks` to customize behavior:

```python
from paramorph.paramorph_callbacks import ParamorphCallbacks

class CustomParamorphCallbacks(ParamorphCallbacks):
    def set_learning_rate(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """
        print(f"Parameter group {parameter_group_name} updated learning rate to {value}")
        super().set_learning_rate(parameter_group_name, value)

# Use in build function
callbacks, optimizer, lr_scheduler, trainer_cls = build_for_huggingface(
    model=model,
    optimizer_type=optim.AdamW,
    paramorph_config_path="./config.yaml",
    initial_learning_rate=0.0003,
    initial_weight_decay=0.01,
    paramorph_callback_override=CustomParamorphCallbacks,
)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the virtual environment and have installed the package correctly.

2. **libinephany Import Errors**: If you see import errors related to `libinephany`, make sure you've installed it correctly:
   - For developers: Ensure you're in the monorepo and the package is available
   - For clients: Make sure you've cloned and installed `libinephany` from its mirror repository before installing paramorph

3. **W&B Login Issues**: Make sure you're logged in with `wandb login` and have a valid API key.

4. **Configuration Errors**: Check that your `config.yaml` follows the correct format and all required fields are present.

5. **Training Arguments**: Ensure you're using the required Hugging Face training arguments:
   - `lr_scheduler_type="constant"` - Required when using learning rate agents
   - `max_grad_norm=-1` - Required when using gradient clipping agents

6. **Dependency Conflicts**: If you encounter dependency conflicts, try installing in a fresh virtual environment:
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate
   # Install libinephany first, then paramorph
   ```

### Getting Help

- Check the example scripts in the repository
- Review the configuration file format
- Ensure all dependencies are installed correctly
- Verify your model architecture matches the agent module mapping

## Architecture

Paramorph uses a multi-agent architecture where different agents control hyperparameters for different parts of your model. Agents can be applied to any layer and at any level of granularity as defined in the config.
