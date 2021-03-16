# LinuxTracker-RSSObserver
An observer script for LinuxTracker RSS Feed

This project aims at reading an RSS feed provided by the [Linuxtracker](https://linuxtracker.org/) community.

The main file is `linuxtracker_rss.py`: this takes care of parsing the RSS feed, downloading the torrents files, logging and environment variables handling. These newly downloaded files should then be handled by a handler, contained in the `handlers` directory.


Ideally, one could implement its own handler for the specific neede use and simply replace the few lines of code regarding the invocation of the handler.

Also, specifying environment variables for the handler can be done, using the `.env` file, which is already read by `linuxtracker_rss.py`.


Future releases will handle choosing a handler at runtime with environment variables, easing updates and more scenarios.


Logging levels are implemented and can be changed always from the `.env` file.

The available logging levels are:
'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'.