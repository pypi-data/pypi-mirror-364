import torch
from torch.optim.adamw import AdamW
from mortm.train.train import AbstractTrainSet, TrainArgs
from mortm.train.utils.loss import RLDFLoss
from mortm.train.noam import noam_lr
from mortm.models.modules.config import MORTMArgs
from mortm.models.mortm import MORTM
from mortm.models.bertm import BERTM, ActorCritic

class RLDF(AbstractTrainSet):

    def __init__(self, t_args: TrainArgs, args: MORTMArgs, b_args: MORTMArgs, progress, load_mortm_directory, load_bertm_directory, use_lora=False):
        self.args = args
        self.args.use_lora = use_lora
        ############ LOAD MODEL ###########################
        self.base_model = MORTM(args, progress)
        self.base_model.load_state_dict(torch.load(load_mortm_directory), strict=True)
        for param in self.base_model.parameters():
            param.requires_grad = False

        ########### LOAD REWARD MODEL ####################
        self.bertm = BERTM(args=b_args, progress=progress)
        self.actor_critic = ActorCritic(args=b_args, progress=progress)
        self.bertm.load_state_dict(torch.load(load_bertm_directory), strict=True)
        self.actor_critic.load_state_dict(torch.load(load_mortm_directory), strict=True)
        for param in self.bertm.parameters():
            param.requires_grad = False

        sc = noam_lr(args.d_model, warmup_steps=t_args.warmup_steps)
        super().__init__(criterion=RLDFLoss(),
                         optimizer=AdamW(self.actor_critic.parameters(), lr=5e-1),
                         scheduler=sc)

    def epoch_fc(self, model, pack, progress):
        pass

    def pre_processing(self, pack, progress):
        pass
