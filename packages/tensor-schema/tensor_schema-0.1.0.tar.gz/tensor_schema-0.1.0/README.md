# Tensor Schema

Validate PyTorch tensor shapes using Python type annotations — fast, runtime-safe, and production-ready.

## Overview

Tensor Schema enables robust, automatic validation of PyTorch tensor shapes using Python type annotations. Designed for multimodal and ML pipelines, it helps teams catch shape mismatches early, standardize input contracts, and streamline debugging.

**Key benefits:**
- Enforce input shape contracts at runtime
- Debug shape errors before model execution
- Standardize multimodal/model input types
- Integrate seamlessly with type annotations

## Installation

```bash
pip install tensor-schema
```

## Example: TypedDict vs. TensorSchema

**Without validation:**
```python
class Phi3VImagePixelInputs(TypedDict):
    type: Literal["pixel_values"]
    data: Union[torch.Tensor, List[torch.Tensor]]  # (batch_size * num_images, 1 + num_patches, num_channels, height, width)
    image_sizes: torch.Tensor  # (batch_size * num_images, 2)
```

**With TensorSchema:**
```python
from typing_extensions import Annotated  # Use this import for Python <3.9

class Phi3VImagePixelInputs(TensorSchema):
    """
    b: batch size
    n: number of images
    p: number of patches
    h: patch height
    w: patch width
    """
    type: Literal["pixel_values"] = "pixel_values"
    data: Annotated[Union[torch.Tensor, List[torch.Tensor]], TensorShape("bn", "p", 3, "h", "w")]
    image_sizes: Annotated[Union[torch.Tensor, List[torch.Tensor]], TensorShape("bn", 2)]

inputs = Phi3VImagePixelInputs(
    data=torch.randn(16, 64, 3, 32, 32),
    image_sizes=torch.randint(0, 256, (16, 2))
)
inputs.validate()  # Raises ValueError if shape is invalid
```

## How It Works

- **Annotation-driven**: Specify expected shapes with `Annotated` and `TensorShape`.
- **Symbolic & constant dims**: Enforce both named and fixed dimensions across fields.
- **List/tuple support**: Validate leading dimension with `len()`, recurse on elements.
- **Optional fields**: Handle `None` and omitted fields.
- **Performance toggle**: Enable/disable validation as needed.
- **Clear errors**: Immediate, actionable feedback on mismatches.

## Use Cases

- Model input validation in ML pipelines
- Data loader and preprocessing checks
- Debugging and test assertions
- Enforcing input contracts in shared libraries
- Standardizing APIs for multimodal models

## Integration & Extensibility

- Drop-in for any PyTorch-based ML or data pipeline
- Easily integrates into multimodal and preprocessing workflows
- Designed for future backend extensions (e.g., NumPy, JAX, MLX — currently only PyTorch is supported)

## Validated Scenarios

- Single tensor and list/tuple inputs
- Symbolic and constant dimension checks
- Runtime shape substitution
- Variable-length and dynamic dimensions
- Optional fields and omission
- Validation toggle
- Mismatch and error cases

See `test_log.txt` for details.

## Running Tests

To run tests, first set up a virtual environment and install the package in editable mode:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest
pytest tests/
```

To confirm your installation, you can also run:
```bash
python -c "from tensor_schema import TensorSchema; print('TensorSchema import successful')"
```

**Note:**
- Using a virtual environment avoids permission issues and ensures dependencies are isolated.
- Avoid using the system Python for development. Prefer a venv, conda, or Homebrew/pyenv Python.

---

**Roadmap:**
- PyPI releases and versioning
- Deeper integration with ML libraries
- Broader backend/tensor support (NumPy, JAX, MLX)
