Feature: Branch checking
  As registered user
  I want check all branch in repository
  So I create specific requests to GitHub  API

  Scenario Outline: Create branch with custom name
    Given I clean up repository by name "<repo_name>"
    Given I create repository with custom name "<repo_name>"
    When I extract repository name from repository response
    Then I assert repository name is "<repo_name>"
    Given I create commit in repository "<repo_name>"
    When I create new branch with name "<branch_name>" in repository "<repo_name>"
    Then I should see the branch "<branch_name>"
    Examples:
      | repo_name         | branch_name |
      | new_branch_repo_1 | first       |
      | new_branch_repo_a | abc123      |
      | new_branch_repo_A | qwerty      |
