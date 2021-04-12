# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

import signal
from contextlib import contextmanager


class IAgent():

    __metaclass__ = ABCMeta

    name = ""

    @abstractmethod
    def __init__(self, name, _):
        pass

    @abstractmethod
    def getAction(self, observations):
        pass

    @abstractmethod
    def getReward(self, info):
        pass

    @abstractmethod
    def observeOthers(self, envInfo):
        pass

    @abstractmethod
    def actionUpdate(self,  observation, nextObservation, action, envInfo):
        pass

    @abstractmethod
    def matchUpdate(self,  envInfo):
        pass


    """Adds a timeout for the action function"""
    @contextmanager
    def timeout(self,time):
        # Register a function to raise a TimeoutError on the signal.
        signal.signal(signal.SIGALRM, self.raise_timeout)
        # Schedule the signal to be sent after ``time``.
        signal.alarm(time)

        try:
            yield
        except TimeoutError:
            pass
        finally:
            # Unregister the signal so it won't be triggered
            # if the timeout is not reached.
            signal.signal(signal.SIGALRM, signal.SIG_IGN)


    def raise_timeout(self, signum, frame):
        raise TimeoutError