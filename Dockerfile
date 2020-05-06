FROM python:3-alpine

RUN apk update && apk upgrade

COPY . /TimelineExtractor

WORKDIR /TimelineExtractor/src

RUN pip install -r ../requirements.txt

ENTRYPOINT ["python", "extract.py"]
CMD ["-h"]
