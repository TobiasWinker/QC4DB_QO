import torch

class max_layer(torch.nn.Module):

    def __init__(self, action_space=2):
        super().__init__()

    def forward(self, x):
        """Forward step, as described above."""
        return x.argmax()

class reshapeSumLayer(torch.nn.Module):

    def __init__(self):
        super().__init__()

    def forward(self, x):
        result = torch.reshape(x, (16, 16))
        return result.sum(1)


class NormLayer(torch.nn.Module):

    def __init__(self):
        super().__init__()

    def forward(self, x):
        result = x / x.max()
        return result


class CutOutputLayer(torch.nn.Module):

    def __init__(self, nOut):
        super().__init__()
        self.nOut = nOut

    def forward(self, x):
        return torch.narrow(x, -1, 0, self.nOut)
