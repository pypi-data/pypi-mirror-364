"""
Model I/O Utilities for OpenArchX.

This module provides utilities for saving and loading OpenArchX models to/from
disk in the native .oaxm format, as well as conversion utilities for other formats.
"""

import os
import json
import pickle
import numpy as np
import importlib.util
from ..core.tensor import Tensor


class ModelSerializer:
    """Utility for serializing OpenArchX models to the native .oaxm format."""
    
    @staticmethod
    def save_model(model, filepath, metadata=None, compress=True):
        """
        Save an OpenArchX model to a .oaxm file.
        
        Args:
            model: The OpenArchX model to save.
            filepath: The path to save the model to. If the extension is not .oaxm,
                      it will be appended.
            metadata: Optional dictionary of metadata to save with the model.
            compress: Whether to compress the saved model file.
            
        Returns:
            The path to the saved model file.
        """
        # Ensure the file has the .oaxm extension
        if not filepath.endswith('.oaxm'):
            filepath += '.oaxm'
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        # Prepare model state
        model_state = {}
        
        # Get model parameters
        if hasattr(model, 'state_dict'):
            params = model.state_dict()
        else:
            # Fallback for models without state_dict method
            params = {}
            for key, value in model.__dict__.items():
                if key.startswith('_'):
                    continue
                if isinstance(value, Tensor):
                    params[key] = value
        
        # Convert Tensor objects to numpy arrays
        model_state['parameters'] = {
            name: param.data if isinstance(param, Tensor) else param
            for name, param in params.items()
        }
        
        # Save model architecture if available
        if hasattr(model, 'config'):
            model_state['config'] = model.config
        elif hasattr(model, 'architecture'):
            model_state['architecture'] = model.architecture
            
        # Add metadata
        if metadata is not None:
            model_state['metadata'] = metadata
        else:
            model_state['metadata'] = {
                'format_version': '1.0',
                'framework': 'openarchx',
                'model_type': model.__class__.__name__
            }
            
        # Save model state
        if compress:
            import gzip
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(model_state, f)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(model_state, f)
                
        return filepath
    
    @staticmethod
    def load_model(filepath, model_class=None):
        """
        Load an OpenArchX model from a .oaxm file.
        
        Args:
            filepath: The path to the model file.
            model_class: The model class to instantiate. If None, the method will
                         try to infer it from the saved metadata.
            
        Returns:
            The loaded OpenArchX model.
        """
        # Check if the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
            
        # Load the model state
        if filepath.endswith('.oaxm.gz') or (filepath.endswith('.oaxm') and _is_gzipped(filepath)):
            import gzip
            with gzip.open(filepath, 'rb') as f:
                model_state = pickle.load(f)
        else:
            with open(filepath, 'rb') as f:
                model_state = pickle.load(f)
                
        # Get the model parameters
        parameters = model_state.get('parameters', {})
        
        # Convert numpy arrays to Tensor objects
        tensor_params = {
            name: Tensor(param) if isinstance(param, np.ndarray) else param
            for name, param in parameters.items()
        }
        
        # Get model configuration
        config = model_state.get('config', None)
        architecture = model_state.get('architecture', None)
        
        # Initialize the model
        if model_class is not None:
            # Use the provided model class
            if config is not None:
                model = model_class(config=config)
            else:
                model = model_class()
        else:
            # Try to infer the model class from metadata
            metadata = model_state.get('metadata', {})
            model_type = metadata.get('model_type', None)
            
            if model_type is None:
                raise ValueError("Model class must be provided if not stored in metadata")
                
            # Import the model class dynamically
            from ..nn.models import get_model_class
            try:
                model_class = get_model_class(model_type)
                if config is not None:
                    model = model_class(config=config)
                else:
                    model = model_class()
            except (ImportError, AttributeError):
                raise ValueError(f"Could not import model class: {model_type}")
                
        # Load parameters into the model
        if hasattr(model, 'load_state_dict'):
            model.load_state_dict(tensor_params)
        else:
            # Fallback for models without load_state_dict method
            for name, param in tensor_params.items():
                if hasattr(model, name):
                    setattr(model, name, param)
                    
        return model


class ModelConverter:
    """Utility for converting between different model formats."""
    
    @staticmethod
    def from_pytorch(torch_model, output_file, metadata=None):
        """
        Convert a PyTorch model to OpenArchX .oaxm format.
        
        Args:
            torch_model: The PyTorch model to convert.
            output_file: The path to save the converted model.
            metadata: Optional metadata to include in the saved model.
            
        Returns:
            The path to the saved .oaxm file.
        """
        # Check if PyTorch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        import torch
        
        # Get model parameters
        state_dict = torch_model.state_dict()
        
        # Convert to numpy arrays
        numpy_params = {
            name: param.detach().cpu().numpy()
            for name, param in state_dict.items()
        }
        
        # Create model state
        model_state = {
            'parameters': numpy_params,
            'metadata': {
                'format_version': '1.0',
                'framework': 'openarchx',
                'original_framework': 'pytorch',
                'model_type': torch_model.__class__.__name__
            }
        }
        
        # Update with custom metadata if provided
        if metadata is not None:
            model_state['metadata'].update(metadata)
            
        # Save the model
        if not output_file.endswith('.oaxm'):
            output_file += '.oaxm'
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Save the model
        with open(output_file, 'wb') as f:
            pickle.dump(model_state, f)
            
        return output_file
    
    @staticmethod
    def from_tensorflow(tf_model, output_file, metadata=None):
        """
        Convert a TensorFlow model to OpenArchX .oaxm format.
        
        Args:
            tf_model: The TensorFlow model to convert.
            output_file: The path to save the converted model.
            metadata: Optional metadata to include in the saved model.
            
        Returns:
            The path to the saved .oaxm file.
        """
        # Check if TensorFlow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        
        # Get model weights
        weights = tf_model.get_weights()
        weight_names = [weight.name for weight in tf_model.weights]
        
        # Create parameters dictionary
        numpy_params = {
            name.replace(':0', ''): weight
            for name, weight in zip(weight_names, weights)
        }
        
        # Create model state
        model_state = {
            'parameters': numpy_params,
            'metadata': {
                'format_version': '1.0',
                'framework': 'openarchx',
                'original_framework': 'tensorflow',
                'model_type': tf_model.__class__.__name__
            }
        }
        
        # Update with custom metadata if provided
        if metadata is not None:
            model_state['metadata'].update(metadata)
            
        # Save the model
        if not output_file.endswith('.oaxm'):
            output_file += '.oaxm'
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Save the model
        with open(output_file, 'wb') as f:
            pickle.dump(model_state, f)
            
        return output_file
    
    @staticmethod
    def to_pytorch(oaxm_file, torch_model=None):
        """
        Convert an OpenArchX .oaxm model to PyTorch format.
        
        Args:
            oaxm_file: The path to the .oaxm model file.
            torch_model: Optional PyTorch model to load the parameters into.
                         If None, an equivalent PyTorch model will be created.
            
        Returns:
            The PyTorch model with the loaded parameters.
        """
        # Check if PyTorch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        import torch
        
        # Load the OpenArchX model
        model_state = _load_oaxm_state(oaxm_file)
        parameters = model_state.get('parameters', {})
        
        # If no PyTorch model is provided, we can't create one automatically
        # as the architecture is not fully defined in the .oaxm file
        if torch_model is None:
            raise ValueError("A PyTorch model must be provided to load parameters into")
            
        # Convert numpy arrays to PyTorch tensors
        torch_state_dict = {
            name: torch.tensor(param) if isinstance(param, np.ndarray) else param
            for name, param in parameters.items()
        }
        
        # Load parameters into the model
        torch_model.load_state_dict(torch_state_dict)
        
        return torch_model
    
    @staticmethod
    def to_tensorflow(oaxm_file, tf_model=None):
        """
        Convert an OpenArchX .oaxm model to TensorFlow format.
        
        Args:
            oaxm_file: The path to the .oaxm model file.
            tf_model: Optional TensorFlow model to load the parameters into.
                      If None, an equivalent TensorFlow model will be created.
            
        Returns:
            The TensorFlow model with the loaded parameters.
        """
        # Check if TensorFlow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        
        # Load the OpenArchX model
        model_state = _load_oaxm_state(oaxm_file)
        parameters = model_state.get('parameters', {})
        
        # If no TensorFlow model is provided, we can't create one automatically
        if tf_model is None:
            raise ValueError("A TensorFlow model must be provided to load parameters into")
            
        # Get weight names from the TensorFlow model
        weight_names = [weight.name.replace(':0', '') for weight in tf_model.weights]
        
        # Map the parameters to the TensorFlow weights
        weights = []
        for name in weight_names:
            if name in parameters:
                weights.append(parameters[name])
            else:
                raise ValueError(f"Parameter not found in .oaxm file: {name}")
                
        # Set the weights
        tf_model.set_weights(weights)
        
        return tf_model


class ModelRegistry:
    """Registry for model architectures to help with model loading."""
    
    _registry = {}
    
    @classmethod
    def register(cls, name, model_class):
        """
        Register a model class with a name.
        
        Args:
            name: The name to register the model class under.
            model_class: The model class to register.
        """
        cls._registry[name] = model_class
        
    @classmethod
    def get(cls, name):
        """
        Get a model class by name.
        
        Args:
            name: The name of the model class.
            
        Returns:
            The model class or None if not found.
        """
        return cls._registry.get(name, None)
        
    @classmethod
    def list_models(cls):
        """
        List all registered model names.
        
        Returns:
            A list of registered model names.
        """
        return list(cls._registry.keys())


# Helper functions

def _is_gzipped(filepath):
    """Check if a file is gzipped."""
    with open(filepath, 'rb') as f:
        return f.read(2) == b'\x1f\x8b'


def _load_oaxm_state(filepath):
    """Load the state from a .oaxm file."""
    # Check if the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
        
    # Load the model state
    if filepath.endswith('.oaxm.gz') or (filepath.endswith('.oaxm') and _is_gzipped(filepath)):
        import gzip
        with gzip.open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        with open(filepath, 'rb') as f:
            return pickle.load(f)


# Convenience functions

def save_model(model, filepath, metadata=None, compress=True):
    """
    Save an OpenArchX model to a .oaxm file.
    
    Args:
        model: The OpenArchX model to save.
        filepath: The path to save the model to.
        metadata: Optional dictionary of metadata to save with the model.
        compress: Whether to compress the saved model file.
        
    Returns:
        The path to the saved model file.
    """
    return ModelSerializer.save_model(model, filepath, metadata, compress)


def load_model(filepath, model_class=None):
    """
    Load an OpenArchX model from a .oaxm file.
    
    Args:
        filepath: The path to the model file.
        model_class: The model class to instantiate. If None, the method will
                     try to infer it from the saved metadata.
        
    Returns:
        The loaded OpenArchX model.
    """
    return ModelSerializer.load_model(filepath, model_class)


def convert_from_pytorch(torch_model, output_file, metadata=None):
    """
    Convert a PyTorch model to OpenArchX .oaxm format.
    
    Args:
        torch_model: The PyTorch model to convert.
        output_file: The path to save the converted model.
        metadata: Optional metadata to include in the saved model.
        
    Returns:
        The path to the saved .oaxm file.
    """
    return ModelConverter.from_pytorch(torch_model, output_file, metadata)


def convert_from_tensorflow(tf_model, output_file, metadata=None):
    """
    Convert a TensorFlow model to OpenArchX .oaxm format.
    
    Args:
        tf_model: The TensorFlow model to convert.
        output_file: The path to save the converted model.
        metadata: Optional metadata to include in the saved model.
        
    Returns:
        The path to the saved .oaxm file.
    """
    return ModelConverter.from_tensorflow(tf_model, output_file, metadata)


def convert_to_pytorch(oaxm_file, torch_model=None):
    """
    Convert an OpenArchX .oaxm model to PyTorch format.
    
    Args:
        oaxm_file: The path to the .oaxm model file.
        torch_model: Optional PyTorch model to load the parameters into.
                     If None, an equivalent PyTorch model will be created.
        
    Returns:
        The PyTorch model with the loaded parameters.
    """
    return ModelConverter.to_pytorch(oaxm_file, torch_model)


def convert_to_tensorflow(oaxm_file, tf_model=None):
    """
    Convert an OpenArchX .oaxm model to TensorFlow format.
    
    Args:
        oaxm_file: The path to the .oaxm model file.
        tf_model: Optional TensorFlow model to load the parameters into.
                  If None, an equivalent TensorFlow model will be created.
        
    Returns:
        The TensorFlow model with the loaded parameters.
    """
    return ModelConverter.to_tensorflow(oaxm_file, tf_model)


def register_model(name, model_class):
    """
    Register a model class with a name.
    
    Args:
        name: The name to register the model class under.
        model_class: The model class to register.
    """
    ModelRegistry.register(name, model_class)


def get_model_class(name):
    """
    Get a model class by name.
    
    Args:
        name: The name of the model class.
        
    Returns:
        The model class or None if not found.
    """
    return ModelRegistry.get(name)


def list_registered_models():
    """
    List all registered model names.
    
    Returns:
        A list of registered model names.
    """
    return ModelRegistry.list_models() 