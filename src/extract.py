import argparse
import datetime as DT
import logging
from typing import List, Optional
import xml.etree.ElementTree as ET
import CaptureDate
import LocationHistory

def OutputLocationHistory(History: ET.ElementTree, Output: argparse.FileType) -> None:
    LocationHistory.RemoveErroneousAltitude(History)
    LocationHistory.ConvertTimeSpanPointToLineString(History)
    LocationHistory.ReorderLineStringAndTimeSpan(History)

    # Set the default namespace. Workaround for bug in GPSBabel: https://github.com/gpsbabel/gpsbabel/issues/508
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')
    with open(Output.name, 'w', encoding='utf-8') as OutputFile:
        OutputFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        OutputFile.write(ET.tostring(History.getroot(), encoding='utf-8').decode('utf-8'))

    logging.info(f'Location history has been saved to {Output.name}')


def GetLocationHistoryForDates(Dates: List[DT.date], AuthCookie: str, AuthUser: int, Rapt: str) -> ET.ElementTree:
    logging.info(f'Calculating location history for {len(Dates)} date(s)')
    return LocationHistory.GetDates(Dates, AuthCookie, AuthUser, Rapt)


def GetLocationHistoryForDateRange(StartDate: DT.date, EndDate: DT.date, AuthCookie: str, AuthUser: int, Rapt: str) -> ET.ElementTree:
    logging.info(f'Calculating location history for {StartDate:%Y-%m-%d} to {EndDate:%Y-%m-%d}')
    return LocationHistory.GetDateRange(StartDate, EndDate, AuthCookie, AuthUser, Rapt)


def GetLocationHistoryForPaths(Paths: List[str], VisitSubdirectories: bool, AuthCookie: str, AuthUser: int, Rapt: str) -> Optional[ET.ElementTree]:
    DateTimes = set()
    for Path in Paths:
        logging.info(f'Calculating dates for photos in {Path}')
        DateTimes.update(CaptureDate.GetFromPath(Path, VisitSubdirectories))

    if not bool(DateTimes):
        logging.warning('No dates found to extract location history for.')
        return None

    Dates = list(set(map(lambda d: d.date(), DateTimes)))
    return GetLocationHistoryForDates(Dates, AuthCookie, AuthUser, Rapt)


def StringToDate(DateString: str) -> DT.date:
    return DT.datetime.strptime(DateString, '%Y-%m-%d').date()


def main() -> None:
    Parser = argparse.ArgumentParser(description='Extract location history from Google.')
    Parser.add_argument('-l', '--log', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Set the logging level.')
    Parser.add_argument('-c', '--cookie', required=True, type=open, help='File containing your Google authentication cookie.')
    Parser.add_argument('-u', '--authuser', required=True, type=int, help='The authuser number from the Google Maps URL.')
    Parser.add_argument('-r', '--rapt', required=True, type=str, help='The "re-auth proof token" (rapt) from a Google Maps KML file download url.')
    Parser.add_argument('-o', '--output', required=True, type=argparse.FileType('w'), help='Output file to write the extracted location history.')



    Subparsers = Parser.add_subparsers(title='mode', dest='mode', required=True, help='How to specify dates to extract location history for.')

    # Argument parser for date mode.
    DateParser = Subparsers.add_parser('date')
    DateParser.add_argument('date', nargs='+', type=StringToDate, help='One or more dates to extract location history for. Format: YYYY-MM-DD')

    # Argument parser for date range mode.
    RangeParser = Subparsers.add_parser('range')
    RangeParser.add_argument('start', type=StringToDate, help='First date to extract location history for. Format: YYYY-MM-DD')
    RangeParser.add_argument('end', type=StringToDate, help='Last date to extract location history for. Format: YYYY-MM-DD')

    # Argument parser for directory mode.
    PhotoParser = Subparsers.add_parser('photo')
    PhotoParser.add_argument('photo', nargs='+', help='One or more photos or directories to extract location history for. History will be extracted for the capture dates of the photos.')
    PhotoParser.add_argument('-s', '--subdir', action='store_true', default=False, help='Also consider photos in subdirectories.')

    Args = Parser.parse_args()

    AuthCookie = Args.cookie.read()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=Args.log.upper())

    History = None
    if Args.mode == 'date':
        History = GetLocationHistoryForDates(Args.date, AuthCookie, Args.authuser, Args.rapt)
    elif Args.mode == 'range':
        History = GetLocationHistoryForDateRange(Args.start, Args.end, AuthCookie, Args.authuser, Args.rapt)
    elif Args.mode == 'photo':
        History = GetLocationHistoryForPaths(Args.photo, Args.subdir, AuthCookie, Args.authuser, Args.rapt)

    if History is None:
        logging.error('Location history could not be calculated.')
    else:
        OutputLocationHistory(History, Args.output)

if __name__ == '__main__':
    main()
