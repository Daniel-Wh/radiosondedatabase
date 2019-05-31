import os as os


DIR_NAME = "27199/27199_1994"
for file in os.listdir(DIR_NAME):
    if file.endswith('.out'):
        open(os.path.join(DIR_NAME, file))
