Feature: The inventory store service back-end
    As a Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all my inventory records

Background:
    Given the following inventory records
        | product id  | name     | condition    | quantity | active  | 
        |          1  | table    | new          | 10       | True    | 
        |          2  | chair    | refurbished  | 3        | True    | 
        |          1  | table    | refurbished  | 5        | True    | 
        |          3  | board    | new          | 2        | True    | 
        |          4  | mobile   | return       |1         | False   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "product id" to "10"
    And I select "new" in the "condition" dropdown
    And I set the "name" to "table"
    And I set the "quantity" to "5"
    And I select "True" in the "active" dropdown
    And I press the "create" button
    Then I should see the message "Success"
    When I copy the "product id,condition" combined field
    And I press the "clear" button
    Then the "product id" field should be empty
    And the "name" field should be empty
    And the "condition" field should be empty
    And the "quantity" field should be empty
    And the "active" field should be empty
    When I paste the "product id,condition" combined field
    And I press the "read" button
    Then I should see the message "Success"
    And I should see "10" in the "product id" field
    And I should see "new" in the "condition" dropdown
    And I should see "table" in the "name" field
    And I should see "5" in the "quantity" field
    And I should see "True" in the "active" dropdown

Scenario: List all inventory records
    When I visit the "Home Page"
    And I press the "clear" button
    And I press the "search" button
    Then I should see the message "Success"
    And I should see "1" in the results
    And I should see "chair" in the results
    And I should see "refurbished" in the results
    And I should see "10" in the results
    And I should see "true" in the results
    And I should not see "bottle" in the results

Scenario: Search for record 
    When I visit the "Home Page"
    And I press the "clear" button
    And I set the "product id" to "1"
    And I select "new" in the "condition" dropdown
    And I press the "search" button
    Then I should see the message "Success"
    And I should see "table" in the results
    And I should see "10" in the results
    And I should not see "chair" in the results
    And I should not see "board" in the results

Scenario: Search for record having quantity greater than 5
    When I visit the "Home Page"
    And I press the "clear" button
    And I set the "quantity" to "3"
    And I select ">=" in the "operator" dropdown
    And I press the "search" button
    Then I should see the message "Success"
    And I should see "table" in the results
    And I should see "chair" in the results
    And I should not see "board" in the results

Scenario: Update a Record
    When I visit the "Home Page"
    And I press the "clear" button
    And I set the "product id" to "1"
    And I select "new" in the "condition" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "table" in the "name" field
    And I should see "new" in the "condition" dropdown
    And I should see "True" in the "active" dropdown
    When I select "False" in the "active" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "product id,condition" combined field
    And I press the "Clear" button
    And I paste the "product id,condition" combined field
    And I press the "search" button
    Then I should see the message "Success"
    And I should see "1" in the results
    And I should see "table" in the results
    And I should see "new" in the results
    And I should see "false" in the results
    And I should not see "board" in the results

 Scenario: Delete a Record
    When I visit the "Home Page"
    And I press the "clear" button
    And I select "False" in the "active" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "mobile" in the "name" field
    And I should see "return" in the "condition" field
    When I copy the "product id,condition" combined field
    And I press the "clear" button
    And I paste the "product id,condition" combined field
    And I press the "delete" button
    Then I should see the message "Product has been Deleted!"
    When I press the "clear" button
    And I press the "search" button
    Then I should see the message "Success"
    And I should not see "mobile" in the results

Scenario: Checkout a Record
    When I visit the "Home Page"
    And I press the "clear" button
    And I set the "product id" to "2"
    And I select "refurbished" in the "condition" dropdown
    And I press the "read" button
    Then I should see the message "Success"
    And I should see "chair" in the "name" field
    And I should see "3" in the "quantity" field
    When I copy the "product id,condition" combined field
    And I press the "clear" button
    And I paste the "product id,condition" combined field
    And I set the "ordered quantity" to "2"
    And I press the "checkout" button
    Then I should see the message "Product has been checked out from Inventory!"
    When I set the "product id" to "2"
    And I select "refurbished" in the "condition" dropdown
    And I press the "read" button
    Then I should see the message "Success"
    And I should see "1" in the "quantity" field

Scenario: Reorder a Record
    When I visit the "Home Page"
    And I press the "clear" button
    And I set the "product id" to "1"
    And I select "new" in the "condition" dropdown
    And I press the "read" button
    Then I should see the message "Success"
    And I should see "table" in the "name" field
    And I should see "10" in the "quantity" field
    When I copy the "product id,condition" combined field
    And I press the "clear" button
    And I paste the "product id,condition" combined field
    And I set the "ordered quantity" to "5"
    And I press the "reorder" button
    Then I should see the message "Product has been reordered!"
    When I set the "product id" to "1"
    And I select "new" in the "condition" dropdown
    And I press the "read" button
    Then I should see the message "Success"
    And I should see "15" in the "quantity" field