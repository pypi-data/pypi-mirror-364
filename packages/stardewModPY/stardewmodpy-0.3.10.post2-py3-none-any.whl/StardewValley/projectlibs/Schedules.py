from .libModel import libModel

class Schedules(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Schedules as Schedules_List
from StardewValley.Data.SVModels.Schedules import Schedules
""" if self.optionals["Schedules"] else ""

        self.implements="Schedules(mod=self, Schedules_List=[])" if self.optionals["Schedules"] else ""

        self.classFileData_imports="""from StardewValley.Characters.schedules import scheduleData, scheduleValueData
from StardewValley.Data.GameData import Direction
"""
        
        self.classFileData_contents="""self.json={}

        self.json["spring"]=scheduleData(
            [
                scheduleValueData(
                    time=1000,
                    location="Town",
                    tileX=130,
                    tileY=150,
                    facingDirection=Direction.Down
                )
            ]
        ).getJson()"""