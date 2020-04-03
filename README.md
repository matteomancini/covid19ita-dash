# A dashboard to monitor the spread of COVID-19 in Italy

![Dashboard screenshot](img/screenshot.png)

### What is it?

This is a dashboard written in Python using Dash. It can be run using Jupyter Lab or as a Flask-based web application.

### Using the dashboard in Jupyter Lab

To use the dashboard inside Jupyter Lab, it is necessary to install the [jupyterlab-dash extension](https://github.com/plotly/jupyterlab-dash).

### Running the web app locally

The easiest way is to clone this repository, create a virtual environment and install the required packages:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the actual web app:

```
python app.py
```

The dashboard can then be used in a browser pointing to link http://127.0.0.1:8050/ .