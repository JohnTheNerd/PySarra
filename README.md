# PySarra

A Python 3 application that can read from Sarracenia and relay the messages however you'd like. A Google Cloud relay processor is included for your convenience. It is also only tested on Linux.

This application consists of two modules and the main application, and one can tie them however they would like! It is also possible to easily create another processor or consumer which is just a Python script in the respective folder. Your filename will be the name, which can be specified in config.json.

**Processor:** You must define process() in your processor that accepts one argument (which is the entire message as a dictionary - check ECConsumer.py). Your processor will be imported as soon as the consumer runs and process() will be triggered for each message received, including the consumer name as 'consumer', the topic subscribed to as 'topic', and the full URL of the new file available as 'message'.

**Consumer:** You must put the following block of code somewhere at the top of your script, which will import your appropriate processor and assign it as processor. Now you can call `processor.process(message)` from anywhere and your processor will receive the message!

~~~~python
import os, sys, importlib
sys.path.insert(0, os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'), 'processors/'))
processor = importlib.import_module(task['processor'])
~~~~

## Notes

- To use the Google Cloud processor, you must:

  - have a working Google Cloud Platform account

  - change the project name (which is set as a global variable in the processor script itself) to your project name as created in GCP

  - pass in your Google Cloud credentials as an environment variable as described [right here](https://cloud.google.com/video-intelligence/docs/common/auth#authenticating_with_application_default_credentials) unless you are directly running this from a Compute Engine instance that already has access to the topic you are relaying the messages to.

- If regex is defined in config.json, it is tested with each incoming message, and if it is a match the entire message is processed.

- You can subscribe to any subtopics by using the . delimeter - for example to be notified of any changes under [http://dd.weather.gc.ca/alerts/cap/20180725](http://dd.weather.gc.ca/alerts/cap/20180725) can be tracked by using a topic value of `alerts.cap.20180725`.

## Usage

- Clone this repository.

- Install pika by running `pip3 install pika`.

- If needed, install the Google Cloud Pub-Sub library by running `pip3 install google-cloud-pubsub`.

- Edit config.json if necessary.

- Run main.py!
