import argparse
import datetime as DT
import logging
import sys
from typing import List
import xml.etree.ElementTree as ET
import LocationHistory

def OutputLocationHistory(History: ET.ElementTree) -> None:
    LocationHistory.RemoveErroneousAltitude(History)
    LocationHistory.ConvertTimeSpanPointToLineString(History)
    LocationHistory.ReorderLineStringAndTimeSpan(History)

    # Set the default namespace. Workaround for bug in GPSBabel: https://github.com/gpsbabel/gpsbabel/issues/508
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')
    History.write(sys.stdout.buffer)


def GetLocationHistoryForDates(Dates: List[DT.date], AuthCookie: str) -> ET.ElementTree:
    logging.info('Calculating location history for %d date(s)', len(Dates))
    return LocationHistory.GetDates(Dates, AuthCookie)


def StringToDate(DateString: str) -> DT.date:
    return DT.datetime.strptime(DateString, '%Y-%m-%d').date()


def main() -> None:
    Parser = argparse.ArgumentParser(description="Extract location history from Google.")
    Parser.add_argument('-l', '--log', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Set the logging level.')
    Parser.add_argument('-c', '--cookie', required=True, type=open, help='File containing your Google authentication cookie.')

    Subparsers = Parser.add_subparsers(title='mode', dest='mode', required=True, help='How to specify dates to extract location history for.')

    # Argument parser for date mode.
    DateParser = Subparsers.add_parser('date')
    DateParser.add_argument('date', nargs='+', type=StringToDate, help='One or more dates to extract location history for. Format: YYYY-MM-DD')

    Args = Parser.parse_args()

    AuthCookie = Args.cookie.read()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=Args.log.upper())

    History = None
    if Args.mode == 'date':
        History = GetLocationHistoryForDates(Args.date, AuthCookie)

    if History is None:
        logging.error('Location history could not be calculated.')
    else:
        OutputLocationHistory(History)

if __name__ == '__main__':
    main()
