from collections import deque
from datetime import datetime
import pprint

from torch import Tensor
from .QML import QML
from torch.optim import SGD, Adam

from torch.optim.lr_scheduler import *
import torch


class GradientQML(QML):

    def __init__(self, agent, env, settings, inputFile="data.csv"):
        self.prefix = ""
        super().__init__(agent, env, settings, inputFile)
        # check for learning rate scheduler
        lrSettings = self.settings["lr"]
        if isinstance(lrSettings, list):
            lr = lrSettings[0]
        else:
            lr = lrSettings
        # chose optimizer
        if self.settings["optimizer"].lower() == "adam":
            self.optimizer = Adam(self.agent.model.parameters(), lr=lr, amsgrad=True)
        elif self.settings["optimizer"].lower() == "sgd":
            self.optimizer = SGD(self.agent.model.parameters(), lr=lr, momentum=0.9)
        else:
            self.optimizer = Adam(self.agent.model.parameters(), lr=lr)
        # create scheduler
        if isinstance(lrSettings, list):
            self.scheduler = StepLR(self.optimizer, step_size=lrSettings[1], gamma=lrSettings[2])
        else:
            self.scheduler = ConstantLR(self.optimizer, factor=1.0)

    def setModel(self, model):
        self.agent = model

    def run(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Start Time =", current_time)
        print("Settings: ")
        pprint.pprint(self.settings)
        # print settings to file
        with open(self.generateFilename("settings", "conf"), "w") as settingsLog:
            pprint.pprint(self.settings, settingsLog)

        # initialize variables for live evaluation
        rewardList = deque(maxlen=40)

        # train the agent
        for episode in range(self.numEpisodes):

            loss = torch.tensor(0.0)
            for i in range(self.settings["batchsize"]):
                # learn a new state
                state, rewards = self.env.step()
                input = Tensor(state)
                prediction = self.agent(input)
                selected = self.agent.select(prediction, len(rewards))

                reward = rewards[selected]

                # calculate average for console output
                rewardList.append(reward)
                averageReward = sum(rewardList) / len(rewardList)

                # calculate loss
                loss += self.agent.loss(prediction, rewards)

            # backward calculation and optimizer step
            if (loss > 0):
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                self.scheduler.step()

            # print current result
            print("Episode: {}, loss: {:.3f}, Reward : {:.3f}, LR : {:.4f}".format(episode, loss.item(), averageReward, self.scheduler.get_last_lr()[0]), end="\n")

            if (episode % self.logInterval) == 0 or episode == self.numEpisodes - 1:
                # log to results file
                stats = self.env.elvaluateModel(self.agent)
                self.resultFile.write(",".join(str(e) for e in ([episode] + stats)))
                self.resultFile.write("\n")

        # store generated model
        self.saveModel()
        self.end()
        print("End Time =", datetime.now().strftime("%H:%M:%S"))
