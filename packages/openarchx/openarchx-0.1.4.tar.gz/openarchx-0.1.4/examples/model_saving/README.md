# OpenArchX Model Saving and Loading

This directory contains examples showing how to save and load models in OpenArchX's native `.oaxm` format.

## What is .oaxm?

The `.oaxm` format (OpenArchX Model) is a native serialization format for OpenArchX models. It provides a consistent way to save and load models independent of external machine learning frameworks.

## Features

- Save OpenArchX models to disk in a portable format
- Load models back into memory for inference or further training
- Convert between PyTorch/TensorFlow models and OpenArchX models
- Include metadata with saved models
- Option to compress model files to save disk space

## Examples

The `model_saving_example.py` file demonstrates:

1. How to create and train a simple model
2. How to save the model to a `.oaxm` file
3. How to load a model from a `.oaxm` file
4. How to convert between PyTorch/TensorFlow models and OpenArchX models
5. How to include metadata when saving models

## Usage

Run the example script:

```python
python model_saving_example.py
```

## Basic Usage

```python
from openarchx.utils import save_model, load_model

# Save a model
save_model(my_model, "path/to/model.oaxm")

# Load a model
loaded_model = load_model("path/to/model.oaxm", model_class=MyModelClass)

# Save with metadata and compression
metadata = {
    "description": "My awesome model",
    "version": "1.0.0",
    "author": "Your Name"
}
save_model(my_model, "path/to/model.oaxm", metadata=metadata, compress=True)
```

## Framework Conversions

Convert PyTorch models to OpenArchX:

```python
from openarchx.utils import convert_from_pytorch

# Convert PyTorch model to .oaxm
convert_from_pytorch(torch_model, "path/to/model.oaxm")
```

Convert TensorFlow models to OpenArchX:

```python
from openarchx.utils import convert_from_tensorflow

# Convert TensorFlow model to .oaxm
convert_from_tensorflow(tf_model, "path/to/model.oaxm")
```

Convert in the opposite direction:

```python
from openarchx.utils import convert_to_pytorch, convert_to_tensorflow

# Convert .oaxm to PyTorch (needs an empty PyTorch model with matching architecture)
convert_to_pytorch("path/to/model.oaxm", torch_model)

# Convert .oaxm to TensorFlow (needs an empty TensorFlow model with matching architecture)
convert_to_tensorflow("path/to/model.oaxm", tf_model)
``` 