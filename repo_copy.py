from git import Repo
import os, shutil, argparse, sys
#from colorama import Fore

'''
This script use argparse, run 'python repo_copy.py --help' to have more information.

The main objective is to determine what kind of travis test should be run and makes the 
corresponding checkouts and merge. To do this

$TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                * For builds triggered by a PR this is the name of the branch targered by the PR.
                * For builds triggered by a TAG, this is the same as the name of the TAG (TRAVIS_TAG).
$TRAVIS_PULL_REQUEST_BRANCH: * For builds triggered by a PR this is the name of the branch origineted.
                             * For others, this is "" (empty string).
$TRAVIS_PULL_REQUEST:   * It is the number of PR.
                        * For PUSH is set to "false".        

If the build is triggered by a PR the TRAVIS_PULL_REQUEST_BRANCH will be the name 
of origin branch and if the build is triggered by a PUSH, TRAVIS_PULL_REQUEST_BRANCH 
will be an empty string.
'''
# Define some constants
constants = {
    "default_branch": "development",
    "master": "master",
    "pr": "PR",
    "push": "PUSH"
}

class DefaultBranchNotFound(Exception):
    pass

class DefaultBranchNotProvided(Exception):
    pass

class TravisTestDoesNotExist(Exception):
    pass

class MergeError(Exception):
    pass

class Color():
    '''
        Define the colors for function cprint.
    '''
    GREEN = "\033[1;32;40m"
    RED = "\033[1;31;40m"
    DEFAULT = "\033[0;37;40m"

def get_available_branches(repo):
    '''
        Return a list with the names of remotes branches in repo.
    '''
    branches = []
    
    for branch in repo.remotes.origin.refs:
        branches.append(branch.name.replace('origin/', ''))
    
    return branches

def get_available_tags(repo):
    '''
        Return a list with the names of tags in repo.
    '''
    return [tag.name for tag in repo.tags]

def check_default_branch(repo, default_branch):
    '''
        If default_branch is not provided raise DefaultBranchNotProvided.
        If default_branch is provided but not exist in repo return DefaultBranchNotFound.
        Else return True.
    '''
    # Check default branch is not an empty string
    if not default_branch:
        raise DefaultBranchNotProvided(f'Default branch was not provide. Exit excution.')
    # Get the branches in repo
    branches = get_available_branches(repo)

    # If default branch does not exist raise DefaultBranchNotFound
    if not (default_branch in branches):
        raise DefaultBranchNotFound(f'Default branch does not exist. Exit excution.')

def checkout(repo, branch):
    '''
        This function check if branch is in the repo, and then checkout. 
        The argument branch could be a tag.
        Return True if the checkout is successful and False if the branch or tag 
        does not exist in repo.
    '''
    # Get the remote branches names and tags names
    branches = get_available_branches(repo)
    tags = get_available_tags(repo)

    if branch in branches:
        response = repo.git.checkout(branch)
        cprint("Checkout " + str(repo.active_branch), color='GREEN')
        return True
    elif branch in tags:
        repo.git.checkout('tags/' + branch)
        cprint(f"Checkout tags/{branch}", color='GREEN')
        return True
    
    return False

def merge(repo, target, origin, default = constants['default_branch']):
    '''
        This function try to merge the origin branch into the target branch.
        If the target branch is not in the repo, try to merge into the default branch.
        If the origin branch is not in the report, the result is the checkout to target
        branch or default branch and return False.
        If there is any error with git.merge, for example merge conflics, raise MergeError.
        If the merge is succesful, return True.
    '''
    # Try checkout to origin like 'git checkout origin'
    o_check = checkout(repo, origin)
    # Try checkout to target like 'git checkout target'    
    t_check = checkout(repo, target)

    if not t_check:
        # If target does not exists, checkout to default
        checkout(repo, default)

    if o_check:
        # If origin exists, merge into default
        try:
            cprint(f"Merge {origin} into {repo.active_branch}.")
            response = repo.git.merge(origin)
            # This print out all the message about the merge.
            cprint(response)
            return True
        except Exception as error:
            raise MergeError(str(error))
    else:
        cprint(f"The origin branch: {origin} does not exist.")
        cprint(f"Not need to merge.")
        pass

    return False

def clone_repo(url, path):
    '''
        This function clone a repository form the url to the path.
        Return a Repo object.
        Raise and Exception if the repository could not be cloned.
    '''
    
    # Delete the repository, just to clone_from url and not get an error
    if os.path.exists(path):
        cprint(f"The directory {path} already exist. Will be delete.")
        shutil.rmtree(path)

    # Clone the repo
    try:
        cprint(f"Cloning {url}.")
        
        # Clone the master branch
        repo = Repo.clone_from(url=url, to_path=path)
        
        cprint("The repository was cloned successfully.", color='GREEN')

    except Exception as error:
        # If there is an error during the cloning raise an exception
        cprint(f"The repository could not be clone from the {url} to {path}.", color='RED')
        cprint(str(error), color='RED')
        raise Exception()

    return repo

def get_parse_args(args=None):
    '''
        This function implement the parse.
    '''

    parse = argparse.ArgumentParser(description='Clones a GitHub repository and proceeds to checkout and '
                                    'merge branches according to Travis-CI PR or PUSH test. '
                                    ''
                                    'If TARGET or ORIGIN are not provided, '
                                    'it will try to read it from Travis-CI environmental variables '
                                    'TRAVIS_BRANCH or TRAVIS_PULL_REQUEST_BRANCH. '
                                    ''
                                    'TARGET, ORIGIN and DEFAULT determines the Travis-CI test (PR or PUSH)'
                                    ''
                                    'If the test corresponds to PUSH, then'
                                    'checkout TARGET (if not possible, checkout DEFAULT branch). '
                                    ''
                                    'For PR test, the script will '
                                    'merge ORIGIN into TARGET '
                                    '(If not possible, it will merge ORIGIN into DEFAULT) '
                                    '(If not possible, it will checkout TARGET) ' 
                                    '(If not possible, it will checkout DEFAULT). '
                                    ''
                                    'If TARGET and ORIGIN branches are not defined, the execution exits.')
    
    # Define the optional and positiional arguments
    parse.add_argument('url', help='Repository URL.')
    parse.add_argument('-t', '--target-branch', dest='target', nargs='?', const=None, 
                        help='Target branch from PR or PUSH. Default value is the' 
                        ' enviroment variable TRAVIS_BRANCH.')
    parse.add_argument('-d', '--default-branch', dest='default', nargs='?', const=None, 
                        help='Default branch if the target branch does not exist.'
                        ' Default value is "development" or "master".')
    parse.add_argument('-o', '--origin-branch', dest='origin', nargs='?', const=None, 
                        help='Origin branch from PR. Default value is the enviroment variable'
                        ' TRAVIS_PULL_REQUEST_BRANCH.')

    # Return the variables
    return parse.parse_args(args)

def validate_args(args=None):
    '''
        This function check the arguments passsed in command-line options and 
        define if the current travis test is a PUSH or PR.
        The url of repository is a positional argument. The name of branches are optional
        arguments.
        Return a Namespace with repository url, target branch, origin branch, 
        default branch and travis test type.
    '''
    args = get_parse_args(args)
    # If default branch not passed set as constans["default_branch"]
    if args.default == None:
        args.default = constants['default_branch']

    # If target branch not passed set as TRAVIS_BRANCH enviroment variable
    if args.target == None:
        args.target = os.environ.get('TRAVIS_BRANCH')
        if args.target:
            cprint(f"env var TRAVIS_BRANCH found: '{args.target}'.")
        else:
            cprint(f"Not TARGET branch provided", color='RED')
    # If origin branch not passed set as TRAVIS_PULL_REQUEST_BRANCH enviroment variable
    if args.origin == None:
        args.origin = os.environ.get('TRAVIS_PULL_REQUEST_BRANCH')
        
        if args.origin:
            # If TRAVIS_PULL_REQUEST_BRANCH is set,
            # so the current travis test is 'PR'
            cprint(f"env var TRAVIS_PULL_REQUEST_BRANCH found: '{args.origin}'.")
        else: 
            # If TRAVIS_PULL_REQUEST_BRANCH isn't set,
            # so the current travis test is 'PUSH'
            cprint(f"No ORIGIN branch provided.", color='RED')
    # Set the test type
    if os.environ.get('TRAVIS_PULL_REQUEST') == 'false':
        args.test = constants['push']
    else: 
        args.test = constants['pr']


    return args

def cprint(string, color = Color.DEFAULT):
    '''
    This function print the argument string with color.
    The default value is WHITE, if the color argument is not
    an attribute of Color, the default value is used.
    '''
    color = getattr(Color, str(color).upper(), Color.DEFAULT)
    print(color + str(string) + Color.DEFAULT)

def get_path(url_address):
    '''
        Take an url address of a repository and return the last name without ".git".
        Example:
            url_address = https://github.com/openworm/org.geppetto.git
            return =>  org.geppetto
    '''
    path = url_address.split('/')[-1]
    return path.replace(".git", "")

def print_info(url, travis_type, target, origin, default):
    cprint("\nINFO")
    cprint("###################################")
    cprint(f"Repository url:      {url}.")
    cprint(f"Travis test mode:    {travis_type}.")
    cprint("-----------------------------------")
    if test_type == constants['pr']:
        cprint(f"Origin branch:       {origin}.")

    cprint(f"Target branch:       {target}.")
    cprint(f"Default branch:      {default}.")
    cprint("-----------------------------------\n")

def travis_pr(repo, target, origin, default):
    '''
        Try to merge the origin branch into the target.
        If target doesn't exists in repo, try to merge into default branch.
    '''
    
    # Check Default Branch
    check_default_branch(repo, default)
    # Try to merge origin_branch into target_branch
    return merge(repo, target, origin, default)

def travis_push(repo, target, default):
    '''
        Checkout to target branch, if it doesn't exist in repo checkout to default branch.
    '''
    # Check Default Branch
    check_default_branch(repo, default)
    # Try checkout to target branch like 'git checkout target_branch'
    target_check = checkout(repo, target)

    if not target_check:
        # If target branch does not exists
        return checkout(repo, default)
    return target_check

def travis_test_run(url_address, travis_type, target, origin, default):
    '''
        Run the corresponding TRAVIS test. For PUSH or PR.
    '''
    if not target and not origin:
        cprint("Target branch and origin branch were not provide. Exit execution.")
        return

    # Print some information
    print_info(url_address, travis_type, target, origin, default)
    
    # Define the directory name for the repository cloned
    clone_path = get_path(url_address)

    # Clone the repository
    repo = clone_repo(url_address, clone_path)
    cprint("-----------------------------------\n")

    if travis_type == 'pr':
        return travis_pr(repo, target, origin, default)
    elif travis_type == 'push':
        return travis_push(repo, target, default)
    else:
        raise TravisTestDoesNotExist(f"({travis_test} is not a valid Travis test type.)")

    # Close the repo and delete de variable
    repo.close()
    del repo
    
    # Delete the ".git"
    cprint(f"Deleting the '.git'.")
    os.chdir(clone_path)
    shutil.rmtree('.git')
    cprint("-----------------------------------\n")

def main():
    
    # Take the arguments from command-line and set the variables.
    data = validate_args(sys.argv[1:])
    clone_url = data.url
    target_branch = data.target
    origin_branch = data.origin
    default_branch = data.default
    test_type = data.test
    
    # Run the TravisCI test
    travis_test_run(test_type, repo, target_branch, origin_branch, default_branch)


if __name__ == "__main__":

    main()