import numpy as np
from ..core.tensor import Tensor
import importlib.util

class Dataset:
    """Base dataset class for OpenArchX framework."""
    
    def __init__(self, data=None, targets=None):
        self.data = data
        self.targets = targets
        self.length = len(data) if data is not None else 0
        
    def __getitem__(self, index):
        if self.data is None or self.targets is None:
            raise NotImplementedError("Dataset must implement __getitem__ or provide data and targets")
        return self.data[index], self.targets[index]
        
    def __len__(self):
        return self.length


class DataLoader:
    """DataLoader for iterating over a dataset in batches with optional shuffling."""
    
    def __init__(self, dataset, batch_size=32, shuffle=False, drop_last=False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.indices = np.arange(len(dataset))
        
    def __iter__(self):
        if self.shuffle:
            np.random.shuffle(self.indices)
        
        for start_idx in range(0, len(self.dataset), self.batch_size):
            batch_indices = self.indices[start_idx:start_idx + self.batch_size]
            
            if len(batch_indices) < self.batch_size and self.drop_last:
                continue
                
            batch = [self.dataset[i] for i in batch_indices]
            
            # Transpose the batch to get separate data and target batches
            batch_data, batch_targets = zip(*batch)
            
            # Convert to arrays
            batch_data = np.array(batch_data)
            batch_targets = np.array(batch_targets)
            
            # Convert to Tensors
            yield Tensor(batch_data), Tensor(batch_targets)
            
    def __len__(self):
        if self.drop_last:
            return len(self.dataset) // self.batch_size
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size


# ===== ADAPTERS FOR EXTERNAL FRAMEWORKS =====
# These are optional conversion utilities that don't affect core functionality

class TorchDatasetAdapter(Dataset):
    """Adapter for PyTorch datasets to OpenArchX framework."""
    
    def __init__(self, torch_dataset):
        """
        Args:
            torch_dataset: A PyTorch Dataset object
        """
        super().__init__()
        self.torch_dataset = torch_dataset
        self.length = len(torch_dataset)
        
    def __getitem__(self, index):
        data, target = self.torch_dataset[index]
        
        # Convert torch tensors to numpy arrays if needed
        if hasattr(data, 'numpy'):
            data = data.numpy()
        if hasattr(target, 'numpy'):
            target = target.numpy()
            
        return data, target
        
    def __len__(self):
        return self.length


class TFDatasetAdapter(Dataset):
    """Adapter for TensorFlow datasets to OpenArchX framework."""
    
    def __init__(self, tf_dataset, x_key='x', y_key='y'):
        """
        Args:
            tf_dataset: A TensorFlow Dataset object
            x_key: Key for input features in TF dataset elements
            y_key: Key for target values in TF dataset elements
        """
        super().__init__()
        self.tf_dataset = tf_dataset
        self.x_key = x_key
        self.y_key = y_key
        
        # Count samples (might be expensive for large datasets)
        try:
            self.length = tf_dataset.cardinality().numpy()
            if self.length < 0:  # If cardinality is unknown
                self.length = sum(1 for _ in tf_dataset)
        except:
            # Fallback method
            self.length = sum(1 for _ in tf_dataset)
        
        # Create iterator
        self.iterator = iter(tf_dataset)
        
    def __getitem__(self, index):
        # TensorFlow datasets don't support random indexing
        # This implementation will iterate to the requested index
        # Warning: This is inefficient for large indices or repeated access
        # Better to use batching through the DataLoader
        
        # Reset iterator if needed
        if index == 0 or not hasattr(self, 'current_index') or index < self.current_index:
            self.iterator = iter(self.tf_dataset)
            self.current_index = 0
            
        # Iterate until we reach the desired index
        while self.current_index < index:
            next(self.iterator)
            self.current_index += 1
            
        # Get the item at the current index
        item = next(self.iterator)
        self.current_index += 1
        
        # Extract features and target
        if isinstance(item, dict):
            data = item[self.x_key].numpy()
            target = item[self.y_key].numpy()
        else:
            data = item[0].numpy()
            target = item[1].numpy()
            
        return data, target
        
    def __len__(self):
        return self.length


class HuggingFaceDatasetAdapter(Dataset):
    """Adapter for Hugging Face datasets to OpenArchX framework."""
    
    def __init__(self, hf_dataset, input_cols=None, target_col=None, transform=None):
        """
        Args:
            hf_dataset: A Hugging Face Dataset object
            input_cols: Columns to use as input features
            target_col: Column to use as target
            transform: Optional transform to apply to inputs
        """
        super().__init__()
        self.hf_dataset = hf_dataset
        self.input_cols = input_cols
        self.target_col = target_col
        self.transform = transform
        self.length = len(hf_dataset)
        
    def __getitem__(self, index):
        item = self.hf_dataset[index]
        
        # Extract inputs
        if self.input_cols:
            if isinstance(self.input_cols, list):
                data = np.array([item[col] for col in self.input_cols])
            else:
                data = np.array(item[self.input_cols])
        else:
            # Default: use all columns except target as input
            data = np.array([v for k, v in item.items() if k != self.target_col])
            
        # Extract target
        if self.target_col:
            target = np.array(item[self.target_col])
        else:
            # Default behavior if no target specified
            target = np.zeros(1)  # For unsupervised learning
            
        # Apply transform if specified
        if self.transform:
            data = self.transform(data)
            
        return data, target
        
    def __len__(self):
        return self.length


class DatasetFactory:
    """Factory for creating datasets from various sources."""
    
    @staticmethod
    def from_numpy(data, targets):
        """Create a dataset from NumPy arrays."""
        return Dataset(data, targets)
    
    @staticmethod
    def from_torch(torch_dataset):
        """Create a dataset from a PyTorch dataset."""
        # Check if PyTorch is available
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required for this adapter. Please install it with 'pip install torch'")
        return TorchDatasetAdapter(torch_dataset)
    
    @staticmethod
    def from_tensorflow(tf_dataset, x_key='x', y_key='y'):
        """Create a dataset from a TensorFlow dataset."""
        # Check if TensorFlow is available
        if importlib.util.find_spec("tensorflow") is None:
            raise ImportError("TensorFlow is required for this adapter. Please install it with 'pip install tensorflow'")
        return TFDatasetAdapter(tf_dataset, x_key, y_key)
    
    @staticmethod
    def from_huggingface(hf_dataset, input_cols=None, target_col=None, transform=None):
        """Create a dataset from a Hugging Face dataset."""
        # Check if datasets is available
        if importlib.util.find_spec("datasets") is None:
            raise ImportError("Hugging Face datasets is required for this adapter. Please install it with 'pip install datasets'")
        return HuggingFaceDatasetAdapter(hf_dataset, input_cols, target_col, transform) 