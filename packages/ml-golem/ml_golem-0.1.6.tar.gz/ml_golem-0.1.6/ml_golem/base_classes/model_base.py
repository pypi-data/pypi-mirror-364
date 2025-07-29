from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass
import torch.nn as nn

class ModelBase(ConfigBasedClass,nn.Module):
    def __init__(self,args,subconfig_keys):
        ConfigBasedClass.__init__(self, args, subconfig_keys)
        nn.Module.__init__(self)
        self.resume_epoch = None

    def _set_device(self, device):
        self.device = device

    # Call this method to get the device on which the model is currently located
    def _get_device(self):
        return self.device

    def _set_resume_epoch(self, epoch):
        self.resume_epoch = epoch

    # Call this method to get the epoch from which the model resumed training or inference
    def _get_resume_epoch(self):
        return self.resume_epoch    