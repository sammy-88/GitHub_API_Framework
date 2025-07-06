Feature: Repository checking
  As registered user
  I want check all repository functions
  So I create specific requests to GitHub  API

  Scenario Outline: Create repository with custom name
    Given I clean up repository by name "<repo_name>"
    Given I create repository with custom name "<repo_name>"
    When I extract repository name from repository response
    Then I assert repository name is "<repo_name>"
    Examples:
      | repo_name |
      | abc123   |
      | qwe456   |
      | asd789   |
