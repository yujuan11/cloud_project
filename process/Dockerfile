# base on latest python file
FROM python:latest

# add our python program
ADD processdata.py ./
ADD infofile.py ./
# install dependent libraries
RUN pip install --upgrade --user pika vector awkward uproot aiohttp

# the command to run our program
CMD [ "python", "./processdata.py"]
