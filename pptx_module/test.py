
from parser import PPTParser
from controller import PPTController
from create import PPTCreator
import os
import json
import time


file_path = "test.pptx"
creator = PPTCreator(file_path)
creator.main()

absolute_path = os.path.abspath(file_path)

parser = PPTParser(absolute_path)
data = parser.parse()
with open(os.path.splitext(os.path.basename(file_path))[0]+".json", "w") as outfile:
        json.dump(data, outfile, indent=4)


controller = PPTController()
controller.open_presentation(absolute_path)
controller.start_show()

time.sleep(7)
controller.next_slide()
print("Now at slide 2")
time.sleep(3)
controller.goto_slide(4)
print("Now at slide 4")
time.sleep(3)
controller.previous_slide()
print("NOw at slide 3")
time.sleep(3)
controller.goto_slide(5)
print("Now at slide 5")
time.sleep(3)

controller.end_show()
print("End show")
# controller.close()
print("Close application")
