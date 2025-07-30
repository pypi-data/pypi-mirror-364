"""
TensorFlow Integration Utilities for OpenArchX.

This module provides conversion and adapter utilities for using TensorFlow models
and datasets with OpenArchX. These utilities are completely optional and do not 
affect OpenArchX's core functionality, which remains independent from external libraries.
"""

import numpy as np
import importlib.util
from ..core.tensor import Tensor


class TensorFlowModelAdapter:
    """Adapter for using TensorFlow models with OpenArchX."""
    
    def __init__(self, tf_model, device=None):
        """
        Initialize a TensorFlow model adapter.
        
        Args:
            tf_model: A TensorFlow/Keras model.
            device: The device to run the model on ('/CPU:0', '/GPU:0', etc.).
        """
        # Check if tensorflow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        
        self.model = tf_model
        
        # Handle device placement
        if device is not None:
            with tf.device(device):
                # Create a duplicate model on the specified device
                self.model = tf.keras.models.clone_model(tf_model)
                self.model.set_weights(tf_model.get_weights())
        
    def __call__(self, inputs, **kwargs):
        """
        Process inputs through the TensorFlow model.
        
        Args:
            inputs: Input data, can be numpy arrays, lists, or OpenArchX Tensors.
            **kwargs: Additional arguments to pass to the model.
            
        Returns:
            OpenArchX Tensor containing the model output.
        """
        import tensorflow as tf
        
        # Convert inputs to tf tensors
        if isinstance(inputs, Tensor):
            inputs = inputs.data
            
        if isinstance(inputs, np.ndarray):
            inputs = tf.convert_to_tensor(inputs, dtype=tf.float32)
        elif isinstance(inputs, list):
            inputs = tf.convert_to_tensor(np.array(inputs), dtype=tf.float32)
        elif not isinstance(inputs, tf.Tensor):
            raise TypeError(f"Unsupported input type: {type(inputs)}")
            
        # Forward pass
        outputs = self.model(inputs, training=False, **kwargs)
            
        # Convert output to numpy and then to Tensor
        if isinstance(outputs, tf.Tensor):
            return Tensor(outputs.numpy())
        elif isinstance(outputs, (tuple, list)):
            return tuple(Tensor(output.numpy()) for output in outputs 
                        if isinstance(output, tf.Tensor))
        elif isinstance(outputs, dict):
            return {k: Tensor(v.numpy()) if isinstance(v, tf.Tensor) else v 
                   for k, v in outputs.items()}
        else:
            return outputs


class TensorFlowDatasetConverter:
    """Utility for converting between TensorFlow and OpenArchX datasets."""
    
    @staticmethod
    def to_openarchx_dataset(tf_dataset, transform=None):
        """
        Convert a TensorFlow Dataset to an OpenArchX Dataset.
        
        Args:
            tf_dataset: A TensorFlow tf.data.Dataset instance.
            transform: Optional transform to apply to the data.
            
        Returns:
            An OpenArchX Dataset.
        """
        from .data import Dataset
        
        # Check if tensorflow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        
        class OpenArchXDatasetFromTensorFlow(Dataset):
            def __init__(self, tf_dataset, transform=None):
                self.tf_dataset = tf_dataset
                self.transform = transform
                
                # Convert tf.data.Dataset to a list for random access
                self.data_list = list(tf_dataset.as_numpy_iterator())
                
            def __len__(self):
                return len(self.data_list)
                
            def __getitem__(self, idx):
                data = self.data_list[idx]
                
                # Handle different return types from TensorFlow dataset
                if isinstance(data, tuple) and len(data) == 2:
                    # Standard (input, target) format
                    features, target = data
                    
                    # Apply transform if provided
                    if self.transform:
                        features = self.transform(features)
                        
                    return features, target
                else:
                    # Generic handling for other formats
                    return data
        
        return OpenArchXDatasetFromTensorFlow(tf_dataset, transform)
    
    @staticmethod
    def from_openarchx_dataset(ox_dataset, tensor_dtype=None):
        """
        Convert an OpenArchX Dataset to a TensorFlow Dataset.
        
        Args:
            ox_dataset: An OpenArchX Dataset instance.
            tensor_dtype: Optional dtype for the TensorFlow tensors.
            
        Returns:
            A TensorFlow tf.data.Dataset.
        """
        # Check if tensorflow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        
        # Use a generator to create a tf.data.Dataset
        def generator():
            for i in range(len(ox_dataset)):
                data = ox_dataset[i]
                
                # Handle different return types from OpenArchX dataset
                if isinstance(data, tuple) and len(data) == 2:
                    # Standard (input, target) format
                    features, target = data
                    
                    # Convert to numpy if needed
                    if isinstance(features, Tensor):
                        features = features.data
                    if isinstance(target, Tensor):
                        target = target.data
                        
                    yield features, target
                else:
                    # Generic handling for other formats
                    if isinstance(data, Tensor):
                        yield data.data
                    else:
                        yield data
        
        # Get the first element to determine shapes and types
        sample = ox_dataset[0]
        
        if isinstance(sample, tuple) and len(sample) == 2:
            features, target = sample
            feature_shape = features.shape if hasattr(features, 'shape') else None
            target_shape = target.shape if hasattr(target, 'shape') else None
            
            feature_dtype = tensor_dtype or tf.float32
            target_dtype = tensor_dtype or tf.float32
            
            return tf.data.Dataset.from_generator(
                generator,
                output_signature=(
                    tf.TensorSpec(shape=feature_shape, dtype=feature_dtype),
                    tf.TensorSpec(shape=target_shape, dtype=target_dtype)
                )
            )
        else:
            sample_shape = sample.shape if hasattr(sample, 'shape') else None
            sample_dtype = tensor_dtype or tf.float32
            
            return tf.data.Dataset.from_generator(
                generator,
                output_signature=tf.TensorSpec(shape=sample_shape, dtype=sample_dtype)
            )


class TensorFlowModelConverter:
    """Utility for converting TensorFlow models to OpenArchX architecture."""
    
    @staticmethod
    def convert_model(tf_model, framework_dependence=False):
        """
        Convert a TensorFlow/Keras model to an OpenArchX model.
        
        Args:
            tf_model: A TensorFlow/Keras model.
            framework_dependence: If True, the resulting model will still rely on TensorFlow
                                 for forward passes. If False, it will be converted to
                                 pure OpenArchX layers.
                                 
        Returns:
            An OpenArchX model.
        """
        # Check if tensorflow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
            
        import tensorflow as tf
        from ..nn.base import Layer, Model
        from ..nn.layers import Dense, Conv2D, MaxPool2D, Flatten, Dropout
        
        if framework_dependence:
            # Create a wrapper around the TensorFlow model
            class TensorFlowWrappedModel(Model):
                def __init__(self, tf_model):
                    super().__init__()
                    self.tf_model = tf_model
                    
                def forward(self, x):
                    # Convert OpenArchX Tensor to TensorFlow tensor
                    if isinstance(x, Tensor):
                        x_tf = tf.convert_to_tensor(x.data, dtype=tf.float32)
                    else:
                        x_tf = tf.convert_to_tensor(x, dtype=tf.float32)
                        
                    # Forward pass
                    output = self.tf_model(x_tf, training=False)
                        
                    # Convert back to OpenArchX Tensor
                    if isinstance(output, tf.Tensor):
                        return Tensor(output.numpy())
                    else:
                        return output
            
            return TensorFlowWrappedModel(tf_model)
            
        else:
            # Convert to pure OpenArchX model by translating each layer
            class OpenArchXModelFromTensorFlow(Model):
                def __init__(self, tf_model):
                    super().__init__()
                    self.layers = []
                    
                    # Convert each layer
                    for layer in tf_model.layers:
                        # Dense (Fully Connected) layer
                        if isinstance(layer, tf.keras.layers.Dense):
                            ox_layer = Dense(layer.units)
                            # Set weights and biases
                            weights, bias = layer.get_weights()
                            ox_layer.weights = Tensor(weights)
                            ox_layer.bias = Tensor(bias)
                            self.layers.append(ox_layer)
                            
                        # Convolutional layer
                        elif isinstance(layer, tf.keras.layers.Conv2D):
                            ox_layer = Conv2D(
                                filters=layer.filters,
                                kernel_size=layer.kernel_size,
                                strides=layer.strides,
                                padding='same' if layer.padding.lower() == 'same' else 'valid'
                            )
                            # Set weights and biases
                            weights, bias = layer.get_weights()
                            ox_layer.kernels = Tensor(weights)
                            ox_layer.bias = Tensor(bias)
                            self.layers.append(ox_layer)
                            
                        # MaxPooling layer
                        elif isinstance(layer, tf.keras.layers.MaxPool2D):
                            ox_layer = MaxPool2D(
                                pool_size=layer.pool_size,
                                strides=layer.strides,
                                padding='same' if layer.padding.lower() == 'same' else 'valid'
                            )
                            self.layers.append(ox_layer)
                            
                        # Flatten layer
                        elif isinstance(layer, tf.keras.layers.Flatten):
                            ox_layer = Flatten()
                            self.layers.append(ox_layer)
                            
                        # Dropout layer
                        elif isinstance(layer, tf.keras.layers.Dropout):
                            ox_layer = Dropout(rate=layer.rate)
                            self.layers.append(ox_layer)
                            
                        # Other layer types could be added as needed
                        else:
                            raise ValueError(f"Unsupported layer type: {type(layer).__name__}")
                    
                def forward(self, x):
                    for layer in self.layers:
                        x = layer(x)
                    return x
            
            return OpenArchXModelFromTensorFlow(tf_model)


class ModelWeightsExtractor:
    """Utility for extracting weights from TensorFlow models for use in OpenArchX."""
    
    @staticmethod
    def extract_transformer_weights(tf_model, layer_mapping=None):
        """
        Extract weights from a TensorFlow transformer model into a format usable by OpenArchX.
        
        Args:
            tf_model: A TensorFlow transformer model.
            layer_mapping: Optional dictionary mapping TensorFlow layer names to 
                          OpenArchX parameter names.
                          
        Returns:
            Dictionary mapping OpenArchX parameter names to weights as Tensors.
        """
        # Check if tensorflow is installed
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
        
        # Default mapping for common transformer architectures
        default_mapping = {
            'embeddings': 'embedding',
            'encoder': 'encoder',
            'decoder': 'decoder',
            'attention': 'attention',
            'dense': 'linear',
            'layer_norm': 'norm',
            'kernel': 'weight',
            'bias': 'bias'
        }
        
        mapping = default_mapping
        if layer_mapping:
            mapping.update(layer_mapping)
        
        result = {}
        
        # Process weights
        for weight in tf_model.weights:
            name = weight.name
            value = weight.numpy()
            
            # Transform the name according to the mapping
            transformed_name = name
            for tf_key, ox_key in mapping.items():
                transformed_name = transformed_name.replace(tf_key, ox_key)
                
            # Remove any TensorFlow-specific suffixes
            transformed_name = transformed_name.replace(':0', '')
            
            # Store the weight as a Tensor
            result[transformed_name] = Tensor(value)
            
        return result


# Convenience functions

def get_tensorflow_model_adapter(tf_model, device=None):
    """
    Helper function to get a TensorFlow model adapter.
    
    Args:
        tf_model: A TensorFlow/Keras model.
        device: The device to run the model on.
        
    Returns:
        A TensorFlowModelAdapter instance.
    """
    return TensorFlowModelAdapter(tf_model, device)


def convert_to_tensorflow_dataset(ox_dataset, tensor_dtype=None):
    """
    Convert an OpenArchX Dataset to a TensorFlow Dataset.
    
    Args:
        ox_dataset: An OpenArchX Dataset instance.
        tensor_dtype: Optional dtype for the TensorFlow tensors.
        
    Returns:
        A TensorFlow Dataset.
    """
    return TensorFlowDatasetConverter.from_openarchx_dataset(ox_dataset, tensor_dtype)


def convert_from_tensorflow_dataset(tf_dataset, transform=None):
    """
    Convert a TensorFlow Dataset to an OpenArchX Dataset.
    
    Args:
        tf_dataset: A TensorFlow Dataset instance.
        transform: Optional transform to apply to the data.
        
    Returns:
        An OpenArchX Dataset.
    """
    return TensorFlowDatasetConverter.to_openarchx_dataset(tf_dataset, transform)


def convert_tensorflow_model(tf_model, framework_dependence=False):
    """
    Convert a TensorFlow model to an OpenArchX model.
    
    Args:
        tf_model: A TensorFlow/Keras model.
        framework_dependence: If True, the resulting model will still rely on TensorFlow.
                             If False, it will be converted to pure OpenArchX layers.
                             
    Returns:
        An OpenArchX model.
    """
    return TensorFlowModelConverter.convert_model(tf_model, framework_dependence)


def extract_tensorflow_weights(tf_model):
    """
    Extract weights from a TensorFlow model.
    
    Args:
        tf_model: A TensorFlow model.
        
    Returns:
        Dictionary mapping parameter names to OpenArchX Tensors.
    """
    # Check if tensorflow is installed
    if importlib.util.find_spec("tensorflow") is None:
        raise ImportError("TensorFlow is required. Install with 'pip install tensorflow'")
        
    weights_dict = {}
    
    # Extract weights from the model
    for weight in tf_model.weights:
        name = weight.name.replace(':0', '')  # Remove TensorFlow-specific suffix
        weights_dict[name] = Tensor(weight.numpy())
        
    return weights_dict


def extract_transformer_weights(tf_model, layer_mapping=None):
    """
    Extract weights from a TensorFlow transformer model for use in OpenArchX.
    
    Args:
        tf_model: A TensorFlow transformer model.
        layer_mapping: Optional dictionary mapping TensorFlow layer names to OpenArchX names.
        
    Returns:
        Dictionary mapping OpenArchX parameter names to weights as Tensors.
    """
    return ModelWeightsExtractor.extract_transformer_weights(tf_model, layer_mapping) 