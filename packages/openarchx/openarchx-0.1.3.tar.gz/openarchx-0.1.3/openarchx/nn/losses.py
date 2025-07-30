import numpy as np
from ..core.tensor import Tensor
from .module import Module

class MSELoss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        loss = (pred - target) ** 2
        if self.reduction == 'mean':
            return Tensor(np.mean(loss.data), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss.data), requires_grad=True)
        return loss

class CrossEntropyLoss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        # Apply log softmax
        max_val = np.max(pred.data, axis=1, keepdims=True)
        exp_x = np.exp(pred.data - max_val)
        softmax = exp_x / np.sum(exp_x, axis=1, keepdims=True)
        log_softmax = np.log(softmax + 1e-10)
        
        # Compute cross entropy
        batch_size = pred.data.shape[0]
        loss = -np.sum(target.data * log_softmax) / batch_size if self.reduction == 'mean' \
               else -np.sum(target.data * log_softmax)
        
        return Tensor(loss, requires_grad=True)

class BCELoss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        eps = 1e-12
        loss = -(target.data * np.log(pred.data + eps) + (1 - target.data) * np.log(1 - pred.data + eps))
        
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)

class BCEWithLogitsLoss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        # Compute sigmoid and BCE in a numerically stable way
        max_val = np.maximum(0, pred.data)
        loss = pred.data - pred.data * target.data + max_val + \
               np.log(np.exp(-max_val) + np.exp(pred.data - max_val))
        
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)

class L1Loss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        loss = np.abs(pred.data - target.data)
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)

class SmoothL1Loss(Module):
    def __init__(self, reduction='mean', beta=1.0):
        super().__init__()
        self.reduction = reduction
        self.beta = beta

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        diff = np.abs(pred.data - target.data)
        loss = np.where(diff < self.beta, 0.5 * diff ** 2 / self.beta, diff - 0.5 * self.beta)
        
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)

class KLDivLoss(Module):
    def __init__(self, reduction='mean', log_target=False):
        super().__init__()
        self.reduction = reduction
        self.log_target = log_target

    def forward(self, pred, target):
        if not isinstance(target, Tensor):
            target = Tensor(target, requires_grad=False)
        
        if self.log_target:
            loss = np.exp(target.data) * (target.data - pred.data)
        else:
            loss = target.data * (np.log(target.data + 1e-10) - pred.data)
        
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)

class CosineEmbeddingLoss(Module):
    def __init__(self, margin=0.0, reduction='mean'):
        super().__init__()
        self.margin = margin
        self.reduction = reduction

    def forward(self, x1, x2, y):
        if not isinstance(y, Tensor):
            y = Tensor(y, requires_grad=False)
        
        cos_sim = np.sum(x1.data * x2.data, axis=1) / \
                 (np.sqrt(np.sum(x1.data ** 2, axis=1)) * np.sqrt(np.sum(x2.data ** 2, axis=1)) + 1e-10)
        
        loss = np.where(y.data == 1, 1 - cos_sim, np.maximum(0, cos_sim - self.margin))
        
        if self.reduction == 'mean':
            return Tensor(np.mean(loss), requires_grad=True)
        elif self.reduction == 'sum':
            return Tensor(np.sum(loss), requires_grad=True)
        return Tensor(loss, requires_grad=True)