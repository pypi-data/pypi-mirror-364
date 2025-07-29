import torch
from torch import nn
from torch.nn import functional as F

__all__ = ['MHA']

class MHA(nn.Module):
    """
    Given Q,K,V and mask (Optional), it returns the output of Multi Head Attention.
    Args:
        x : Input
        mask : Mask (Optional)
    Returns:
        output : Output of Multi Head Attention
    """
    def __init__(self,d_model,num_head,dropout=None):
        super().__init__()
        self.d_model=d_model
        self.num_head=num_head
        self.d_k=d_model//num_head
        self.q = nn.Linear(d_model,d_model)
        self.k = nn.Linear(d_model,d_model)
        self.v = nn.Linear(d_model,d_model)

        if dropout is not None:
            self.dropout = nn.Dropout(dropout)
        else:
            self.dropout = nn.Dropout(0)
        
        self.out = nn.Linear(d_model,d_model)

    def forward(self,x,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Multi Head Attention.
        Args:
            x : Input
            mask : Mask (Optional)
        Returns:
            output : Output of Multi Head Attention
        """ 
        B,seq_len,d_model = x.shape
        q = self.q(x)
        k = self.k(x)
        v = self.v(x)
        
        q = q.view(B,seq_len,self.num_head,self.d_k)
        k = k.view(B,seq_len,self.num_head,self.d_k)
        v = v.view(B,seq_len,self.num_head,self.d_k)

        q = q.transpose(1,2)
        k = k.transpose(1,2)
        v = v.transpose(1,2)

        output,attn_weights = self.scaled_dot_product_attention(q,k,v,mask)

        output = output.transpose(1,2)
        output = output.contiguous().view(B,seq_len,d_model)

        output = self.out(output)
        output = self.dropout(output)

        return output,attn_weights
    
    def scaled_dot_product_attention(self,q,k,v,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Scaled Dot Product Attention.
        Args:
            q : Query
            k : Key
            v : Value
            mask : Mask (Optional)
        Returns:
            output : Output of Scaled Dot Product Attention
        """
        d_k = q.size(-1)

        scores = q @ k.transpose(-2,-1) / torch.sqrt(torch.tensor(d_k))
        if mask is not None:
            scores = scores.masked_fill(mask==0,float('-inf'))

        attn_weights = F.softmax(scores,dim=-1)
        output = attn_weights @ v
        
        return output,attn_weights

class MQA(nn.Module):
    """
    Given Q,K,V and mask (Optional), it returns the output of Multi Query Attention.
    Args:
        x : Input
        mask : Mask (Optional)
    Returns:
        output : Output of Multi Query Attention
    """
    def __init__(self,d_model,num_head,dropout=None):
        super().__init__()
        self.d_model=d_model
        self.num_head=num_head
        self.d_k=d_model//num_head
        self.q = nn.Linear(d_model,d_model)
        self.k = nn.Linear(d_model,d_model)
        self.v = nn.Linear(d_model,d_model)

        if dropout is not None:
            self.dropout = nn.Dropout(dropout)
        else:
            self.dropout = nn.Dropout(0)
        
        self.out = nn.Linear(d_model,d_model)
    
    def forward(self,x,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Multi Query Attention.
        Args:
            x : Input
            mask : Mask (Optional)
        Returns:
            output : Output of Multi Query Attention
        """
        B,seq_len,d_model = x.shape
        q = self.q(x)
        k = self.k(x)
        v = self.v(x)
        
        q = q.view(B,seq_len,self.num_head,self.d_k)
        k = k.view(B,seq_len,self.num_head,self.d_k)
        v = v.view(B,seq_len,self.num_head,self.d_k)

        q = q.transpose(1,2)
        k = k.transpose(1,2)
        v = v.transpose(1,2)

        output,attn_weights = self.new_kv_attention(q,k,v,mask)

        output = output.transpose(1,2)
        output = output.contiguous().view(B,seq_len,d_model)

        output = self.out(output)
        output = self.dropout(output)

        return output,attn_weights

    def new_kv_attention(self,q,k,v,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of New KV Attention.
        Args:
            q : Query
            k : Key
            v : Value
            mask : Mask (Optional)
        Returns:
            output : Output of New KV Attention
        """
        d_k = q.size(-1)
        
        scores = (q@k.transpose(-2,-1))/torch.sqrt(torch.tensor(d_k))
        
        if mask is not None:
            scores = scores.masked_fill(mask==0,float('-inf'))

        scores = scores.softmax(dim=-1)
        
        output = scores@v
        
        return output,scores

