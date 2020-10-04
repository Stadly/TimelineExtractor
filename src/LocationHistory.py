import datetime as DT
import re
import requests
from typing import List
import xml.etree.ElementTree as ET

def ElementsAreEqual(Element1: ET.Element, Element2: ET.Element) -> bool:
    """
    Check that two elements are indistinguishable from each other.
    """
    if Element1.tag != Element2.tag:
        return False
    if Element1.text != Element2.text:
        return False
    if Element1.tail != Element2.tail:
        return False
    if Element1.attrib != Element2.attrib:
        return False
    if len(Element1) != len(Element2):
        return False
    return all(ElementsAreEqual(Child1, Child2) for Child1, Child2 in zip(Element1, Element2))


def Merge(LocationHistory1: ET.ElementTree, LocationHistory2: ET.ElementTree) -> ET.ElementTree:
    """
    Merge two location histories.
    """
    Ns = {
        'ns': 'http://www.opengis.net/kml/2.2',
    }

    Document1 = LocationHistory1.find('ns:Document', Ns)
    Document2 = LocationHistory2.find('ns:Document', Ns)
    if Document1 is None or Document2 is None:
        raise Exception('Location history is malformed.')

    Name1 = Document1.find('ns:name', Ns)
    Name2 = Document2.find('ns:name', Ns)
    if Name1 is None or Name1.text is None or Name2 is None or Name2.text is None:
        raise Exception('Location history is malformed.')

    Name1.text += '\n' + Name2.text

    LastPlacermark1 = Document1.find('ns:Placemark[last()]', Ns)
    FirstPlacermark2 = Document2.find('ns:Placemark[1]', Ns)

    if LastPlacermark1 is not None and FirstPlacermark2 is not None:
        if ElementsAreEqual(LastPlacermark1, FirstPlacermark2):
            Document1.remove(LastPlacermark1)

    for Placemark in Document2.findall('ns:Placemark', Ns):
        Document1.append(Placemark)

    return LocationHistory1


def GetDate(Date: DT.date, AuthCookie: str) -> ET.ElementTree:
    """
    Get location history for a date.
    """
    Url = 'https://www.google.com/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i{0}!2i{1}!3i{2}!2m3!1i{0}!2i{1}!3i{2}'.format(Date.year, Date.month - 1, Date.day)

    Response = requests.get(Url, cookies=dict(cookie=AuthCookie))
    if 200 != Response.status_code:
        raise Exception('Could not fetch location history.')

    return ET.ElementTree(ET.fromstring(Response.text))


def GetDates(Dates: List[DT.date], AuthCookie: str) -> ET.ElementTree:
    """
    Get location history for one or more dates.
    """
    if not bool(Dates):
        raise Exception('You must specify at least one date.')

    SortedDates = sorted(Dates)

    LocationHistory = GetDate(SortedDates[0], AuthCookie)

    for Date in SortedDates[1:]:
        LocationHistory = Merge(LocationHistory, GetDate(Date, AuthCookie))

    return LocationHistory


def GetDateRange(StartDate: DT.date, EndDate: DT.date, AuthCookie: str) -> ET.ElementTree:
    """
    Get location history for a date range.
    """
    if EndDate < StartDate:
        raise Exception('Start date cannot be later than end date.')

    LocationHistory = GetDate(StartDate, AuthCookie)

    for Delta in range((EndDate - StartDate).days):
        Date = StartDate + DT.timedelta(Delta + 1)
        LocationHistory = Merge(LocationHistory, GetDate(Date, AuthCookie))

    return LocationHistory


def ReorderLineStringAndTimeSpan(KmlTree: ET.ElementTree) -> None:
    """
    Move LineString last so it follows TimeSpan or TimeStamp.
    Workaround for bug in Google Location History: https://github.com/gpsbabel/gpsbabel/issues/482
    """
    Ns = {
        'ns': 'http://www.opengis.net/kml/2.2',
    }

    for Placemark in KmlTree.findall('ns:Document/ns:Placemark', Ns):
        LineString = Placemark.find('ns:LineString', Ns)
        if LineString is not None:
            Placemark.remove(LineString)
            Placemark.append(LineString)


def ConvertTimeSpanPointToLineString(KmlTree: ET.ElementTree) -> None:
    """
    Convert Point combined with TimeSpan to LineString.
    Workaround for limitation in GPSBabel: https://github.com/gpsbabel/gpsbabel/issues/484
    """
    Ns = {
        'ns': 'http://www.opengis.net/kml/2.2',
    }

    for Placemark in KmlTree.findall('ns:Document/ns:Placemark', Ns):
        Point = Placemark.find('ns:Point', Ns)
        TimeSpan = Placemark.find('ns:TimeSpan', Ns)
        if Point is not None and TimeSpan is not None:
            Point.tag = '{' + Ns['ns'] + '}LineString'
            Coordinates = Point.find('ns:coordinates', Ns)
            if Coordinates is not None and Coordinates.text is not None:
                Coordinates.text = Coordinates.text + ' ' + Coordinates.text


def RemoveErroneousAltitude(KmlTree: ET.ElementTree) -> None:
    """
    Remove altitude information.
    Google Location History always reports the altitude as 0.
    That is obviously wrong, so it is better to have no altitude information.
    """
    Ns = {
        'ns': 'http://www.opengis.net/kml/2.2',
    }

    CoordinatesRegEx = '(\\d+(?:\\.\\d*)?,\\d+(?:\\.\\d*)?),0'
    RegEx = '^(?:' + CoordinatesRegEx + ' +)*' + CoordinatesRegEx + ' *$'

    for Placemark in KmlTree.findall('ns:Document/ns:Placemark', Ns):
        Point = Placemark.find('ns:Point', Ns)
        if Point is not None:
            Coordinates = Point.find('ns:coordinates', Ns)
            if Coordinates is not None and Coordinates.text is not None and re.search(RegEx, Coordinates.text):
                # All altitudes are 0. Remove them.
                Coordinates.text = re.sub(CoordinatesRegEx, '\\1', Coordinates.text)

        LineString = Placemark.find('ns:LineString', Ns)
        if LineString is not None:
            Coordinates = LineString.find('ns:coordinates', Ns)
            if Coordinates is not None and Coordinates.text is not None and re.search(RegEx, Coordinates.text):
                # All altitudes are 0. Remove them.
                Coordinates.text = re.sub(CoordinatesRegEx, '\\1', Coordinates.text)
