# Automated navigation and tests

You don't need this doc if you are using PA Autotest VirtualBox !!!

Using [Selenium over Python](https://selenium-python.readthedocs.io/getting-started.html) 

## Create a virtual environment

~~~
mkdir -p ~/venv
python -mvenv ~/venv/selenium
. ~/venv/selenium/bin/activate
~~~

Install dependencies
~~~
tools/install
~~~

Chrome and Chromedriver must be installed, done in the VM, [instructions](https://chromedriver.chromium.org/getting-started) here.

## Basics

SEE "examples" folder.

~~~
python -mexamples.screenshot
~~~

## As tests (with report)

SEE tests/test_00_example.py

We extend clasis BaseTest from pa_lib.

~~~
tools/tests_run
~~~

runs all files starting with "test" 

