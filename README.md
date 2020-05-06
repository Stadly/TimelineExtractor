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

## Usage

### Authentication

In order to download location history from Google Maps, you must be authenticated. Authentication is done by passing an authentication cookie to `TimelineExtractor`.

#### Get authentication cookie

Follow the steps below to get your authentication cookie from Google Maps Timeline:

1. Go to [Timeline](https://www.google.com/maps/timeline) using [Google Chrome](https://www.google.com/chrome/) or another Chromium-based browser.
2. Open `Developer tools` (`Ctrl+Shift+I`).
3. Go to the `Network` tab.
4. Enter this URL in the address bar of your browser: `https://www.google.com/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2020!2i0!3i1!2m3!1i2020!2i0!3i1`
5. A new request will appear in the `Developer tools`. Copy it as `cURL`.

   ![Copy request as cURL](docs/get-authentication-cookie.png)

6. Paste the copied request into a text editor.
7. You should get something like this:
```
curl "https://www.google.com/maps/timeline/kml?authuser=0^&pb=^!1m8^!1m3^!1i2020^!2i0^!3i1^!2m3^!1i2020^!2i0^!3i1" ^
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ^
  -H "accept-language: en" ^
  -H "authority: www.google.com" ^
  -H "cookie: <COOKIE CONTENT>" ^
  -H "user-agent: Mozilla/5.0" ^
  --compressed
```

8. Save the cookie content (what is replaced by `<COOKIE CONTENT>` above) so you can use it to authenticate requests sent by `TimelineExtractor` when downloading location history. It is recommended to store it in a file called `cookie` in the directory `src`, as that will be assumed in most of the examples further down.

#### Authenticate

To authenticate, specify the path to your cookie file using the `-c` or `--cookie` argument when running `TimelineExtractor`:

```
python extract.py -c path/to/cookie
```

### Get location history

There are three ways to specify which dates to extract location history for:
1. [Specify one or more dates](#get-location-history-for-one-or-more-dates).
2. [Specify a date range](#get-location-history-for-a-date-range).
3. [Specify one or more photos or directories](#get-location-history-for-one-or-more-photos-or-directories), to download location history for the capture dates of the photos and contained photos.

#### Get location history for one or more dates

To download location history for a date, simply use the `date` mode and specify the date in `YYYY-MM-DD` format:

``` bash
python extract.py -c cookie date 2020-01-01
```

If you specify multiple dates, location history will be downloaded for all of them:

``` bash
python extract.py -c cookie date 2020-01-01 2020-01-05 2020-02-10
```

#### Get location history for a date range

To download location history for a date range, simply use the `range` mode and specify the first date and last date in `YYYY-MM-DD` format:

``` bash
python extract.py -c cookie range 2020-01-01 2020-01-31
```

#### Get location history for one or more photos or directories

To download location history for the capture date of a photo, simply use the `photo` mode and specify the path to the photo:

``` bash
python extract.py -c cookie photo path/to/photo.jpg
```

If you specify a directory, location history will be downloaded for all the photos in the directory:

``` bash
python extract.py -c cookie photo path/to/directory
```

If you specify multiple paths, location history will be downloaded for all of them:

``` bash
python extract.py -c cookie photo path/to/photo.jpg path/to/directory
```

Use the `-s` or `--subdir` argument to download location history also for photos in subdirectories of the specified directories:

``` bash
python extract.py -c cookie photo -s path/to/directory-tree
```

### Store the location history

The downloaded location history is written to `stdout`. To store it in a file, simply redirect `stdout` to the file:

``` bash
python extract.py -c cookie date 2020-01-01 > path/to/location-history.kml
```

### Logging output

Any logging output generated by `TimelineExtractor` is written to `stderr`. There are five levels of logging:

1. debug
2. info
3. warning
4. error
5. critical

By default, `info` and higher log messages are output. Use the `-l` or `--log` argument to specify which levels of log messages to output:

``` bash
python extract.py -l debug -c cookie date 2020-01-01
```

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
