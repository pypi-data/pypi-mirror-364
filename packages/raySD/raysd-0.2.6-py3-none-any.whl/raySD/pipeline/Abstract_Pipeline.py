from abc import ABC, abstractmethod

class AbstractPipeline(ABC):
    def __init__(self, **kwargs):
         ## Hook model
        self.module_pre_hook = []
        self.module_post_hook = []

    def __call__(self, *args, **kwargs):
        for hook in self.module_pre_hook:
            x = hook(*args, **kwargs)
        x = self.forward(*args, **kwargs)
        for hook in self.module_post_hook:
            x = hook(*args, **kwargs)
        return x
    
    def register_pre_hook(self, hook):
        self.module_pre_hook.append(hook)

    def register_post_hook(self, hook):
        self.module_post_hook.append(hook)

    def forward(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_weights(self):
        pass
