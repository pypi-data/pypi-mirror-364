"""
Integration Example - How to use OpenArchX with other frameworks

This example demonstrates how to use OpenArchX with:
1. PyTorch datasets and models
2. TensorFlow/Keras datasets and models 
3. Hugging Face datasets and models
"""

import sys
import os
import numpy as np

# Add the parent directory to the path to import openarchx directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openarchx.core.tensor import Tensor
from openarchx.utils.data import DatasetFactory, DataLoader
from openarchx.utils.transforms import ToTensor, Normalize, Compose, TransformFactory
from openarchx.nn.model import Model
from openarchx.layers import Dense, ReLU

# =====================================================================
# Part 1: Using PyTorch datasets with OpenArchX
# =====================================================================

def pytorch_integration_example():
    """Example of using PyTorch datasets with OpenArchX."""
    print("\n=== PyTorch Integration Example ===")
    
    try:
        import torch
        from torch.utils.data import Dataset as TorchDataset
        from torchvision import datasets, transforms
        
        # Create a PyTorch MNIST dataset
        torch_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        torch_dataset = datasets.MNIST('./data', train=True, download=True,
                                 transform=torch_transform)
        
        # Convert to OpenArchX dataset
        openarchx_dataset = DatasetFactory.from_torch(torch_dataset)
        
        # Create OpenArchX DataLoader
        dataloader = DataLoader(openarchx_dataset, batch_size=32, shuffle=True)
        
        # Inspect a batch
        for inputs, targets in dataloader:
            print(f"Batch shape: {inputs.data.shape}")
            print(f"Targets shape: {targets.data.shape}")
            break
            
        # Create a simple model to process the data
        model = Model([
            Dense(784, 128),
            ReLU(),
            Dense(128, 10)
        ])
        
        # Process a batch with the model
        for inputs, targets in dataloader:
            # Reshape for dense layer
            batch_size = inputs.data.shape[0]
            inputs_flat = Tensor(inputs.data.reshape(batch_size, -1))
            
            # Forward pass
            outputs = model.forward(inputs_flat)
            print(f"Model output shape: {outputs.data.shape}")
            break
            
    except ImportError as e:
        print(f"PyTorch example skipped: {e}")


# =====================================================================
# Part 2: Using TensorFlow datasets with OpenArchX
# =====================================================================

def tensorflow_integration_example():
    """Example of using TensorFlow datasets with OpenArchX."""
    print("\n=== TensorFlow Integration Example ===")
    
    try:
        import tensorflow as tf
        from openarchx.utils.tensorflow import (
            get_tf_model_adapter, 
            convert_from_tf_dataset,
            convert_keras_model
        )
        
        # Create a TensorFlow dataset
        (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
        x_train = x_train / 255.0  # Normalize pixel values
        
        # Create one-hot encoded targets
        y_train_onehot = tf.one_hot(y_train, 10)
        
        # Create a TensorFlow dataset
        tf_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train_onehot))
        tf_dataset = tf_dataset.batch(32)
        
        # Convert to OpenArchX dataset
        openarchx_dataset = convert_from_tf_dataset(tf_dataset)
        
        # Create an OpenArchX DataLoader
        dataloader = DataLoader(openarchx_dataset, batch_size=32)
        
        # Inspect a batch
        for inputs, targets in dataloader:
            print(f"Batch shape: {inputs.data.shape}")
            print(f"Targets shape: {targets.data.shape}")
            break
            
        # Create a simple Keras model
        keras_model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        
        # Wrap the Keras model with the adapter
        model_adapter = get_tf_model_adapter(keras_model)
        
        # Process a batch with the wrapped model
        for inputs, targets in dataloader:
            outputs = model_adapter(inputs.data)
            print(f"Model output shape: {outputs.data.shape}")
            break
            
    except ImportError as e:
        print(f"TensorFlow example skipped: {e}")


# =====================================================================
# Part 3: Using Hugging Face datasets and models with OpenArchX
# =====================================================================

def huggingface_integration_example():
    """Example of using Hugging Face datasets and models with OpenArchX."""
    print("\n=== Hugging Face Integration Example ===")
    
    try:
        from openarchx.utils.huggingface import (
            get_huggingface_dataset,
            get_huggingface_model,
            get_huggingface_tokenizer
        )
        
        # Load a small text classification dataset
        hf_dataset_loader = get_huggingface_dataset('glue', 'sst2', split='train[:100]')
        
        # Convert to OpenArchX dataset
        openarchx_dataset = hf_dataset_loader.to_openarchx_dataset(
            input_cols='sentence', 
            target_col='label'
        )
        
        # Create a dataloader
        dataloader = DataLoader(openarchx_dataset, batch_size=8)
        
        # Inspect a batch
        for inputs, targets in dataloader:
            sample_texts = [str(x) for x in inputs.data[:2]]
            print(f"Sample texts: {sample_texts}")
            print(f"Targets: {targets.data[:2]}")
            break
            
        # Initialize a tokenizer
        tokenizer = get_huggingface_tokenizer('distilbert-base-uncased')
        
        # Initialize a pretrained model
        model = get_huggingface_model(
            'distilbert-base-uncased-finetuned-sst-2-english',
            task='text-classification'
        )
        
        # Process a sample with the model
        sample_text = "This movie is fantastic!"
        encoded_input = tokenizer(sample_text, return_tensors="np")
        output = model([sample_text])
        
        print(f"Model prediction shape: {output.data.shape}")
        print(f"Sentiment prediction: {'Positive' if np.argmax(output.data) == 1 else 'Negative'}")
        
    except ImportError as e:
        print(f"Hugging Face example skipped: {e}")


# =====================================================================
# Main function to run all examples
# =====================================================================

def main():
    print("OpenArchX Integration Examples")
    print("==============================")
    
    # Run PyTorch example
    pytorch_integration_example()
    
    # Run TensorFlow example
    tensorflow_integration_example()
    
    # Run Hugging Face example
    huggingface_integration_example()


if __name__ == "__main__":
    main() 