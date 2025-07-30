import numpy as np
from ..core.tensor import Tensor
from ..nn.module import Module
from .base import Linear

def get_positional_encoding(seq_length, d_model):
    """Generate positional encodings for transformer input"""
    position = np.arange(seq_length)[:, np.newaxis]
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
    
    pos_encoding = np.zeros((seq_length, d_model))
    pos_encoding[:, 0::2] = np.sin(position * div_term)
    pos_encoding[:, 1::2] = np.cos(position * div_term)
    
    return Tensor(pos_encoding[np.newaxis, :, :])  # Add batch dimension

class PositionalEncoding(Module):
    def __init__(self, d_model, max_seq_length=5000):
        super().__init__()
        self.pos_encoding = get_positional_encoding(max_seq_length, d_model)
    
    def forward(self, x):
        return x + self.pos_encoding[:, :x.data.shape[1], :]

class MultiHeadAttention(Module):
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        self.q_proj = Linear(embed_dim, embed_dim)
        self.k_proj = Linear(embed_dim, embed_dim)
        self.v_proj = Linear(embed_dim, embed_dim)
        self.out_proj = Linear(embed_dim, embed_dim)
    
    def split_heads(self, x, batch_size):
        # [batch_size, seq_len, embed_dim] -> [batch_size, seq_len, num_heads, head_dim]
        new_shape = (batch_size, -1, self.num_heads, self.head_dim)
        x = x.reshape(*new_shape)
        # [batch_size, seq_len, num_heads, head_dim] -> [batch_size, num_heads, seq_len, head_dim]
        return x.transpose(0, 2, 1, 3)
    
    def merge_heads(self, x, batch_size, seq_len):
        # [batch_size, num_heads, seq_len, head_dim] -> [batch_size, seq_len, num_heads, head_dim]
        x = x.transpose(0, 2, 1, 3)
        # [batch_size, seq_len, num_heads, head_dim] -> [batch_size, seq_len, embed_dim]
        return x.reshape(batch_size, seq_len, self.embed_dim)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.data.shape[0]
        q_len, k_len = query.data.shape[1], key.data.shape[1]
        
        # Linear projections and split heads
        q = self.split_heads(self.q_proj.forward(query), batch_size)  # [batch, heads, q_len, head_dim]
        k = self.split_heads(self.k_proj.forward(key), batch_size)    # [batch, heads, k_len, head_dim]
        v = self.split_heads(self.v_proj.forward(value), batch_size)  # [batch, heads, v_len, head_dim]
        
        # Scaled dot-product attention
        # [batch, heads, q_len, head_dim] @ [batch, heads, head_dim, k_len]
        scores = (q @ k.transpose(0, 1, 3, 2)) / np.sqrt(self.head_dim)
        
        if mask is not None:
            scores.data = scores.data + mask.data * -1e9
        
        # Apply softmax and attention
        attn = self._softmax(scores)  # [batch, heads, q_len, k_len]
        out = attn @ v  # [batch, heads, q_len, head_dim]
        
        # Merge heads and project
        out = self.merge_heads(out, batch_size, q_len)  # [batch, q_len, embed_dim]
        return self.out_proj.forward(out)
    
    def _softmax(self, x):
        exp_x = Tensor(np.exp(x.data - np.max(x.data, axis=-1, keepdims=True)))
        return exp_x / exp_x.sum(axis=-1, keepdims=True)

class LayerNorm(Module):
    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.gamma = Tensor(np.ones(normalized_shape), requires_grad=True)
        self.beta = Tensor(np.zeros(normalized_shape), requires_grad=True)
    
    def forward(self, x):
        mean = x.mean(axis=-1, keepdims=True)
        var = ((x - mean) ** 2).mean(axis=-1, keepdims=True)
        return self.gamma * (x - mean) / (var + self.eps).sqrt() + self.beta
    
    def parameters(self):
        return [self.gamma, self.beta]

class TransformerEncoderLayer(Module):
    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, nhead)
        self.pos_encoding = PositionalEncoding(d_model)
        self.linear1 = Linear(d_model, dim_feedforward)
        self.linear2 = Linear(dim_feedforward, d_model)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.dropout = dropout
    
    def forward(self, src, src_mask=None):
        # Add positional encoding
        src = self.pos_encoding.forward(src)
        
        # Multi-head self-attention
        attn_output = self.self_attn.forward(src, src, src, mask=src_mask)
        attn_output = self._dropout(attn_output)
        out1 = self.norm1.forward(src + attn_output)
        
        # Position-wise feed-forward network
        ff_output = self.linear1.forward(out1)
        ff_output = self._relu(ff_output)
        ff_output = self._dropout(ff_output)
        ff_output = self.linear2.forward(ff_output)
        ff_output = self._dropout(ff_output)
        
        return self.norm2.forward(out1 + ff_output)
    
    def _dropout(self, x):
        if self.dropout > 0:
            mask = np.random.binomial(1, 1-self.dropout, x.data.shape)
            return Tensor(x.data * mask / (1-self.dropout))
        return x
    
    def _relu(self, x):
        return Tensor(np.maximum(0, x.data))