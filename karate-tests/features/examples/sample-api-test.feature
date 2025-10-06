Feature: Sample API Test
  Background:
    * url 'https://jsonplaceholder.typicode.com'

  Scenario: Get a user by ID
    Given path 'users/1'
    When method GET
    Then status 200
    And match response.name == '#string'
    And match response.email == '#string'

  @smoke
  Scenario: Get all users
    Given path 'users'
    When method GET
    Then status 200
    And match response == '#array'
    And match each response == { id: '#number', name: '#string', email: '#string' }

  Scenario: Create a new user
    Given path 'users'
    And request { name: 'Test User', email: 'test@example.com' }
    When method POST
    Then status 201
    And match response.name == 'Test User'
    And match response.email == 'test@example.com'
