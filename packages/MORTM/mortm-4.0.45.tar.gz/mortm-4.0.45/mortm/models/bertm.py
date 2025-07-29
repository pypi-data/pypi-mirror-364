from .modules.layers import *
from .modules.config import MORTMArgs

from flash_attn.bert_padding import unpad_input, pad_input



class ActorCritic(nn.Module):
    def __init__(self, args: MORTMArgs, progress):
        super(ActorCritic, self).__init__()
        self.args = args
        self.progress = progress
        self.e_layer = args.e_layer
        self.d_layer = args.d_layer
        self.num_heads = args.num_heads
        self.d_model = args.d_model
        self.dim_feedforward = args.dim_feedforward
        self.dropout = args.dropout
        self.use_lora = args.use_lora

        self.decoder = MORTMDecoder(args, progress=progress)

        print(f"Input Vocab Size:{args.vocab_size}")
        self.embedding: nn.Embedding = nn.Embedding(args.vocab_size, self.d_model, padding_idx=0).to(self.progress.get_device())
        if not self.use_lora:
            self.Wout: nn.Linear = nn.Linear(self.d_model, args.vocab_size).to(self.progress.get_device())
        else:
            self.Wout: lora.Linear = lora.Linear(self.d_model, args.vocab_size, r=args.lora_r, lora_alpha=args.lora_alpha)

        self.critic_hidden = nn.Linear(self.d_model, self.d_model // 2)
        self.critic_out = nn.Linear(self.d_model // 2, 1)  # 出力次元を1に設定

        self.softmax: nn.Softmax = nn.Softmax(dim=-1).to(self.progress.get_device())

    def forward(self, x, padding_mask=None, is_causal=False, is_save_cache=False):
        x: Tensor = self.embedding(x).to(dtype=torch.bfloat16)
        if padding_mask is not None:
            batch, tgt_len, embed_dim = x.size()
            x, indices, cu_seqlens, max_s, used_seqlens = unpad_input(x, padding_mask)
        else:
            tgt_len, embed_dim = x.size()
            batch = None
            indices = cu_seqlens = max_s = used_seqlens = None
        out = self.decoder(tgt=x, tgt_is_causal=is_causal, cu_seqlens=cu_seqlens, max_seqlen=max_s,
                           batch_size=batch, indices=indices, is_save_cache=is_save_cache)
        if padding_mask is not None:
            out = pad_input(out, indices, batch, tgt_len)

        with torch.autocast(device_type="cuda", dtype=torch.float32):
            score: Tensor = self.Wout(out)
            hidden = self.critic_hidden(out)
            hidden = F.relu(hidden)
            critic_score = self.critic_out(hidden)
        return score, critic_score

class BERTM(nn.Module):

    def __init__(self, args: MORTMArgs, progress):
        super(BERTM, self).__init__()
        self.args = args # argsを保存しておくと便利
        self.embedding = nn.Embedding(args.vocab_size, args.d_model)
        self.decoder = MORTMDecoder(args=args,
                                    progress=progress)
        self.attn_pool = Pool(args)
        self.hidden = nn.Linear(args.d_model, args.d_model // 2)
        self.Wout = nn.Linear(args.d_model // 2, 1) # linear層の出力次元に合わせる

    def forward(self, x: Tensor, padding_mask=None):
        x: Tensor = self.embedding(x).to(dtype=torch.bfloat16)

        if padding_mask is not None:
            x, indices, cu_seqlens, max_s, used_seqlens = unpad_input(x, padding_mask)
        else:
            indices = cu_seqlens = max_s = used_seqlens = None

        out = self.decoder(tgt=x, tgt_is_causal=False, cu_seqlens=cu_seqlens, max_seqlen=max_s)

        out = self.attn_pool(out, cu_seqlens if cu_seqlens is not None else torch.tensor([0, len(x)], dtype=torch.int32, device=x.device))  # バッチサイズをcu_seqlensに設定

        out = self.hidden(out)
        hid = F.relu(out)
        score = self.Wout(hid)

        return score