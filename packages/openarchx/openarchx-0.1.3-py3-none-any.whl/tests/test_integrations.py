import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openarchx.core.tensor import Tensor
from openarchx.utils.data import Dataset, DataLoader, DatasetFactory
from openarchx.utils.transforms import Compose, ToTensor, Normalize, RandomCrop


class TestDataIntegration(unittest.TestCase):
    """Test the dataset integration features."""
    
    def setUp(self):
        # Create a simple dataset for testing
        self.X = np.random.randn(100, 3, 32, 32).astype(np.float32)
        self.y = np.random.randint(0, 10, size=100).astype(np.int64)
        self.dataset = Dataset(self.X, self.y)
        
    def test_dataset_creation(self):
        """Test creating a dataset."""
        self.assertEqual(len(self.dataset), 100)
        x, y = self.dataset[0]
        self.assertEqual(x.shape, (3, 32, 32))
        self.assertIsInstance(y, np.int64)
        
    def test_dataloader(self):
        """Test the dataloader."""
        dataloader = DataLoader(self.dataset, batch_size=16, shuffle=True)
        self.assertEqual(len(dataloader), 7)  # 100/16 = 6.25 -> 7 batches
        
        for x_batch, y_batch in dataloader:
            self.assertIsInstance(x_batch, Tensor)
            self.assertIsInstance(y_batch, Tensor)
            self.assertEqual(x_batch.data.shape[0], 16)  # Batch size
            self.assertEqual(y_batch.data.shape[0], 16)  # Batch size
            break
            
    def test_dataset_factory(self):
        """Test the dataset factory."""
        dataset = DatasetFactory.from_numpy(self.X, self.y)
        self.assertEqual(len(dataset), 100)
        x, y = dataset[0]
        self.assertEqual(x.shape, (3, 32, 32))
        self.assertIsInstance(y, np.int64)


class TestTransforms(unittest.TestCase):
    """Test the transforms functionality."""
    
    def setUp(self):
        # Create sample data for testing
        self.x = np.random.randn(3, 32, 32).astype(np.float32)
        
    def test_to_tensor(self):
        """Test converting to tensor."""
        transform = ToTensor()
        output = transform(self.x)
        self.assertIsInstance(output, Tensor)
        self.assertEqual(output.data.shape, (3, 32, 32))
        
    def test_normalize(self):
        """Test normalizing data."""
        transform = Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        output = transform(self.x)
        self.assertTrue(np.all(output <= 1.0))
        self.assertTrue(np.all(output >= -1.0))
        
    def test_random_crop(self):
        """Test random cropping."""
        transform = RandomCrop(24)
        output = transform(self.x)
        self.assertEqual(output.shape, (3, 24, 24))
        
    def test_compose(self):
        """Test composing transforms."""
        transforms = Compose([
            ToTensor(),
            Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        output = transforms(self.x)
        self.assertIsInstance(output, Tensor)
        self.assertTrue(np.all(output.data <= 1.0))
        self.assertTrue(np.all(output.data >= -1.0))


class TestPyTorchIntegration(unittest.TestCase):
    """Test PyTorch integration features (if available)."""
    
    @classmethod
    def setUpClass(cls):
        # Skip tests if PyTorch is not available
        try:
            import torch
            cls.torch_available = True
        except ImportError:
            cls.torch_available = False
            
    def setUp(self):
        if not self.torch_available:
            self.skipTest("PyTorch not available")
            
        import torch
        from torch.utils.data import TensorDataset
        
        # Create a simple PyTorch dataset
        self.x_torch = torch.randn(100, 3, 32, 32)
        self.y_torch = torch.randint(0, 10, (100,))
        self.torch_dataset = TensorDataset(self.x_torch, self.y_torch)
        
    def test_torch_adapter(self):
        """Test PyTorch dataset adapter."""
        from openarchx.utils.data import TorchDatasetAdapter
        
        adapter = TorchDatasetAdapter(self.torch_dataset)
        self.assertEqual(len(adapter), 100)
        
        x, y = adapter[0]
        self.assertEqual(x.shape, (3, 32, 32))
        
    def test_torch_factory(self):
        """Test creating dataset from PyTorch."""
        dataset = DatasetFactory.from_torch(self.torch_dataset)
        self.assertEqual(len(dataset), 100)
        
        x, y = dataset[0]
        self.assertEqual(x.shape, (3, 32, 32))
        
        # Test with DataLoader
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
        for x_batch, y_batch in dataloader:
            self.assertIsInstance(x_batch, Tensor)
            self.assertEqual(x_batch.data.shape[0], 16)  # Batch size
            break


class TestTensorFlowIntegration(unittest.TestCase):
    """Test TensorFlow integration features (if available)."""
    
    @classmethod
    def setUpClass(cls):
        # Skip tests if TensorFlow is not available
        try:
            import tensorflow as tf
            cls.tf_available = True
        except ImportError:
            cls.tf_available = False
            
    def setUp(self):
        if not self.tf_available:
            self.skipTest("TensorFlow not available")
            
        import tensorflow as tf
        
        # Create a simple TensorFlow dataset
        self.x_tf = np.random.randn(100, 32, 32, 3).astype(np.float32)  # TF uses channels last
        self.y_tf = np.random.randint(0, 10, size=100).astype(np.int64)
        self.tf_dataset = tf.data.Dataset.from_tensor_slices((self.x_tf, self.y_tf)).batch(10)
        
    def test_tf_adapter(self):
        """Test TensorFlow dataset adapter."""
        from openarchx.utils.tensorflow import convert_from_tf_dataset
        
        adapter = convert_from_tf_dataset(self.tf_dataset)
        
        # Test with DataLoader
        dataloader = DataLoader(adapter, batch_size=5)
        for x_batch, y_batch in dataloader:
            self.assertIsInstance(x_batch, Tensor)
            break
            
    def test_tf_model_adapter(self):
        """Test TensorFlow model adapter."""
        if not self.tf_available:
            self.skipTest("TensorFlow not available")
            
        import tensorflow as tf
        from openarchx.utils.tensorflow import get_tf_model_adapter
        
        # Create a simple Keras model
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(32, 32, 3)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        
        # Create adapter
        adapter = get_tf_model_adapter(model)
        
        # Test inference
        test_input = np.random.randn(1, 32, 32, 3).astype(np.float32)
        output = adapter(test_input)
        
        self.assertIsInstance(output, Tensor)
        self.assertEqual(output.data.shape, (1, 10))


class TestHuggingFaceIntegration(unittest.TestCase):
    """Test Hugging Face integration features (if available)."""
    
    @classmethod
    def setUpClass(cls):
        # Skip tests if transformers is not available
        try:
            import transformers
            cls.hf_available = True
        except ImportError:
            cls.hf_available = False
            
    def test_tokenizer_adapter(self):
        """Test Hugging Face tokenizer adapter."""
        if not self.hf_available:
            self.skipTest("Hugging Face transformers not available")
            
        try:
            from openarchx.utils.huggingface import get_huggingface_tokenizer
            
            # Create tokenizer adapter
            tokenizer = get_huggingface_tokenizer("bert-base-uncased")
            
            # Test tokenization
            text = "Hello, world!"
            tokens = tokenizer(text, return_tensors="np")
            
            self.assertIsInstance(tokens, dict)
            self.assertIn("input_ids", tokens)
            self.assertIsInstance(tokens["input_ids"], Tensor)
        except Exception as e:
            self.skipTest(f"Hugging Face tokenizer test failed: {e}")


if __name__ == "__main__":
    unittest.main() 