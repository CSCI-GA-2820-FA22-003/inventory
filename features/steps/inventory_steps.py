######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Pet Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
import enum
import logging
from behave import given
from compare import expect

class Condition(enum.Enum):
        '''Definition of condition values'''
        NEW = 'new'
        REFURBISHED = 'refurbished'
        RETURN = 'return'



@given('the following inventory records')
def step_impl(context):
    """ Delete all Pets and load new ones """
    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/inventory"
    logging.info(rest_endpoint)
    context.resp = requests.get(rest_endpoint)
    # logging.info(context.resp)
    
    expect(context.resp.status_code).to_equal(200)
    for record in context.resp.json():
        # print(record)
        # logging.info(record['condition'])
        # logging.info(Condition(record['condition']).name)
        context.resp = requests.delete(f"{rest_endpoint}/{record['product_id']}/"+Condition(record['condition']).name)
        expect(context.resp.status_code).to_equal(204)

    #load the database with new pets
    
    for row in context.table:
        # logging.info(row)
        # logging.info(type(int(row['product id'])))
        payload = {
            "product_id": int(row['product id']),
            "name": row['name'],
            "condition": row['condition'],
            "quantity": int(row['quantity']),
            "active": row['active'] in ['True', 'true', '1']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
