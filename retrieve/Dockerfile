# base on latest python file
FROM python:latest

# add our python program
ADD retrievepath.py ./
ADD infofile.py ./

# install dependent libraries
RUN pip install pika 

# the command to run our program
CMD [ "python", "-u", "./retrievepath.py"]
