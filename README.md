<div align="center" id="top">
  <img src="./.github/app.gif" alt="Fx Data Downloader" />

  &#xa0;

  <!-- <a href="https://fxdatadownloader.netlify.app">Demo</a> -->
</div>

<h1 align="center">Fx Data Downloader</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/javiergarciad/fx-data-downloader?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/javiergarciad/fx-data-downloader?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/javiergarciad/fx-data-downloader?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/javiergarciad/fx-data-downloader?color=56BEB8">

  <!-- <img alt="Github issues" src="https://img.shields.io/github/issues/javiergarciad/fx-data-downloader?color=56BEB8" /> -->

  <!-- <img alt="Github forks" src="https://img.shields.io/github/forks/javiergarciad/fx-data-downloader?color=56BEB8" /> -->

  <!-- <img alt="Github stars" src="https://img.shields.io/github/stars/javiergarciad/fx-data-downloader?color=56BEB8" /> -->
</p>

<!-- Status -->

<!-- <h4 align="center">
	🚧  Fx Data Downloader 🚀 Under construction...  🚧
</h4>

<hr> -->

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0;
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/javiergarciad" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

This script will download tick data for some FX pairs from FXCM into a SQLlite database.

Tick data can be used to backtest trading strategies.

FXCM offer market data from a public repository at https://github.com/fxcm/MarketData.

Tick data is available for free for some pairs. Other paid data is also available.

## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://python.org/)

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Git](https://git-scm.com) and [Python3](https://Python.org/) installed.

## :checkered_flag: Starting ##

```bash
# Clone this project
$ git clone https://github.com/javiergarciad/fx-data-downloader

# Access
$ cd fx-data-downloader

# Create a virtual environment using your preferred tool (e.g., venv, conda, etc.). For example, using venv:
$ python -m venv .venv

# Activate the virtual environment:
# On windows:
  $ .\env\Scripts\activate

# On Linux
  $ source env/bin/activate

# Installl the required dependencies from the requirements.txt file
$ pip install -r requirements.txt

```

Execute the script with the desired options. The available options are as follows:

- -d or --db: Run a new database, delete the old one if exist. This option is a boolean flag and defaults to False.
- -m or --mp: Enable the multiprocessing option. This option is a boolean flag and defaults to False.
- -t or --tk: Provide a list of tickets. This option accepts multiple values separated by spaces. If not provided, all tickets in the database will be updated.
- -s or --start-date: The date to start getting the data. Default to 2019-01-01 as this is the date FXCM is providing data from. Use format YYYY-MM-DD.
- -e or --end-date: The date to end the update. Default to the last day of last month. Use format YYYY-MM-DD.

Example usage:

```
python run.py -d -m -t EURUSD GBPUSD
```

This command will run the script with the database and multiprocessing options enabled, and the tickets set to "EURUSD" and "GBPUSD".

- If you don't provide the -t option, the script will default to updating all tickets available in the database.
- If you don-t provide a start date it will default to 2019-01-01.
- If you don't provide a end date it will default to the last day of last month from today.


## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/javiergarciad" target="_blank">Javier Garcia</a>

&#xa0;

<a href="#top">Back to top</a>
