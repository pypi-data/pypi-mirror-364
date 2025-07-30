import numpy as np
from ..core.tensor import Tensor
from .module import Module
from .layers import Linear, LayerNorm
from .activations import ReLU

class MultiheadAttention(Module):
    def __init__(self, embed_dim, num_heads, dropout=0.0, bias=True):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim, "embed_dim must be divisible by num_heads"
        
        self.q_proj = Linear(embed_dim, embed_dim, bias=bias)
        self.k_proj = Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = Linear(embed_dim, embed_dim, bias=bias)

    def forward(self, query, key, value, attn_mask=None, key_padding_mask=None):
        batch_size = query.data.shape[0]
        
        # Linear projections and reshape
        q = self._reshape_for_attention(self.q_proj(query))
        k = self._reshape_for_attention(self.k_proj(key))
        v = self._reshape_for_attention(self.v_proj(value))
        
        # Scaled dot-product attention
        scaling = float(self.head_dim) ** -0.5
        attn = np.matmul(q.data, k.data.transpose(0, 1, 3, 2)) * scaling
        
        if attn_mask is not None:
            attn = np.where(attn_mask, -np.inf, attn)
        
        attn = self._softmax(attn)
        
        if self.dropout > 0:
            attn = np.where(np.random.random(attn.shape) > self.dropout, attn, 0) / (1 - self.dropout)
        
        output = np.matmul(attn, v.data)
        output = output.transpose(0, 2, 1, 3).reshape(batch_size, -1, self.embed_dim)
        
        return self.out_proj(Tensor(output, requires_grad=True))

    def _reshape_for_attention(self, x):
        batch_size, seq_len, _ = x.data.shape
        return Tensor(
            x.data.reshape(batch_size, seq_len, self.num_heads, self.head_dim)
            .transpose(0, 2, 1, 3),
            requires_grad=True
        )

    def _softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

class TransformerEncoderLayer(Module):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.self_attn = MultiheadAttention(d_model, nhead, dropout=dropout)
        self.linear1 = Linear(d_model, dim_feedforward)
        self.linear2 = Linear(dim_feedforward, d_model)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.dropout = dropout
        self.activation = ReLU()

    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        # Self attention block
        src2 = self.self_attn(src, src, src, attn_mask=src_mask,
                             key_padding_mask=src_key_padding_mask)
        src = src + self._dropout_layer(src2)
        src = self.norm1(src)
        
        # Feedforward block
        src2 = self.linear2(self._dropout_layer(self.activation(self.linear1(src))))
        src = src + self._dropout_layer(src2)
        src = self.norm2(src)
        
        return src

    def _dropout_layer(self, x):
        if self.dropout > 0:
            mask = np.random.random(x.data.shape) > self.dropout
            return Tensor(mask * x.data / (1 - self.dropout), requires_grad=True)
        return x

class TransformerDecoderLayer(Module):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.self_attn = MultiheadAttention(d_model, nhead, dropout=dropout)
        self.multihead_attn = MultiheadAttention(d_model, nhead, dropout=dropout)
        self.linear1 = Linear(d_model, dim_feedforward)
        self.linear2 = Linear(dim_feedforward, d_model)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.norm3 = LayerNorm(d_model)
        self.dropout = dropout
        self.activation = ReLU()

    def forward(self, tgt, memory, tgt_mask=None, memory_mask=None,
                tgt_key_padding_mask=None, memory_key_padding_mask=None):
        # Self attention block
        tgt2 = self.self_attn(tgt, tgt, tgt, attn_mask=tgt_mask,
                             key_padding_mask=tgt_key_padding_mask)
        tgt = tgt + self._dropout_layer(tgt2)
        tgt = self.norm1(tgt)
        
        # Cross attention block
        tgt2 = self.multihead_attn(tgt, memory, memory, attn_mask=memory_mask,
                                  key_padding_mask=memory_key_padding_mask)
        tgt = tgt + self._dropout_layer(tgt2)
        tgt = self.norm2(tgt)
        
        # Feedforward block
        tgt2 = self.linear2(self._dropout_layer(self.activation(self.linear1(tgt))))
        tgt = tgt + self._dropout_layer(tgt2)
        tgt = self.norm3(tgt)
        
        return tgt

    def _dropout_layer(self, x):
        if self.dropout > 0:
            mask = np.random.random(x.data.shape) > self.dropout
            return Tensor(mask * x.data / (1 - self.dropout), requires_grad=True)
        return x

class TransformerEncoder(Module):
    def __init__(self, encoder_layer, num_layers, norm=None):
        super().__init__()
        self.layers = [encoder_layer for _ in range(num_layers)]
        self.norm = norm

    def forward(self, src, mask=None, src_key_padding_mask=None):
        output = src
        for layer in self.layers:
            output = layer(output, src_mask=mask, src_key_padding_mask=src_key_padding_mask)
        
        if self.norm is not None:
            output = self.norm(output)
        
        return output

class TransformerDecoder(Module):
    def __init__(self, decoder_layer, num_layers, norm=None):
        super().__init__()
        self.layers = [decoder_layer for _ in range(num_layers)]
        self.norm = norm

    def forward(self, tgt, memory, tgt_mask=None, memory_mask=None,
                tgt_key_padding_mask=None, memory_key_padding_mask=None):
        output = tgt
        for layer in self.layers:
            output = layer(output, memory, tgt_mask=tgt_mask, memory_mask=memory_mask,
                         tgt_key_padding_mask=tgt_key_padding_mask,
                         memory_key_padding_mask=memory_key_padding_mask)
        
        if self.norm is not None:
            output = self.norm(output)
        
        return output

class Transformer(Module):
    def __init__(self, d_model=512, nhead=8, num_encoder_layers=6,
                 num_decoder_layers=6, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        
        encoder_layer = TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)
        encoder_norm = LayerNorm(d_model)
        self.encoder = TransformerEncoder(encoder_layer, num_encoder_layers, encoder_norm)
        
        decoder_layer = TransformerDecoderLayer(d_model, nhead, dim_feedforward, dropout)
        decoder_norm = LayerNorm(d_model)
        self.decoder = TransformerDecoder(decoder_layer, num_decoder_layers, decoder_norm)
        
        self.d_model = d_model
        self.nhead = nhead

    def forward(self, src, tgt, src_mask=None, tgt_mask=None, memory_mask=None,
                src_key_padding_mask=None, tgt_key_padding_mask=None,
                memory_key_padding_mask=None):
        memory = self.encoder(src, mask=src_mask, src_key_padding_mask=src_key_padding_mask)
        output = self.decoder(tgt, memory, tgt_mask=tgt_mask, memory_mask=memory_mask,
                            tgt_key_padding_mask=tgt_key_padding_mask,
                            memory_key_padding_mask=memory_key_padding_mask)
        return output