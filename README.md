# Python script to checkout and merge repository branches based on Travis-CI test

## Summary
When runnig a ci test from Travis, use the following script to automate reposity cloning, checkout and merge. The required operations and branches will be inferred from ENV variables such as `TRAVIS_BRANCH`.
```bash
python3 copy_.py 'https://github.com/MyOrg/myrepo.git'
```

## Requirements
- Python >= 3.4
- `pip install -r requitements.txt`

## IMPORTANT
Set environmental variable `ENV DEFAULT_BRANCH` before running the script so that we have a branch to fallback.

## Description and Example

- Uses [GitPython](https://gitpython.readthedocs.io/en/stable/).
- Works with either [Travis Environment Variables](https://docs.travis-ci.com/user/environment-variables/) or command line arguments.
### Travis-CI environmental variables
- TRAVIS_BRANCH
  - For *PUSH* or builds not triggered by a *PR* this is the name of the branch.
  - For builds triggered by a *PR* this is the name of the branch targered by the *PR*.
  - For builds triggered by a *TAG*, this is the same as the name of the *TAG*.
- TRAVIS_PULL_REQUEST_BRANCH
  - For builds triggered by a *PR* this is the name of the branch origineted.
  - For others, this is "" (empty string).
- TRAVIS_PULL_REQUEST
  - It is the number of *PR*.
  - For *PUSH* is set to "false".
NOTE: The default branch is set to `'master'` if the environmental variable **DEFAULT_BRANCH** is not set.
### Examples
- With environmental variables
```bash
python3 copy_.py 'https://github.com/MyOrg/myrepo.git'
```
- With command line arguments
```bash
python3 copy_.py 'https://github.com/MyOrg/myrepo.git' -o 'feature/32' -t 'development' -d 'master' 
```
- With script
```python
# Instantiate a TravisRepoAction Object
travis_repo = TravisRepoAction(url='https://github.com/MyOrg/myrepo.git'',
                            path='the/path/to/clone',
                            clone_repo=True,
                            target_branch='development',
                            origin_branch='feature/32',
                            default_branch='master',
                            action_type='pr')

# Set your account's identity (name and email)
travis_repo.set_credentials()

# Call the method run to execute the actions corresponding with action_type.
travis_repo.run()
```

**NOTES**
- `url` is the only parameter require.
- If `path` is not passed, it will be set to `REPOSITORY_NAME`.
- If `clone_repo` argument is `True` the repository will be clone when the `TravisRepoAction` object is intantiated, the default value is `False`.
- If `target_branch` and `origin_branch` are not defined, then Travis-CI **DEFAULT ENVIRONMENT VARIABLES** are checked.
- The `default_branch` and `action_type` have as default value `'master'` and `'push'`, respectively.
