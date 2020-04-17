# testing
## Summary
The aims of this module is to handle git repositories to clone them form url, makes checkouts and merges. Specifically, the module address the actions for **PUSH** and **PULL REQUEST**.

A PUSH requires a target branch, and a default branch in case the target branch doesn't exist in the repository, and the actions are:
* Clone the repository.
* Checkout to target branch, if doesn't exist checkout to default branch.

A PULL REQUEST (PR) requires a target branch and an origin branch, and a default branch in case the target branch doesn't exist in the repository. The actions for a PR are:
* Clone the repository.
* Check that origin branch and target branch exist:
    * If both branches exist, merge origin branch into target branch.
    * If only origin branch exists, merge origin branch into default branch.
    * If only target branch exists, checkout to target branch.
    * If neither of the two branches exist, exit.

## Description and Example

The python script file **copy_.py** use the library [GitPython](https://gitpython.readthedocs.io/en/stable/) to interact with git repositories. The necessary Python packages are in file **requirements.txt**.

The **copy_.py** could also work with Travis Environment Variables to determine the name of branches and if it's a **PUSH** or a **PR**. The [DEFAULT TRAVIS ENVIRONMENT VARIABLES](https://docs.travis-ci.com/user/environment-variables/#default-environment-variables) used are:

**TRAVIS_BRANCH:** 
* For *PUSH* or builds not triggered by a *PR* this is the name of the branch.
* For builds triggered by a *PR* this is the name of the branch targered by the *PR*.
* For builds triggered by a *TAG*, this is the same as the name of the *TAG*.

**TRAVIS_PULL_REQUEST_BRANCH:**
* For builds triggered by a *PR* this is the name of the branch origineted.
* For others, this is "" (empty string).

**TRAVIS_PULL_REQUEST:**
* It is the number of *PR*.
* For *PUSH* is set to "false".

If the names of branches or the action type (PUSH or PR) aren't provided, they will be found in the environment variables described above.

Finally, the **copy_.py** also use the library `argparse` to allow the command-line arguments. Run `python copy_.py --help` for more information.

### Examples:

```python
    # Instantiate a TravisRepoAction Object
    travis_repo = TravisRepoAction(url='https://github.com/USERNAME/REPOSITORY_NAME.git',
                                path='the/path/to/clone',
                                clone_repo=True,
                                target_branch='target_name',
                                origin_branch='origin_name',
                                default_branch='default_name',
                                action_type='action_type')

    # Call the method run to execute the actions corresponding with action_type.
    travis_repo.run()
```

In the example above the `url` is the only parameter require, the other parameters are optional. 
If `path` argument is not passed, will be set as `'REPOSITORY_NAME'`.
If `clone_repo` argument is `True` the repository will be clone when the `TravisRepoAction` object is intantiated, the default value is `False`.
If `target_branch` and `origin_branch` arguments aren't passed, the **DEFAULT TRAVIS ENVIRONMENT VARIABLES** are checked.
The `default_branch` and `action_type` have as default value `'master'` and `'push'`, respectively.


Also you can run the actions for PUSH or PR directly, as shown in the following example: 

```python
    # Instantiate a TravisRepoAction Object
    travis_repo = TravisRepoAction(url='https://github.com/USERNAME/REPOSITORY.git',
                                target_branch='target_name',
                                default_branch='default_name')

    # Call the method push to execute the actions corresponding with PUSH.
    travis_repo.push()
```

There is also a `pr` method to execute the PR actions. 
In this example the `clone_repo` argument has the default value `False`, so the repository is cloned when the method `push` is called. The same is valid for methods `run` and `pr`.


