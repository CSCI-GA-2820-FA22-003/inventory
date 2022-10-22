<h1 align="center"> NYU DevOps /Inventory </h1>
<h4 align="center"> An Inventory Microservice </h4>
<p align=center>
<img src="Images/inventory.png" alt="isolated"/>
</p>
<h4 align="center">



[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

<h4 align="center">
Inventory is a RESTFul microservice in the eCommerce application

## 

## :star: About Us

The Inventory resource is an integral micro-service of the eCommerce application. This micro-service is used to efficiently organize and manage products in the inventory for the proper functioning of the eCommerce application.

## :mag: Overview

The project's `/service` folder contains `models.py` file for the model and `routes.py` file for the service. The `/tests` folder has `test_models.py` and `test_routes.py` to test `models.py` and `routes.py` separately. The `/tests` folder also contains `factories.py` which can be used to generate a random Inventory record.


## :computer: Setup

To run this project ensure you have [docker](https://docs.docker.com/engine/install/) installed and running in your local machine. Then clone this repository and navigate to the github repository while opening in Visual Studio Code. Then in the terminal type `flask run` and copy the HTTP URL into your web browser or use the Postman collection [here](https://drive.google.com/file/d/1wSYoq8DPg0hr0spHzS9AxRHpN-LQKhzt/view?usp=sharing) to test the application.

## :open_file_folder: Contents

The project contains the following:

```text
.gitignore          - this will ignore git files and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
├── test_routes.py  - test suite for service routes
└── factories.py    - used to generate infinite number of random inventory record
```

## :memo: Schema

Below are the attributes of the inventory table

```
- product_id: int: pk
- name: str
- condition: enum {"new", "refurbished", "return"}: pk (default: new)
- quantity: int (default: 0)
- reorder_quantity: int (default: 0)
- restock_level: int (default: 0)
- active: boolean (used to indicate soft deletes)
- created_at: datetime
- updated_at: datetime
```

## :golf: Endpoints

#### `POST /inventory`

Create an inventory record.

#### Request body
```
{
    "product_id": 2,
    "condition": "return",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
```
{
    "product_id": 2,
    "name": "laptop"
}
```
The fields `condition`, `quantity`, `reorder_quantity` and `restock_level` are optional. If not passed, they assume default values of `NEW`, `0`, `0` and `0` respectively.

#### Response
Created record
```
{
    "product_id": 2,
    "condition": "return",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
The created record is returned in the response.

#### `GET /inventory/{product_id}`

#### Request

```
{
    "product_id": 2,
    "condition": "new"
}
```

#### Response
```
{
    "product_id": 2,
    "condition": "new",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
The record that matches the keys `product_id` and `condition` is returned in the response.

#### `GET /inventory`

List all inventory records.

#### Response
```
[
    {
	"condition": "return",
	"name": "laptop",
	"product_id": 2,
	"quantity": 20,
	"reorder_quantity": 15,
	"restock_level": 3
    }
]
```
The list of inventory records is returned in the response.

#### `PUT /inventory/{product_id}`

Update an inventory record.

#### Request
```
{
    "product_id": 2,
    "condition": "new",
    "quantity": 2,
    "reorder_quantity": 1,
    "restock_level": 3
}
```
Find an inventory record by `product_id` and `condition`. The fields `quantity`, `reorder_quantity`, `restock_level` and `name` are updateable and optional.

#### Response
```
{
    "product_id": 2,
    "condition": "new",
    "name": "laptop",
    "quantity": 2,
    "reorder_quantity": 1,
    "restock_level": 3
}
```
Update the fields of existing record with the passed values. Return the updated record in the response.

#### `DELETE /inventory/{product_id}`

Delete inventory record.

#### Request
```
{
    "product_id": 2,
    "condition": "new"
}
```

#### Response
```
{
    "product_id": 2,
    "condition": "new",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
The record that matches the keys `product_id` and `condition` is returned in the response.

## :wrench: Running Tests

Tests can be run using nosetests. Just type in `nosetests tests` in your terminal to check if all tests are being satisfied and to identify the code coverage.

## :sound: License

Licensed under the Apache License. See [LICENSE](LICENSE)

