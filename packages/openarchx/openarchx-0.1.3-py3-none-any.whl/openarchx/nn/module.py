class Module:
    def __init__(self):
        self._parameters = []
        
    def parameters(self):
        params = []
        for attr in self.__dict__.values():
            if isinstance(attr, Module):
                params.extend(attr.parameters())
            elif hasattr(attr, 'parameters'):
                params.extend(attr.parameters())
        return params + self._parameters
    
    def forward(self, *args, **kwargs):
        raise NotImplementedError
        
    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)