# TimelineExtractor

[![Software License][ico-license]](LICENSE.md)

Extract location history from Google Maps Timeline.

## Introduction

By enabling Location History in Google Maps, Google will save your location data and processes it in order to create your personal [Timeline](https://www.google.com/maps/timeline).

You can easily [download the raw data](https://takeout.google.com/) saved by Google; this will put your timeline data in `JSON` files that do not contain the same level of detail as downloading the `kml` files. It is also possible to download a `kml` file of the processed location history for a single day, but it is not possible to download more than one day at a time.

`TimelineExtractor` lets you easily download your location history. There are multiple options for specifying which dates to download:
- Specify one or more dates.
- Specify a date range.
- Specify one or more photos or directories, to download location history for the capture dates of the photos and contained photos.

Google Timeline exports your location history using the `kml` format. There are some issues with how Google formats the files, making them incompatible with software such as [GPSBabel](https://www.gpsbabel.org). `TimelineExtractor` takes care of these issues, generating valid `kml` files.

## Installation

Use the following commands to set up `TimelineExtractor`.

Download `TimelineExtractor`:

``` bash
git clone -b v1.1.0 --depth 1 https://github.com/Stadly/TimelineExtractor.git
```

Install dependencies:

``` bash
pip install -r TimelineExtractor/requirements.txt
```

Change working directory:

``` bash
cd TimelineExtractor/src
```

### Authentication

In order to download location history from Google Maps, you must be authenticated. Authentication is done by passing an authentication cookie, authenticated user number, and a reauth proof token to `TimelineExtractor`.

Follow the steps below to get your authentication cookie from Google Maps Timeline:

1. Go to [Timeline](https://www.google.com/maps/timeline) in [Firefox](https://www.mozilla.org/en-US/firefox/) (steps have been tested in Firefox, though other browsers should work similarly).
2. Open `Developer tools` (`F12`).
3. In the console, run this command to download the currently selected day's KML file `document.querySelector('.goog-menuitem.export-kml').click();`.
4. A new tab will briefly open and your KML download will start.
   - Depending on your browser settings, you may get a message saying that a pop-up has been prevented from opening; click the message and open the pop-up.
   - If you are prompted to save or cancel the download, be sure to save it (otherwise the URL may not be logged in the history and we'll need that).
5. Open the browser history in Firefox (`CTRL` + `Shift` + `H`) or the download history in Chrome (`CTRL` + `J`).
6. Copy the most recent URL, which should be something like this: `https://timeline.google.com/maps/timeline/kml?authuser=<AUTH USER NUMBER>&pb=%211m8%211m3%211i1990%212i0%213i1%212m3%211i2090%212i0%213i1&pli=1&rapt=<REAUTH PROOF TOKEN>`.
7. With the Developer tools still open, paste that URL into the address bar of your browser.
8. A new request will appear in the `Network` tab. Click on it.
9. Details about the request should appear; look for the `Cookie` in the request headers and copy the cookie value.
10. Save the cookie's content so you can use it to authenticate requests sent by `TimelineExtractor` when downloading location history. It is recommended to store it in a file called `cookie` in the directory `src`, as that will be assumed in most of the examples further down.
11. Make note of the `authuser` number in the URL. Pass this to the `TimelineExtractor` script with the `-u` or `--authuser` argument.
12. Copy the value of the `rapt` parameter in the URL. Pass this to the `TimelineExtractor` script with the `-r` or `--rapt` argument.

Please note that valid cookie and reauth proof tokens change frequently, so these steps may need to be repeated, depending on your usage of `TimelineExtractor`.

### Install in Docker container

It is also possible to set up and use `TimelineExtractor` in a docker container instead of installing it locally. See the section [Using Docker](#using-docker) for details.

## Usage

`TimelineExtractor` is run with the python file `extract.py`:

```
python extract.py
```

### Authenticate

To authenticate, specify the following arguments when running `TimelineExtractor`:
  - The path to your authentication cookie using the `-c` or `--cookie` argument.
  - The authuser number using the `-u` or `--authuser` argument.
  - The reauth proof token using the `-r` or `--rapt` argument.
  - The output file path using the `-o` or `--output` argument.

```
python extract.py -c path/to/cookie -u 1 -r token_value -o path/to/output/file
```

### Get location history

There are three ways to specify which dates to extract location history for:
1. [Specify one or more dates](#get-location-history-for-one-or-more-dates).
2. [Specify a date range](#get-location-history-for-a-date-range).
3. [Specify one or more photos or directories](#get-location-history-for-one-or-more-photos-or-directories), to download location history for the capture dates of the photos and contained photos.

#### Get location history for one or more dates

To download location history for a date, simply use the `date` mode and specify the date in `YYYY-MM-DD` format:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml date 2020-01-01
```

If you specify multiple dates, location history will be downloaded for all of them:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml date 2020-01-01 2020-01-05 2020-02-10
```

#### Get location history for a date range

To download location history for a date range, simply use the `range` mode and specify the first date and last date in `YYYY-MM-DD` format:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml range 2020-01-01 2020-01-31
```

#### Get location history for one or more photos or directories

To download location history for the capture date of a photo, simply use the `photo` mode and specify the path to the photo:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml photo path/to/photo.jpg
```

If you specify a directory, location history will be downloaded for all the photos in the directory:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml photo path/to/directory
```

If you specify multiple paths, location history will be downloaded for all of them:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml photo path/to/photo.jpg path/to/directory
```

Use the `-s` or `--subdir` argument to download location history also for photos in subdirectories of the specified directories:

``` bash
python extract.py -c cookie -u 1 -r token -o output.kml photo -s path/to/directory-tree
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

### Using Docker

[Docker](https://www.docker.com) makes setting up and using `TimelineExtractor` really easy. All you have to do is build the docker image, and you can use `TimelineExtractor` without installing any dependencies (even Python!) locally.

#### Build the docker image

Build the docker image using the following command. Note that you should [save you authentication cookie](#get-authentication-cookie) before building the docker image so that it becomes part of the image.

``` bash
docker build -t extract-timeline .
```

#### Run the docker container

After the image is built, just run it to use `TimelineExtractor`. The syntax when running `TimelineExtractor` inside the docker container is the same as when running it locally, except that `python extract.py` is replaced by `docker run extract-timeline`.

For example, the following command will extract location history for the date `2020-01-01` and store it in the file `timeline.kml` in your current working directory:

``` bash
docker run extract-timeline -c cookie -u 1 -r token -o timeline.kml date 2020-01-01
```

When extracting location history for photos, the docker container must be able to access to the photos in order to get their capture dates. This is achieved by mounting the directories containing the photos to the docker container. To mount a directory, use the `-v` or `--volume` argument and specify the absolute path of the directory in the local file system, followed by `:` and the absolute path of where it should be accessible in the container. Use the latter paths when specifying the photos and directories to get location history for.

In the following example, the local directory `/path/to/photos` is mounted to `/photos` in the container. Location history is then calculated for the photo `/photos/my-image.jpg` (refers to `/path/to/photos/my-image.jpg` in the local file system) and the photos contained in `/photos/more-photos` (refers to `/path/to/photos/more-photos` in the local file system).

``` bash
docker run -v /path/to/photos:/photos extract-timeline -c cookie -u 1 -r token -o output.kml photo /photos/my-image.jpg /photos/more-photos
```

If you want to mount a directory using a relative path, you can use `$(pwd)` to denote the current working directory:

``` bash
docker run -v "$(pwd):/photos" extract-timeline -c cookie -u 1 -r token -o output.kml photo /photos
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
