# TimelineExtractor

[![Software License][ico-license]](LICENSE.md)

Extract location history from Google Maps Timeline.

## Introduction

By enabling Location History in Google Maps, Google will save your location data and processes it in order to create your personal [Timeline](https://www.google.com/maps/timeline).

You can easily [download the raw data](https://takeout.google.com/) saved by Google. It is also possible to download the processed location history for a single day, but not to download more than one day at a time.

`TimelineExtractor` lets you easily download your location history. There are multiple options for specifying which dates to download:
- Specify one or more dates.
- Specify a date range.
- Specify one or more photos or directories, to download location history for the capture dates of the photos and contained photos.

Google Timeline exports your location history using the `kml` format. There are som issues with how Google formats the files, making them incompatible with software such as [GPSBabel](https://www.gpsbabel.org). `TimelineExtractor` takes care of these issues, generating valid `kml` files.

## Change log

Please see [CHANGELOG](CHANGELOG.md) for information on what has changed recently.

## Security

If you discover any security related issues, please email magnar@myrtveit.com instead of using the issue tracker.

## Credits

- [Magnar Ovedal Myrtveit][link-author]
- [All contributors][link-contributors]

## License

The MIT License (MIT). Please see [License file](LICENSE.md) for more information.

[ico-license]: https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square

[link-author]: https://github.com/Stadly
[link-contributors]: ../../contributors
