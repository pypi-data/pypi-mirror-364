import numpy as np
import traceback
import sys
from typing import Dict, List, Any, Optional, Tuple
import inspect
import re

class ErrorKnowledgeBase:
    """Knowledge base of common errors and their solutions"""
    
    def __init__(self):
        self.error_patterns = {
            'shape_mismatch': {
                'patterns': [
                    r'shapes? .* and .* not aligned',
                    r'cannot broadcast',
                    r'dimension mismatch',
                    r'incompatible dimensions'
                ],
                'solutions': [
                    "Check tensor shapes using .shape attribute",
                    "Use reshape() or transpose() to fix dimensions",
                    "Verify matrix multiplication dimensions: (m,k) @ (k,n) = (m,n)",
                    "Consider using broadcasting rules for element-wise operations"
                ]
            },
            'gradient_issues': {
                'patterns': [
                    r'gradient.*None',
                    r'no gradient',
                    r'requires_grad.*False'
                ],
                'solutions': [
                    "Set requires_grad=True for tensors that need gradients",
                    "Check if all operations in the computation graph support gradients",
                    "Verify that loss.backward() is called",
                    "Ensure parameters are properly registered in the model"
                ]
            },
            'memory_issues': {
                'patterns': [
                    r'out of memory',
                    r'memory.*allocation',
                    r'cannot allocate'
                ],
                'solutions': [
                    "Reduce batch size to use less memory",
                    "Use gradient accumulation for effective larger batches",
                    "Enable memory optimization with MemoryOptimizedTensor",
                    "Clear unused variables with del or use context managers"
                ]
            },
            'type_errors': {
                'patterns': [
                    r'unsupported operand type',
                    r'cannot convert',
                    r'invalid dtype'
                ],
                'solutions': [
                    "Ensure all tensors have compatible dtypes",
                    "Use .astype() to convert tensor dtypes",
                    "Check if mixing Tensor and numpy arrays",
                    "Verify tensor creation with correct dtype parameter"
                ]
            }
        }
    
    def find_solutions(self, error_message: str) -> List[str]:
        """Find solutions for a given error message"""
        solutions = []
        error_lower = error_message.lower()
        
        for error_type, info in self.error_patterns.items():
            for pattern in info['patterns']:
                if re.search(pattern, error_lower):
                    solutions.extend(info['solutions'])
                    break
        
        return list(set(solutions))  # Remove duplicates


class SuggestionEngine:
    """Generate contextual suggestions for fixing errors"""
    
    def __init__(self):
        self.knowledge_base = ErrorKnowledgeBase()
    
    def suggest_fix(self, error_type: str, context: Dict[str, Any]) -> List[str]:
        """Generate specific suggestions based on error type and context"""
        suggestions = []
        
        if error_type == 'shape_mismatch':
            suggestions.extend(self._suggest_shape_fixes(context))
        elif error_type == 'gradient_issue':
            suggestions.extend(self._suggest_gradient_fixes(context))
        elif error_type == 'memory_issue':
            suggestions.extend(self._suggest_memory_fixes(context))
        elif error_type == 'type_error':
            suggestions.extend(self._suggest_type_fixes(context))
        
        # Add general solutions from knowledge base
        if 'error_message' in context:
            general_solutions = self.knowledge_base.find_solutions(context['error_message'])
            suggestions.extend(general_solutions)
        
        return suggestions
    
    def _suggest_shape_fixes(self, context: Dict[str, Any]) -> List[str]:
        """Suggest fixes for shape mismatch errors"""
        suggestions = []
        
        if 'expected_shape' in context and 'actual_shape' in context:
            expected = context['expected_shape']
            actual = context['actual_shape']
            
            if len(expected) != len(actual):
                suggestions.append(f"Reshape tensor from {actual} to {expected} using .reshape({expected})")
            else:
                # Check for transpose
                if len(expected) == 2 and expected == actual[::-1]:
                    suggestions.append("Try transposing the tensor using .transpose() or .T")
                
                # Check for dimension expansion/squeeze
                if 1 in actual and 1 not in expected:
                    suggestions.append("Remove singleton dimensions using .squeeze()")
                elif 1 in expected and 1 not in actual:
                    suggestions.append("Add singleton dimension using .unsqueeze() or .reshape()")
        
        if 'operation' in context:
            op = context['operation']
            if 'matmul' in op or '@' in op:
                suggestions.append("For matrix multiplication A @ B, ensure A.shape[-1] == B.shape[-2]")
            elif 'conv' in op:
                suggestions.append("Check convolution input shape: (batch, channels, height, width)")
        
        return suggestions
    
    def _suggest_gradient_fixes(self, context: Dict[str, Any]) -> List[str]:
        """Suggest fixes for gradient-related errors"""
        suggestions = [
            "Ensure tensor.requires_grad = True for parameters that need gradients",
            "Call loss.backward() to compute gradients",
            "Check if all operations in the forward pass support gradients"
        ]
        
        if 'tensor_info' in context:
            info = context['tensor_info']
            if not info.get('requires_grad', False):
                suggestions.insert(0, "Set requires_grad=True for this tensor")
        
        return suggestions
    
    def _suggest_memory_fixes(self, context: Dict[str, Any]) -> List[str]:
        """Suggest fixes for memory-related errors"""
        suggestions = [
            "Reduce batch size to use less memory",
            "Use MemoryOptimizedTensor for automatic memory management",
            "Enable gradient checkpointing for large models",
            "Clear intermediate variables with 'del variable_name'"
        ]
        
        if 'memory_usage' in context:
            usage = context['memory_usage']
            if usage > 1e9:  # > 1GB
                suggestions.insert(0, f"High memory usage detected ({usage/1e9:.1f}GB). Consider reducing model size or batch size")
        
        return suggestions
    
    def _suggest_type_fixes(self, context: Dict[str, Any]) -> List[str]:
        """Suggest fixes for type-related errors"""
        suggestions = [
            "Ensure all tensors have compatible dtypes (float32, float64, etc.)",
            "Use tensor.astype(dtype) to convert tensor types",
            "Check if mixing Tensor objects with numpy arrays"
        ]
        
        if 'expected_type' in context and 'actual_type' in context:
            expected = context['expected_type']
            actual = context['actual_type']
            suggestions.insert(0, f"Convert from {actual} to {expected} using .astype({expected})")
        
        return suggestions


class VisualDebugger:
    """Create visual representations of errors and tensor operations"""
    
    def visualize_shape_mismatch(self, expected_shape: Tuple, actual_shape: Tuple, 
                               operation: str = "") -> str:
        """Create visual representation of shape mismatch"""
        visual = "\n" + "="*60 + "\n"
        visual += "SHAPE MISMATCH VISUALIZATION\n"
        visual += "="*60 + "\n"
        
        if operation:
            visual += f"Operation: {operation}\n\n"
        
        visual += f"Expected shape: {expected_shape}\n"
        visual += f"Actual shape:   {actual_shape}\n\n"
        
        # Create visual representation
        visual += "Visual comparison:\n"
        visual += f"Expected: {self._shape_to_visual(expected_shape)}\n"
        visual += f"Actual:   {self._shape_to_visual(actual_shape)}\n\n"
        
        # Highlight differences
        differences = []
        max_len = max(len(expected_shape), len(actual_shape))
        
        for i in range(max_len):
            exp_dim = expected_shape[i] if i < len(expected_shape) else "missing"
            act_dim = actual_shape[i] if i < len(actual_shape) else "missing"
            
            if exp_dim != act_dim:
                differences.append(f"Dimension {i}: expected {exp_dim}, got {act_dim}")
        
        if differences:
            visual += "Differences:\n"
            for diff in differences:
                visual += f"  • {diff}\n"
        
        visual += "="*60 + "\n"
        return visual
    
    def _shape_to_visual(self, shape: Tuple) -> str:
        """Convert shape tuple to visual representation"""
        if not shape:
            return "scalar ()"
        
        visual = ""
        for i, dim in enumerate(shape):
            if i == 0:
                visual += "["
            visual += str(dim)
            if i < len(shape) - 1:
                visual += " × "
            if i == len(shape) - 1:
                visual += "]"
        
        return visual
    
    def visualize_tensor_operation(self, tensors: List[Any], operation: str) -> str:
        """Visualize tensor operation with shapes and types"""
        visual = "\n" + "="*60 + "\n"
        visual += f"TENSOR OPERATION: {operation.upper()}\n"
        visual += "="*60 + "\n"
        
        for i, tensor in enumerate(tensors):
            if hasattr(tensor, 'shape') and hasattr(tensor, 'dtype'):
                visual += f"Tensor {i+1}: shape={tensor.shape}, dtype={tensor.dtype}\n"
            elif hasattr(tensor, 'shape'):
                visual += f"Tensor {i+1}: shape={tensor.shape}\n"
            else:
                visual += f"Tensor {i+1}: {type(tensor)}\n"
        
        visual += "="*60 + "\n"
        return visual


class ContextualErrorHandler:
    """Superior error handler with context and visual debugging"""
    
    def __init__(self):
        self.suggestion_engine = SuggestionEngine()
        self.visual_debugger = VisualDebugger()
        self.error_history = []
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Handle error with contextual information and suggestions"""
        if context is None:
            context = self._extract_context_from_traceback()
        
        error_type = self._classify_error(error)
        error_message = str(error)
        
        # Build comprehensive error report
        report = self._build_error_report(error, error_type, error_message, context)
        
        # Store in history for pattern analysis
        self.error_history.append({
            'error_type': error_type,
            'message': error_message,
            'context': context,
            'timestamp': __import__('time').time()
        })
        
        return report
    
    def handle_shape_mismatch(self, expected: Tuple, actual: Tuple, operation: str = "") -> str:
        """Specialized handler for shape mismatch errors"""
        context = {
            'expected_shape': expected,
            'actual_shape': actual,
            'operation': operation,
            'error_type': 'shape_mismatch'
        }
        
        # Create visual representation
        visual = self.visual_debugger.visualize_shape_mismatch(expected, actual, operation)
        
        # Get suggestions
        suggestions = self.suggestion_engine.suggest_fix('shape_mismatch', context)
        
        # Build report
        report = visual + "\n"
        report += "SUGGESTED SOLUTIONS:\n"
        report += "-" * 20 + "\n"
        for i, suggestion in enumerate(suggestions, 1):
            report += f"{i}. {suggestion}\n"
        
        return report
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for targeted handling"""
        error_message = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        if 'shape' in error_message or 'dimension' in error_message or 'broadcast' in error_message:
            return 'shape_mismatch'
        elif 'gradient' in error_message or 'requires_grad' in error_message:
            return 'gradient_issue'
        elif 'memory' in error_message or 'allocation' in error_message:
            return 'memory_issue'
        elif 'type' in error_type_name or 'dtype' in error_message:
            return 'type_error'
        elif 'value' in error_type_name:
            return 'value_error'
        else:
            return 'general_error'
    
    def _extract_context_from_traceback(self) -> Dict[str, Any]:
        """Extract context information from current traceback"""
        context = {}
        
        try:
            # Get current frame information
            frame = inspect.currentframe()
            if frame and frame.f_back:
                frame_info = inspect.getframeinfo(frame.f_back)
                context['file'] = frame_info.filename
                context['line'] = frame_info.lineno
                context['function'] = frame_info.function
                
                # Get local variables that might be relevant
                local_vars = frame.f_back.f_locals
                tensor_vars = {}
                
                for name, value in local_vars.items():
                    if hasattr(value, 'shape') and hasattr(value, 'dtype'):
                        tensor_vars[name] = {
                            'shape': value.shape,
                            'dtype': str(value.dtype),
                            'requires_grad': getattr(value, 'requires_grad', False)
                        }
                
                if tensor_vars:
                    context['tensor_variables'] = tensor_vars
        
        except Exception:
            pass  # Ignore errors in context extraction
        
        return context
    
    def _build_error_report(self, error: Exception, error_type: str, 
                          error_message: str, context: Dict[str, Any]) -> str:
        """Build comprehensive error report"""
        report = "\n" + "🚨 " + "="*58 + " 🚨\n"
        report += "OPENARCHX ENHANCED ERROR REPORT\n"
        report += "="*60 + "\n\n"
        
        # Error summary
        report += f"Error Type: {type(error).__name__}\n"
        report += f"Classification: {error_type.replace('_', ' ').title()}\n"
        report += f"Message: {error_message}\n\n"
        
        # Context information
        if context:
            report += "CONTEXT INFORMATION:\n"
            report += "-" * 20 + "\n"
            
            if 'file' in context:
                report += f"File: {context['file']}\n"
            if 'line' in context:
                report += f"Line: {context['line']}\n"
            if 'function' in context:
                report += f"Function: {context['function']}\n"
            
            if 'tensor_variables' in context:
                report += "\nTensor Variables in Scope:\n"
                for name, info in context['tensor_variables'].items():
                    report += f"  {name}: shape={info['shape']}, dtype={info['dtype']}"
                    if info['requires_grad']:
                        report += ", requires_grad=True"
                    report += "\n"
            
            report += "\n"
        
        # Visual debugging for shape errors
        if error_type == 'shape_mismatch' and 'expected_shape' in context:
            visual = self.visual_debugger.visualize_shape_mismatch(
                context['expected_shape'], 
                context['actual_shape'],
                context.get('operation', '')
            )
            report += visual + "\n"
        
        # Suggestions
        suggestions = self.suggestion_engine.suggest_fix(error_type, 
                                                       {**context, 'error_message': error_message})
        if suggestions:
            report += "💡 SUGGESTED SOLUTIONS:\n"
            report += "-" * 20 + "\n"
            for i, suggestion in enumerate(suggestions[:5], 1):  # Limit to top 5
                report += f"{i}. {suggestion}\n"
            report += "\n"
        
        # Additional help
        report += "📚 ADDITIONAL HELP:\n"
        report += "-" * 20 + "\n"
        report += "• Check the OpenArchX documentation for more examples\n"
        report += "• Use tensor.shape to inspect tensor dimensions\n"
        report += "• Enable debug mode for more detailed error tracking\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Analyze error patterns from history"""
        patterns = {}
        for error in self.error_history:
            error_type = error['error_type']
            patterns[error_type] = patterns.get(error_type, 0) + 1
        return patterns
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on error history"""
        patterns = self.get_error_patterns()
        suggestions = []
        
        if patterns.get('shape_mismatch', 0) > 3:
            suggestions.append("Consider adding shape validation in your model's forward method")
        
        if patterns.get('memory_issue', 0) > 2:
            suggestions.append("Consider using MemoryOptimizedTensor for better memory management")
        
        if patterns.get('gradient_issue', 0) > 2:
            suggestions.append("Review your model's gradient flow and requires_grad settings")
        
        return suggestions


# Global error handler instance
_global_error_handler = ContextualErrorHandler()

def handle_error(error: Exception, context: Dict[str, Any] = None) -> str:
    """Global error handling function"""
    return _global_error_handler.handle_error(error, context)

def handle_shape_mismatch(expected: Tuple, actual: Tuple, operation: str = "") -> str:
    """Global shape mismatch handler"""
    return _global_error_handler.handle_shape_mismatch(expected, actual, operation)

def get_error_handler() -> ContextualErrorHandler:
    """Get the global error handler instance"""
    return _global_error_handler