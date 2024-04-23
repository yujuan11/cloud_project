# base on latest python file
FROM python:latest

# add our python program
ADD plotdata.py ./

# install dependent libraries
RUN pip install --upgrade --user pika matplotlib numpy awkward

# the command to run our program
CMD [ "python", "./plotdata.py"]
