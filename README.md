# Market place - electronics store

Inspired by Technodom.

## Goal
The main aim of the project is to represent an online platform for sale with quick and understandable requests.

## APPS
The market place consists of 4 apps and one package with general constants and other things.

* auth_
* core
* market
* payments

## Description
**“auth_”** application represents requests related to user authentication.

 **“core”** includes basic models, queries that form the basis of an online store. 

**“market”** consists of goods with certain characteristics, properties complementary to the product, as well as the integration of the user directly with the system by giving feedback.

**“payments”** application speaks for itself, it provides endpoints that help to order the delivery of a certain item.

It’s also used popular packages that put together a framework for the entire application.


## Draft guidlines

1. Install django project
2. Create, configure and activate virtual environment
3. Install all packages by the following command
```bash
pip install -r requirements.txt
```
4. Create a table with fields
```bash
python manage.py migrate
```
5. Enjoy!
