import torch

from abc import ABC, abstractmethod
"""
Examples in this file use 5 outputs with 3 targets
Target t1,t2,t3
values x1,x2,x3,x4,x5
"""


def fromString(s, model):
    if s == "ModuloSum" or s == "ModSum":
        return ModuloSum(model)
    elif s == "ModuloMean" or s == "ModMean":
        return ModuloMean(model)
    elif s == "ModuloMax" or s == "ModMax":
        return ModuloMax(model)
    elif s == "EqualValues" or s == "Equal":
        return EqualValues(model)
    else:
        return Full(model)


# defines the interpretation of a ML model
class Interpretation(ABC):

    model: torch.nn.Module

    def __init__(self, model) -> None:
        self.model = model

    def __call__(self, input: torch.Tensor) -> torch.Tensor:
        return self.model(input)

    @abstractmethod
    def select(self, prediction: torch.Tensor, n: int = -1):
        pass

    @abstractmethod
    def loss(self, prediction: torch.Tensor, compare):
        pass


class Full(Interpretation):
    """
    For n required outputs use the first n values

    Later values are ignored
    """

    def __init__(self, model) -> None:
        super().__init__(model)

    def select(self, prediction: torch.Tensor, n: int = -1):
        if n < 0:
            return prediction.argmax()
        else:
            return prediction[0:n].argmax()

    def loss(self, prediction: torch.Tensor, compare):
        loss = torch.tensor(0.0)
        predictAllRewards = True
        if (predictAllRewards):
            for i in range(0, len(compare)):
                loss += (prediction[i] - compare[i])**2
        else:
            for i in range(0, len(compare)):
                if (compare[i] > 0):
                    loss += (prediction[i] - compare[i])**2
        return loss


class ModuloCondense(Interpretation):

    @abstractmethod
    def condense(self, prediction: torch.Tensor, n: int) -> torch.Tensor:
        raise Exception("This should not have been called")
        pass

    def select(self, prediction: torch.Tensor, n: int = -1):
        if n <= 0: raise ValueError("Parameter n has to be larger than 0")
        return self.condense(prediction, n).argmax()

    def loss(self, prediction: torch.Tensor, compare):
        loss = torch.tensor(0.0)
        values = self.condense(prediction, len(compare))
        for i in range(0, len(compare)):
            loss += (values[i] - compare[i])**2
        return loss


class ModuloSum(ModuloCondense):
    """
    Use sum to condense multiple values to one
    """

    def condense(self, prediction: torch.Tensor, n: int) -> torch.Tensor:
        result = torch.Tensor([0.0] * n)
        for i in range(len(prediction)):
            result[i % n] += prediction[i]

        # renormalize the result
        return result / result.max()


class ModuloMax(ModuloCondense):
    """
    Use 'max' to condense multiple values to one 
    """

    def condense(self, prediction: torch.Tensor, n: int) -> torch.Tensor:
        result = torch.Tensor([0.0] * n)
        for i in range(len(prediction)):
            result[i % n] = torch.max(prediction[i], result[i % n])
        return result


class ModuloMean(ModuloCondense):
    """
    Use 'mean' to condense multiple values to one 
    """

    def condense(self, prediction: torch.Tensor, n: int) -> torch.Tensor:
        result = torch.Tensor([0.0] * n)
        counter = torch.Tensor([0] * n)
        for i in range(len(prediction)):
            result[i % n] += prediction[i]
            counter[i % n] += 1
        result = torch.div(result, counter)
        return result / result.max()


class EqualValues(Interpretation):
    """
    Use modulo on the selected index
    For selection the maximal value is choosing
    For loss all values should be equal to the target
    """

    def select(self, prediction: torch.Tensor, n: int = -1):
        return prediction.argmax() % n

    def loss(self, prediction: torch.Tensor, compare):
        loss = torch.tensor(0.0)
        for i in range(0, len(prediction)):
            loss += (prediction[i] - compare[i % len(compare)])**2
        return loss
