"""
Hugging Face Integration Utilities for OpenArchX.

This module provides conversion and adapter utilities for using Hugging Face models
and datasets with OpenArchX. These utilities are completely optional and do not 
affect OpenArchX's core functionality, which remains independent from external libraries.
"""

import numpy as np
import importlib.util
from ..core.tensor import Tensor


class HuggingFaceModelAdapter:
    """Adapter for using Hugging Face models with OpenArchX."""
    
    def __init__(self, model_name_or_path, task="text-classification", **model_kwargs):
        """
        Initialize a Hugging Face model adapter.
        
        Args:
            model_name_or_path: Name or path of the pretrained model.
            task: The task the model should perform (e.g., "text-classification", "token-classification").
            **model_kwargs: Additional arguments to pass to the model constructor.
        """
        # Check if transformers is installed
        if importlib.util.find_spec("transformers") is None:
            raise ImportError("Hugging Face transformers library is required. Install with 'pip install transformers'")
            
        from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer
        
        self.task = task
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        # Load appropriate model for the task
        if task == "text-classification" or task == "sequence-classification":
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, **model_kwargs)
        elif task == "feature-extraction" or task == "embeddings":
            self.model = AutoModel.from_pretrained(model_name_or_path, **model_kwargs)
        else:
            # For other tasks, try generic loading
            from transformers import AutoModelForPreTraining
            self.model = AutoModelForPreTraining.from_pretrained(model_name_or_path, **model_kwargs)
            
    def __call__(self, texts, **kwargs):
        """
        Process text through the model.
        
        Args:
            texts: Input text or list of texts.
            **kwargs: Additional arguments to pass to the tokenizer.
            
        Returns:
            OpenArchX Tensor containing the model output.
        """
        # Prepare inputs
        if isinstance(texts, str):
            texts = [texts]
            
        # Tokenize
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, **kwargs)
        
        # Get model output
        with torch_no_grad():
            outputs = self.model(**inputs)
            
        # Process outputs based on task
        if self.task == "text-classification" or self.task == "sequence-classification":
            # Get logits
            result = outputs.logits.detach().cpu().numpy()
        elif self.task == "feature-extraction" or self.task == "embeddings":
            # Get last hidden state (embeddings)
            result = outputs.last_hidden_state.detach().cpu().numpy()
        else:
            # Default to returning all outputs as a dict of numpy arrays
            result = {k: v.detach().cpu().numpy() for k, v in outputs.items() if hasattr(v, 'detach')}
            
        # Convert to Tensor
        if isinstance(result, dict):
            return {k: Tensor(v) for k, v in result.items()}
        return Tensor(result)


class HuggingFaceDatasetLoader:
    """Loader for Hugging Face datasets."""
    
    def __init__(self, dataset_name=None, dataset_path=None, split="train", **dataset_kwargs):
        """
        Initialize a Hugging Face dataset loader.
        
        Args:
            dataset_name: Name of the dataset in the Hugging Face Hub.
            dataset_path: Path to a local dataset.
            split: Dataset split to use ("train", "validation", "test").
            **dataset_kwargs: Additional arguments to pass to the dataset loader.
        """
        # Check if datasets is installed
        if importlib.util.find_spec("datasets") is None:
            raise ImportError("Hugging Face datasets library is required. Install with 'pip install datasets'")
            
        from datasets import load_dataset
        
        if dataset_name is None and dataset_path is None:
            raise ValueError("Either dataset_name or dataset_path must be provided")
            
        # Load dataset
        if dataset_path is not None:
            self.dataset = load_dataset(dataset_path, split=split, **dataset_kwargs)
        else:
            self.dataset = load_dataset(dataset_name, split=split, **dataset_kwargs)
    
    def to_openarchx_dataset(self, input_cols=None, target_col=None, transform=None):
        """
        Convert the Hugging Face dataset to an OpenArchX Dataset.
        
        Args:
            input_cols: Column(s) to use as input features.
            target_col: Column to use as target.
            transform: Transform to apply to the input features.
            
        Returns:
            An OpenArchX Dataset.
        """
        from .data import HuggingFaceDatasetAdapter
        return HuggingFaceDatasetAdapter(self.dataset, input_cols, target_col, transform)


def torch_no_grad():
    """Context manager to disable gradient calculation in PyTorch."""
    try:
        import torch
        return torch.no_grad()
    except ImportError:
        # Fallback for when torch is not available
        from contextlib import contextmanager
        
        @contextmanager
        def dummy_context():
            yield
            
        return dummy_context()


class HuggingFaceTokenizerAdapter:
    """Adapter for using Hugging Face tokenizers with OpenArchX."""
    
    def __init__(self, tokenizer_name_or_path, **tokenizer_kwargs):
        """
        Initialize a Hugging Face tokenizer adapter.
        
        Args:
            tokenizer_name_or_path: Name or path of the pretrained tokenizer.
            **tokenizer_kwargs: Additional arguments to pass to the tokenizer constructor.
        """
        # Check if transformers is installed
        if importlib.util.find_spec("transformers") is None:
            raise ImportError("Hugging Face transformers library is required. Install with 'pip install transformers'")
            
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, **tokenizer_kwargs)
        
    def __call__(self, texts, return_tensors="np", **kwargs):
        """
        Tokenize texts.
        
        Args:
            texts: Input text or list of texts.
            return_tensors: Output tensor format ("np" for numpy, "pt" for PyTorch, "tf" for TensorFlow).
            **kwargs: Additional arguments to pass to the tokenizer.
            
        Returns:
            Tokenized inputs, converted to OpenArchX Tensors if return_tensors="np".
        """
        # Call the tokenizer
        outputs = self.tokenizer(texts, return_tensors=return_tensors, **kwargs)
        
        # Convert to OpenArchX Tensors if requested
        if return_tensors == "np":
            return {k: Tensor(v) if isinstance(v, np.ndarray) else v for k, v in outputs.items()}
        return outputs


class ModelWeightsExtractor:
    """Utility to extract weights from a Hugging Face model into native OpenArchX format."""
    
    @staticmethod
    def extract_transformer_weights(hf_model, layer_mapping=None):
        """
        Extract weights from a Hugging Face transformer model into a format
        usable by OpenArchX native models.
        
        Args:
            hf_model: A Hugging Face transformer model
            layer_mapping: Optional dictionary mapping HF layer names to OpenArchX layer names
            
        Returns:
            Dictionary of weights that can be loaded into a native OpenArchX model
        """
        # Default layer mapping if none provided
        if layer_mapping is None:
            layer_mapping = {
                "embeddings": "embeddings",
                "attention": "attention",
                "intermediate": "intermediate",
                "output": "output",
                "layernorm": "layer_norm",
            }
            
        # Get state dict from HF model
        state_dict = hf_model.state_dict()
        
        # Convert to numpy arrays
        numpy_weights = {k: v.detach().cpu().numpy() for k, v in state_dict.items()}
        
        # Transform to OpenArchX format based on mapping
        openarchx_weights = {}
        
        for hf_name, param in numpy_weights.items():
            # Map the parameter name to OpenArchX format
            openarchx_name = hf_name
            for hf_pattern, ox_pattern in layer_mapping.items():
                if hf_pattern in hf_name:
                    openarchx_name = hf_name.replace(hf_pattern, ox_pattern)
                    break
                    
            openarchx_weights[openarchx_name] = Tensor(param)
            
        return openarchx_weights


# Convenience functions

def get_huggingface_model(model_name, task="text-classification", **kwargs):
    """
    Helper function to get a Hugging Face model adapter.
    
    Args:
        model_name: Name or path of the pretrained model.
        task: The task the model should perform.
        **kwargs: Additional arguments to pass to the model constructor.
        
    Returns:
        A HuggingFaceModelAdapter instance.
    """
    return HuggingFaceModelAdapter(model_name, task=task, **kwargs)


def get_huggingface_dataset(dataset_name=None, dataset_path=None, **kwargs):
    """
    Helper function to get a Hugging Face dataset loader.
    
    Args:
        dataset_name: Name of the dataset in the Hugging Face Hub.
        dataset_path: Path to a local dataset.
        **kwargs: Additional arguments to pass to the dataset loader.
        
    Returns:
        A HuggingFaceDatasetLoader instance.
    """
    return HuggingFaceDatasetLoader(dataset_name=dataset_name, dataset_path=dataset_path, **kwargs)


def get_huggingface_tokenizer(tokenizer_name, **kwargs):
    """
    Helper function to get a Hugging Face tokenizer adapter.
    
    Args:
        tokenizer_name: Name or path of the pretrained tokenizer.
        **kwargs: Additional arguments to pass to the tokenizer constructor.
        
    Returns:
        A HuggingFaceTokenizerAdapter instance.
    """
    return HuggingFaceTokenizerAdapter(tokenizer_name, **kwargs)


def extract_model_weights(hf_model, layer_mapping=None):
    """
    Extract weights from a Hugging Face model for use in a native OpenArchX model.
    
    Args:
        hf_model: A Hugging Face model
        layer_mapping: Optional mapping between HF and OpenArchX layer names
        
    Returns:
        Dictionary of weights compatible with OpenArchX models
    """
    return ModelWeightsExtractor.extract_transformer_weights(hf_model, layer_mapping) 