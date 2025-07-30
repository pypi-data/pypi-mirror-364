import numpy as np
from ..core.tensor import Tensor
from .module import Module
from collections import OrderedDict

class Sequential(Module):
    def __init__(self, *args):
        super().__init__()
        self.modules = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                self.modules.extend(arg)
            elif isinstance(arg, dict):
                self.modules.extend(arg.values())
            else:
                self.modules.append(arg)

    def forward(self, x):
        for module in self.modules:
            x = module(x)
        return x

    def parameters(self):
        params = []
        for module in self.modules:
            params.extend(module.parameters())
        return params

class ModuleList(Module):
    def __init__(self, modules=None):
        super().__init__()
        self.modules = []
        if modules is not None:
            self.extend(modules)

    def __getitem__(self, idx):
        return self.modules[idx]

    def __setitem__(self, idx, module):
        self.modules[idx] = module

    def __len__(self):
        return len(self.modules)

    def append(self, module):
        self.modules.append(module)

    def extend(self, modules):
        if isinstance(modules, (list, tuple)):
            self.modules.extend(modules)
        else:
            self.modules.extend(list(modules))

    def parameters(self):
        params = []
        for module in self.modules:
            params.extend(module.parameters())
        return params

class ModuleDict(Module):
    def __init__(self, modules=None):
        super().__init__()
        self.modules = OrderedDict()
        if modules is not None:
            self.update(modules)

    def __getitem__(self, key):
        return self.modules[key]

    def __setitem__(self, key, module):
        self.modules[key] = module

    def __delitem__(self, key):
        del self.modules[key]

    def __len__(self):
        return len(self.modules)

    def __iter__(self):
        return iter(self.modules)

    def keys(self):
        return self.modules.keys()

    def items(self):
        return self.modules.items()

    def values(self):
        return self.modules.values()

    def update(self, modules):
        if isinstance(modules, dict):
            self.modules.update(modules)
        else:
            for key, module in modules:
                self.modules[key] = module

    def parameters(self):
        params = []
        for module in self.modules.values():
            params.extend(module.parameters())
        return params

class ParameterList(Module):
    def __init__(self, parameters=None):
        super().__init__()
        self.parameters_list = []
        if parameters is not None:
            self.extend(parameters)

    def __getitem__(self, idx):
        return self.parameters_list[idx]

    def __setitem__(self, idx, parameter):
        self.parameters_list[idx] = parameter

    def __len__(self):
        return len(self.parameters_list)

    def append(self, parameter):
        if not isinstance(parameter, Tensor):
            parameter = Tensor(parameter, requires_grad=True)
        self.parameters_list.append(parameter)

    def extend(self, parameters):
        for param in parameters:
            self.append(param)

    def parameters(self):
        return self.parameters_list

class ParameterDict(Module):
    def __init__(self, parameters=None):
        super().__init__()
        self.parameters_dict = OrderedDict()
        if parameters is not None:
            self.update(parameters)

    def __getitem__(self, key):
        return self.parameters_dict[key]

    def __setitem__(self, key, parameter):
        if not isinstance(parameter, Tensor):
            parameter = Tensor(parameter, requires_grad=True)
        self.parameters_dict[key] = parameter

    def __delitem__(self, key):
        del self.parameters_dict[key]

    def __len__(self):
        return len(self.parameters_dict)

    def __iter__(self):
        return iter(self.parameters_dict)

    def keys(self):
        return self.parameters_dict.keys()

    def items(self):
        return self.parameters_dict.items()

    def values(self):
        return self.parameters_dict.values()

    def update(self, parameters):
        if isinstance(parameters, dict):
            for key, param in parameters.items():
                self[key] = param
        else:
            for key, param in parameters:
                self[key] = param

    def parameters(self):
        return list(self.parameters_dict.values())