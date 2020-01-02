# Snotel Project

<p align="center">
<img height="400" src="https://github.com/geomex/metstation/blob/master/figures/snotel_sites.jpeg">
</p>


Snotel Meteorlogical sites have provided water resource managers
viable data to estimate timing of runoff and also helped snow
sciencists better understand patterns and chnages in snow
dynamics.

## Getting Started

### Running the app locally

#### Using VIRTUALENV

We suggest you to create a separate virtual environment running
Python 3 for this app, and install all of the required
dependencies there. Run in Terminal/Command Prompt:

```
git clone https://github.com/geomex/metstation.git
cd metstation
python3 -m virtualenv venv
```

In UNIX system: 

```
source venv/bin/activate
```

In Windows: 

```
venv\Scripts\activate
```

To install all of the required packages to this environment, simply run:


```
pip install -r requirements.txt
```

and all of the required `pip` packages, will be installed, and
the app will be able to run.

#### Using Conda Environment

The other option is to use a conda environment, to do this you
will need to install anaconda or conda onto your computer. You
can following the steps found at the
[Anaconda Installation Site](https://docs.anaconda.com/anaconda/install/). 

Once you have anaconda installed you can run the following to
create the  anaconda environment and then activate it. 

```
1. conda env create -f environment.ymnl
2. conda activate metstation
```


#### Using the Webcrawler

Once in proper environment, you will neeed to make use of the
webcrawler by runninG the following in the command line and
follow the questions prompted.

```
python snotel_webcrawler
```



