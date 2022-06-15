## ModdingCode Backend
This project contains the serverless backend system of the ModdingCode platform. The code is divided into two folders `base` folder which contains the whole infrastructure, and the `logic` folder which holds the logical implementation of the lamdas being used by the defined entities on the infrastructure.

### Installation
This guide will not touch on deploying the application to an AWS account since one may incur costs for allocating the resources but instead, focus on running the automatic __unit tests__. The necessary libraries to execute them can be installed by using the virtual environment that `poetry` provides. First, you need to install poetry, you will need python version 3.8 for that, and placing your terminal in the project root folder, run the following command:
```
    pip3 install -r requirements.txt
```

Then you need to create and install the dependencies for the logic folder, you may run the following command:
```
    poetry install
```

### Testing
To run the __unit tests__ you need to place your terminal on the `logic` folder level, then set the virtual environment with the following command.
```
    poetry shell
```
Now you can run the unit test with the following command
```
    pytest
```

##### Cheers!