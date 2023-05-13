

from dashboardWidgets.widgetConfig import WidgetConfig

class AutoChooser(WidgetConfig):
    def __init__(self, xPos, yPos, nt4Topic_in):
        WidgetConfig.__init__(self, nt4Topic_in, xPos, yPos)
        self.nominalHeight = 5
        self.nominalWidth = 40
        self.isVisible = True
        self.modeNameList = []
        self.nt4TopicDesVal = ""

    def _getJsModeNameListString(self):
        retVal = "["
        retVal += ",".join(self.modeNameList)
        retVal += "]"
        return retVal
        
    def  getJSDeclaration(self):
        retStr = f"var widget{self.idx} = new AutoChooser('widget{self.idx}', '{self.name}', {self._getJsModeNameListString()}, onWidget{self.idx}ValUpdated);\n"
        retStr += f"nt4Client.publishNewTopic(\"{self.nt4TopicDesVal}\", \"int\");"
        return retStr
            
    def  getJSSetData(self):
        retStr = ""
        retStr += f"if(name == \"" + self.nt4TopicCurVal + "\"){ "
        retStr += f"    widget{self.idx}.setActualState(value)"
        retStr += "}"
        return retStr
    
    def  getJSUpdate(self) :
        return f"    widget{self.idx}.render()"
    
    def  getJSSetNoData(self):
        return f"    widget{self.idx}.reportNoData()"
    
    def getJSCallback(self):
        retStr = ""
        retStr += f"function onWidget{self.idx}ValUpdated(value) {{\n"
        retStr += f"    nt4Client.addSample(\"{self.nt4TopicDesVal}\", nt4Client.getServerTime_us(), value);\n"
        retStr += "}"
        return retStr

    def getTopicSubscriptionStrings(self): 
        retStr = ""
        retStr += "\"" + self.nt4TopicDesVal + "\","
        retStr += "\"" + self.nt4TopicCurVal + "\","
        return retStr

    