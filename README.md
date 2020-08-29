# Title

**Item Catalog Project of Udacity Full Stack Web Developer Nanodegree**


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.



## Introduction
A description and purpose of the script is shown below.
Then requirements needed to run the script is discussed.
Followed immediately by the pre-requisites required.
The next step would describe a step by step guide.
on how to set up the project.
Thereafter is a description of how,.
to clone the _app_ and retreive the files.
Finally, the command lines to run the project is shown.

## Description
This python app uses flask framework to connect with our database logic snd the clients,.
a version1 of the catalog app for datafrica website.
The app would provide a digital catalog to users for use in prducing online catalogs and ebooks, bronchures that can be shared and embeded into websites of the user.
It provides reports to three different queries to the database.
The results of the queries are formatted and presented in the users [account]_( http://account.datafrica.com)_.
Here are example of reports in the users account answered by the app.
1. Create, edit and delete category?.
2. Create, edit and delete items?.
3. Create, edit and delete flipbook from the Items?.

The app has clients for receiving inputs from users and resource access control.
It also provide access to APIs for developers to access resources offered by the app..



### Prerequisites

What things you need to install the software

## Requirements
* database_setup file
* Vagrant
* VirtualBox
* Vagrantfile

## Project environment
* Python3
* Sqlalchemy
* Flask
* jQuery library
* Boostrap library
* Oauth2 library


### Installing

A step by step series of how to get a development env running

### Instructions on how to set up and run my Project.
#### How to create the news database..
* Install VirtualBox
 * Download it [here](https://www.virtualbox.org/wiki/
   Download_Old_Builds_5_1)
* Install Vagrant
 * It is a software that runs the virtual machine.
 * To [download](https://www.vagrantup.com/)
 * Here is a zipped [file](https://s3.amazonaws.com/
   video.udacity-data.com/topher/2018/April/
   5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)
   to automate VirtualBox configuration.

### Start the virtual machine
From your terminal inside the vagrant subdirectory.
Run the command ```vagrant up``` to cause Vagrant to.
download the Linux operating system and install it.
When installation is complete,.
you will get your shell prompt back.
At this point run ```vagrant ssh```,.
to log in to the newly installed Linux VM.

#### Download the data
* [Download](https://github.com/k0f1/Catalog-App.git).
* Unzip the file.
 or ,.
In your terminal [clone](https://github.com/k0f1/Catalog-App.git).
* Start vagrant inside the vagrant directory with vagrant up followed by vagrant ssh.



## Instructions on how to run the script
* cd into the vagrant shared directory,. then
  * cd into the directory containing the script
* Run the command ```python3 report.py```
* Use the command ```python3 database_setup.py``` to start the database.
* ```pyhton3 lotsofitems.py``` — script to populate the database
* ```python3 application.py``` — starts runs the app.
* Open your client and enter ```http://localhost:8000```


### Is it in good shape
The code status is error free on pycodestyle test.



### Collaboration


## Contributing

Please read [CONTRIBUTING.md](https://github.com/k0f1/Catalog-App.git/contributing.md) for details on our code of conduct, and the process for submitting pull requests to us.


See also the list of [contributors](https://github.com/k0f1/Catalog-App.git/contributors) who participated in this project.

### TODO list:
* Logout not showing.
* Errors on edit page
* Item image processing - not showing to client
* API README.md page
* Facebook, Linkedin, Amazon, Microsoft, Paypal Oauth2
* Running the app on https

### ssl certficate
* Use the link [here](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-18-04)
* If successful, go to your account in AWS and enable custom HTTPS port 443 and you web app should be accessible live.



### License information
Copyright (c) 2020.

Permission is hereby granted, free of charge,.
to any person obtaining a copy of this.
software and associated documentation files (the "Software"),.
to deal in the Software without restriction,.
including without limitation the rights to use,.
copy, modify, merge, publish, distribute,.
sublicense, and/or sell copies of the Software,.
and to permit persons to whom the Software is furnished to do so,.
subject to the following conditions:.

The above copyright notice and this permission.
notice shall be included in all copies or.
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS",.
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,.
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,.
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR.
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,.
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,.
TORT OR OTHERWISE, ARISING FROM,.
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR.
THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Acknowledgments

* Hat tip to anyone whose code was used
* Lorenzo Brown - for Oauth backend and front end code.
* Steve Wooding - for optional image management at the backend
* etc
* How To Secure Apache with Let's Encrypt on Ubuntu 18.04 [here](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-18-04)
