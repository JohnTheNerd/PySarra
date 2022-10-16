# PySarra

A Python application that can read from Sarracenia and relay the messages however you'd like. It is designed to be significantly simpler than the official client, and is meant for people who don't need all the bells and whistles. It is only tested on Linux, and does not seem to work on macOS.

To create a processor, you must define process() in your processor that accepts one argument which is a dictionary with keys of `topic` and `message`. `message` is the full URL of the file that is now available under the Environment Canada datamart. A Google Cloud relay processor is included as an example.

## Notes

- To use the Google Cloud processor, you must:

  - have a working Google Cloud Platform account

  - change the project name to your project name as created in GCP

  - pass in your Google Cloud credentials as an environment variable as described [right here](https://cloud.google.com/video-intelligence/docs/common/auth#authenticating_with_application_default_credentials) unless you are directly running this from a Compute Engine instance that already has access to the topic you are relaying the messages to.

## Usage

- Clone this repository.

- Install all requirements by running `pip3 install -r requirements.txt`

- Edit config.json as necessary. Tasks is a list of dictionaries, where each dictionary has entries of `topic`, `regex`, and `processor`.

    - `processor` is the filename of your processor, without the `.py`.

    - You can subscribe to any `topic`s by using the . delimeter - for example to be notified of any changes under [http://dd.weather.gc.ca/alerts/cap/20180725](http://dd.weather.gc.ca/alerts/cap/20180725) can be tracked by using a topic value of `alerts.cap.20180725`. Topic subscriptions do not work for files, you should use a regex to filter at the filename-level. If you have a better solution, please feel free to let me know or create a pull request!

    - `regex` is optional. If it is defined, it is tested with each incoming message and the processor is only called if it is a match.

- Run main.py!
