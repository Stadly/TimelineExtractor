import datetime as DT
import logging
import os
import piexif
import re
from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET

def GetFromPictureFile(FilePath: str) -> Optional[DT.datetime]:
    """
    Get capture date for picture file.
    """
    try:
        Exif = piexif.load(FilePath)
    except:
        return None

    if 'Exif' not in Exif or 36867 not in Exif['Exif']:
        return None

    DateTimeString = Exif['Exif'][36867].decode('utf-8')
    return DT.datetime.strptime(DateTimeString, '%Y:%m:%d %H:%M:%S')


def GetFromXmpFile(FilePath: str) -> Optional[DT.datetime]:
    """
    Get capture date for xmp file.
    """
    try:
        XmpTree = ET.parse(FilePath)
    except:
        return None

    XmpNs = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'exif': 'http://ns.adobe.com/exif/1.0/',
    }

    Exif = XmpTree.find('rdf:RDF/rdf:Description', XmpNs)
    if Exif is None:
        return None

    DateTimeString = Exif.get('{' + XmpNs['exif'] + '}DateTimeOriginal')
    if DateTimeString is None:
        return None

    if re.match('\\d+-\\d+-\\d+T\\d+:\\d+:\\d+\\.\\d+', DateTimeString):
        return DT.datetime.strptime(DateTimeString, '%Y-%m-%dT%H:%M:%S.%f')

    return DT.datetime.fromisoformat(DateTimeString)


def GetFromFile(FilePath: str) -> Optional[DT.datetime]:
    """
    Get capture date for file.
    """
    DateTime = None
    FileExt = os.path.splitext(FilePath)[1].lower()
    if FileExt in [
        '.cr2',
        '.dng',
        '.jpg',
        '.nef',
        '.tif',
    ]:
        DateTime = GetFromPictureFile(FilePath)
    elif FileExt in ['.xmp']:
        DateTime = GetFromXmpFile(FilePath)
    else:
        logging.debug('Skipping file with extension %s: %s', FileExt, FilePath)
        return None

    if(DateTime is None):
        logging.warning('Could not get capture date from %s.', FilePath)

    return DateTime


def GetFromPath(Path: str, VisitSubdirectories: bool = False) -> List[DT.datetime]:
    """
    Get list of capture dates for files in path. The path can be either file or directory.
    """
    DateTimes = set()
    if os.path.isdir(Path):
        for File in os.scandir(Path):
            if File.is_file():
                DateTime = GetFromFile(File.path)
                if DateTime is not None:
                    DateTimes.add(DateTime)
            elif File.is_dir() and VisitSubdirectories:
                DateTimes.update(GetFromPath(File.path, VisitSubdirectories))
    elif os.path.isfile(Path):
        DateTime = GetFromFile(Path)
        if DateTime is not None:
            DateTimes.add(DateTime)
    else:
        logging.warning('%s is not a valid path.', Path)

    return list(DateTimes)


def GetMinAndMaxFromPath(Path: str, VisitSubdirectories: bool = False) -> Tuple[Optional[DT.datetime], Optional[DT.datetime]]:
    """
    Get minimum and maximum capture date for files in path. The path can be either file or directory.
    """
    MinDateTime = None
    MaxDateTime = None
    if os.path.isdir(Path):
        for File in os.scandir(Path):
            NextMinDateTime = None
            NextMaxDateTime = None

            if File.is_file():
                DateTime = GetFromFile(File.path)
                NextMinDateTime = DateTime
                NextMaxDateTime = DateTime
            elif File.is_dir() and VisitSubdirectories:
                NextMinDateTime, NextMaxDateTime = GetMinAndMaxFromPath(File.path, VisitSubdirectories)

            if MinDateTime is None:
                MinDateTime = NextMinDateTime
            elif NextMinDateTime is not None:
                MinDateTime = min(MinDateTime, NextMinDateTime)

            if MaxDateTime is None:
                MaxDateTime = NextMaxDateTime
            elif NextMaxDateTime is not None:
                MaxDateTime = max(MaxDateTime, NextMaxDateTime)
    elif os.path.isfile(Path):
        DateTime = GetFromFile(Path)
        MinDateTime = DateTime
        MaxDateTime = DateTime
    else:
        logging.warning('%s is not a valid path.', Path)

    return MinDateTime, MaxDateTime
