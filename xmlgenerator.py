import xml.etree.ElementTree as ET
from xml.dom import minidom

class XmlGenerator:
    def __init__(self):
        self.counter = 1
        self.root = ET.Element("program")
        self.root.set("language", "IPPcode24")
    
    def addTreeElement(self, opcode, *argv):
        instruction = ET.SubElement(self.root, "instruction", order=str(self.counter), opcode=f"{opcode.name}")
        self.counter +=1
        for i, arg in enumerate(argv):
            child = ET.SubElement(instruction, f"arg{i+1}", type=self.getArgType(arg))
            child.text = arg.value
    
    def generateXML(self):
        prettyTree = self.prettify(self.root)
        print(prettyTree)

    def prettify(self, element):
        """Vrátí formátovaný řetězec XML pro daný element ET."""
        rough_string = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def getArgType(self, token):
        tokenTypeStr = token.tokenType.name
        return tokenTypeStr.lower()