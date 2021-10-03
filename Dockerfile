FROM python:latest

RUN adduser imgin
USER imgin
WORKDIR /home/imgin/
COPY requirements.txt /home/imgin/
RUN pip install --user -r requirements.txt
COPY run.py /home/imgin/
COPY imgin/ /home/imgin/imgin
ENTRYPOINT [ "python", "run.py" ]