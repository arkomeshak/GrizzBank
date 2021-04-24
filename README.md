# GrizzBank Installation Guide

## Requirements:

- Python 3.6 or newer (3.9 preferred)
- MySQL Server 8.0 or newer
- Latest version of PIP python package manager
- Latest version of pipenv virtual environment manager (optional)
- The following python packages
  - Django 3.17 or newer
  - mysqlclient 2.0.3 or newer

## Instructions:

1. Clone this repository to a location on the machine you desire to run GrizzBank on
   - The cloned repo root directory will be referred to as *GrizzBankDir*
2. Ensure MySQL Server 8.0 or newer is installed.
3. Create a new database within the server titled **grizz_bank** 
  - MySQL command: ``create database if not exists grizz_bank;``
4. Install required python packages
5. open a terminal and cd into GrizzBankDir.
   
### Installation 6-7 *using pipenv*

6. Run the command to install required python packages: ``pipenv install``
7. use the command ``pipenv shell`` to enter the pipenv virtual environment.

### Installation 6-7 *without pipenv*

6. Use pip, or a virtual environment to install the required python packages.
7. Enter the virtual environment, or simply use your global python interpreter if pip was used.

### *Remaining instructions require an env with required packages*

8. 
9. 
10. 


