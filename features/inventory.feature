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

# Scenario: List all inventory records
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "10" in the results
#     And I should see "table" in the results
#     And I should see "new" in the results
#     And I should see "5" in the results
#     And I should see "True" in the results
#     And I should not see "bottle" in the results

# Scenario: Search for dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for available
#     When I visit the "Home Page"
#     And I select "True" in the "Available" dropdown
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "sammy" in the results
#     And I should not see "leo" in the results

# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field
#     When I change "Name" to "Boxer"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Boxer" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "Boxer" in the results
#     And I should not see "fido" in the results
