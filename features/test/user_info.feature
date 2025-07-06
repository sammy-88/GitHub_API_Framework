Feature: Check user data
  As registered user
  I want check all user data
  So I create specific requests to GitHub  API

  Scenario: Check user login
    Given I receive user data info request
    When I compare user login with saved
    Then I assert that user login as expected

  Scenario Outline: Check user custom login
    Given I receive user data info request
    When I compare user login with custom "<user_login>"
    Then I assert that user login as expected
    Examples:
      | user_login |
      | builuk     |
      | sammy-88   |
#  второй тест всегда будет падать
