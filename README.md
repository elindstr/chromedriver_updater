# Chromedriver Updater: a python script to auto update selenium chromedriver

## Description

* user-defined parameters, e.g.: 
    <code>PACKAGE = 'chromedriver'
    OS = 'mac'
    PLATFORM = 'mac-x64'
    PATH = '/Users/elindstr/bin/chromedriver'</code>
* identifies local version of chrome using <code>import subprocess</code>
* accesses chrome driver [json endpoints](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json') file
* downloads driver based on parameters and saves it to path
