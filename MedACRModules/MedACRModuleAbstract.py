from abc import ABC, abstractmethod

class MedACRModule(ABC):
    @abstractmethod
    def Run(self):
        pass

    @abstractmethod
    def GetReportText(self):
        pass

    @abstractmethod
    def GetModuleName(self):
        pass