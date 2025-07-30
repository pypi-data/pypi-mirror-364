import numpy as np
from ..core.tensor import Tensor
from .module import Module
from .layers import Linear

class RNNCell(Module):
    def __init__(self, input_size, hidden_size, bias=True, nonlinearity="tanh"):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.nonlinearity = nonlinearity

        self.ih = Linear(input_size, hidden_size, bias=bias)
        self.hh = Linear(hidden_size, hidden_size, bias=bias)

    def forward(self, x, h=None):
        if h is None:
            h = Tensor(np.zeros((x.data.shape[0], self.hidden_size)), requires_grad=True)
        
        hidden = self.ih(x) + self.hh(h)
        if self.nonlinearity == "tanh":
            hidden = Tensor(np.tanh(hidden.data), requires_grad=True)
        else:  # relu
            hidden = Tensor(np.maximum(0, hidden.data), requires_grad=True)
        return hidden

class LSTMCell(Module):
    def __init__(self, input_size, hidden_size, bias=True):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        self.ih = Linear(input_size, 4 * hidden_size, bias=bias)
        self.hh = Linear(hidden_size, 4 * hidden_size, bias=bias)

    def forward(self, x, state=None):
        if state is None:
            h = Tensor(np.zeros((x.data.shape[0], self.hidden_size)), requires_grad=True)
            c = Tensor(np.zeros((x.data.shape[0], self.hidden_size)), requires_grad=True)
        else:
            h, c = state

        gates = self.ih(x) + self.hh(h)
        
        # Split gates
        i, f, g, o = np.split(gates.data, 4, axis=1)
        
        # Apply activations
        i = 1 / (1 + np.exp(-i))  # input gate
        f = 1 / (1 + np.exp(-f))  # forget gate
        g = np.tanh(g)            # cell gate
        o = 1 / (1 + np.exp(-o))  # output gate
        
        # Update cell state
        c = Tensor(f * c.data + i * g, requires_grad=True)
        # Compute output
        h = Tensor(o * np.tanh(c.data), requires_grad=True)
        
        return h, c

class GRUCell(Module):
    def __init__(self, input_size, hidden_size, bias=True):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        self.ih = Linear(input_size, 3 * hidden_size, bias=bias)
        self.hh = Linear(hidden_size, 3 * hidden_size, bias=bias)

    def forward(self, x, h=None):
        if h is None:
            h = Tensor(np.zeros((x.data.shape[0], self.hidden_size)), requires_grad=True)
        
        gi = self.ih(x)
        gh = self.hh(h)
        
        # Split gates
        i_r, i_z, i_n = np.split(gi.data, 3, axis=1)
        h_r, h_z, h_n = np.split(gh.data, 3, axis=1)
        
        r = 1 / (1 + np.exp(-(i_r + h_r)))  # reset gate
        z = 1 / (1 + np.exp(-(i_z + h_z)))  # update gate
        n = np.tanh(i_n + r * h_n)          # new gate
        
        h = Tensor((1 - z) * n + z * h.data, requires_grad=True)
        return h

class RNN(Module):
    def __init__(self, input_size, hidden_size, num_layers=1, bias=True,
                 nonlinearity="tanh", bidirectional=False):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        self.cells = []
        for layer in range(num_layers):
            layer_input_size = input_size if layer == 0 else hidden_size * (2 if bidirectional else 1)
            self.cells.append(RNNCell(layer_input_size, hidden_size, bias, nonlinearity))
            if bidirectional:
                self.cells.append(RNNCell(layer_input_size, hidden_size, bias, nonlinearity))

    def forward(self, x, h=None):
        # Assuming x is of shape (batch, seq_len, input_size)
        seq_len = x.data.shape[1]
        batch_size = x.data.shape[0]
        num_directions = 2 if self.bidirectional else 1
        
        if h is None:
            h = [Tensor(np.zeros((batch_size, self.hidden_size)), requires_grad=True) 
                 for _ in range(self.num_layers * num_directions)]
        
        output = []
        for t in range(seq_len):
            x_t = Tensor(x.data[:, t, :], requires_grad=True)
            
            for layer in range(self.num_layers):
                idx = layer * num_directions
                h[idx] = self.cells[idx](x_t, h[idx])
                if self.bidirectional:
                    h[idx + 1] = self.cells[idx + 1](x_t, h[idx + 1])
                
                # Prepare input for next layer
                if self.bidirectional:
                    x_t = Tensor(np.concatenate([h[idx].data, h[idx + 1].data], axis=1), requires_grad=True)
                else:
                    x_t = h[idx]
            
            output.append(x_t.data)
        
        # Stack outputs along sequence dimension
        output = Tensor(np.stack(output, axis=1), requires_grad=True)
        return output, h

class LSTM(Module):
    def __init__(self, input_size, hidden_size, num_layers=1, bias=True, bidirectional=False):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        self.cells = []
        for layer in range(num_layers):
            layer_input_size = input_size if layer == 0 else hidden_size * (2 if bidirectional else 1)
            self.cells.append(LSTMCell(layer_input_size, hidden_size, bias))
            if bidirectional:
                self.cells.append(LSTMCell(layer_input_size, hidden_size, bias))

    def forward(self, x, state=None):
        seq_len = x.data.shape[1]
        batch_size = x.data.shape[0]
        num_directions = 2 if self.bidirectional else 1
        
        if state is None:
            h = [Tensor(np.zeros((batch_size, self.hidden_size)), requires_grad=True) 
                 for _ in range(self.num_layers * num_directions)]
            c = [Tensor(np.zeros((batch_size, self.hidden_size)), requires_grad=True) 
                 for _ in range(self.num_layers * num_directions)]
        else:
            h, c = state
        
        output = []
        for t in range(seq_len):
            x_t = Tensor(x.data[:, t, :], requires_grad=True)
            
            for layer in range(self.num_layers):
                idx = layer * num_directions
                h[idx], c[idx] = self.cells[idx](x_t, (h[idx], c[idx]))
                if self.bidirectional:
                    h[idx + 1], c[idx + 1] = self.cells[idx + 1](x_t, (h[idx + 1], c[idx + 1]))
                
                if self.bidirectional:
                    x_t = Tensor(np.concatenate([h[idx].data, h[idx + 1].data], axis=1), requires_grad=True)
                else:
                    x_t = h[idx]
            
            output.append(x_t.data)
        
        output = Tensor(np.stack(output, axis=1), requires_grad=True)
        return output, (h, c)

class GRU(Module):
    def __init__(self, input_size, hidden_size, num_layers=1, bias=True, bidirectional=False):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        self.cells = []
        for layer in range(num_layers):
            layer_input_size = input_size if layer == 0 else hidden_size * (2 if bidirectional else 1)
            self.cells.append(GRUCell(layer_input_size, hidden_size, bias))
            if bidirectional:
                self.cells.append(GRUCell(layer_input_size, hidden_size, bias))

    def forward(self, x, h=None):
        seq_len = x.data.shape[1]
        batch_size = x.data.shape[0]
        num_directions = 2 if self.bidirectional else 1
        
        if h is None:
            h = [Tensor(np.zeros((batch_size, self.hidden_size)), requires_grad=True) 
                 for _ in range(self.num_layers * num_directions)]
        
        output = []
        for t in range(seq_len):
            x_t = Tensor(x.data[:, t, :], requires_grad=True)
            
            for layer in range(self.num_layers):
                idx = layer * num_directions
                h[idx] = self.cells[idx](x_t, h[idx])
                if self.bidirectional:
                    h[idx + 1] = self.cells[idx + 1](x_t, h[idx + 1])
                
                if self.bidirectional:
                    x_t = Tensor(np.concatenate([h[idx].data, h[idx + 1].data], axis=1), requires_grad=True)
                else:
                    x_t = h[idx]
            
            output.append(x_t.data)
        
        output = Tensor(np.stack(output, axis=1), requires_grad=True)
        return output, h