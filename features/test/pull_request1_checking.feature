Feature: Pull request1 checking
  As registered user
  I want check all branch in repository
  So I create specific requests to GitHub API

  Scenario Outline: Create pull request with custom name
    Given I clean up repository by name "<repo_name>"
    Given I create repository with custom name "<repo_name>"
    When I extract repository name from repository response
    Then I assert repository name is "<repo_name>"
    Given I create commit in repository "<repo_name>"
    When I create new branch with name "<branch_name>" in repository "<repo_name>"
    Then I should see the branch "<branch_name>"
    Then I create new commit in branch in repository "<repo_name>" with branch name "<branch_name>"
    When I create new pull request1 with name "<branch_name>" in repository "<repo_name>" with default branch "master"
    Then I should see new pull request1 branch "<branch_name>" with default branch "master"
    Examples:
      | repo_name         | branch_name |
      | new_branch_repo_12 | first2       |
      | new_branch_repo_a2 | abc1232      |
      | new_branch_repo_A2 | qwerty2      |
