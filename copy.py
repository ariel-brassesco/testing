from git import Repo
import os, shutil, argparse
from colorama import Fore

'''
This script use argparse, run 'python copy.py --help' to have more information.

The main objective is to determine what kind of travis test should be run and makes the 
corresponding checkouts and merge. To do this

$TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                * For builds triggered by a PR this is the name of the branch targered by the PR.
                * For builds triggered by a TAG, this is the same as the name of the TAG (TRAVIS_TAG).
$TRAVIS_PULL_REQUEST_BRANCH: * For builds triggered by a PR this is the name of the branch origineted.
                             * For others, this is "" (empty string).

So, if the build is triggered by a PR the TRAVIS_PULL_REQUEST_BRANCH will be the name 
of origin branch and if the build is triggered by a PUSH TRAVIS_PULL_REQUEST_BRANCH 
will be an empty string.
'''
# Define some constants
constants = {
    "default_branch": "development",
    "pr": "PR",
    "push": "PUSH"
}

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
        cprint(response, 'GREEN')
        cprint("The current branch is " + str(repo.active_branch), color='YELLOW')
        return True
    elif branch in tags:
        repo.git.checkout('tags/' + branch)
        cprint(f"Checking out tags/{branch}", color='YELLOW')
        return True
    
    return False


def merge(repo, target, origin, default = constants['default_branch']):
    '''
        This function try to merge the origin branch into the target branch.
        If the target branch is not in the repo, try to merge into the default branch.
        If the origin branch is not in the report, the result is the checkout to target
        branch or default branch and return False.
        If there is any error with git.merge, for example merge conflics, raise it and
        return False.
        If the merge is succesful, return True.
    '''
    # Try checkout to origin like 'git checkout origin'
    o_check = checkout(repo, origin)
    # Try checkout to target like 'git checkout target'    
    t_check = checkout(repo, target)

    if not t_check:
        # If target does not exists, checkout to default
        cprint(f"The target branch: {target} does not exist.", color='YELLOW')
        cprint(f"Checkout to default branch: {default}.", color='YELLOW')
        checkout(repo, default)

    if o_check:
        # If origin exists, merge into default
        try:
            cprint(f"Start merging {origin} into {repo.active_branch}.", color='YELLOW')
            response = repo.git.merge(origin)
            # This print out all the message about the merge.
            cprint(response)
            cprint("Finish the merge.", color='GREEN')
            return True
        except Exception as error:
            cprint(str(error), color='RED')
    else:
        cprint(f"The origin branch: {origin} does not exist.", color='YELLOW')
        cprint(f"Not need to merge.", color='YELLOW')

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
        cprint(f"Start cloning {url}.", color='YELLOW')
        
        # Clone the master branch
        repo = Repo.clone_from(url=url, to_path=path)
        
        cprint("The repository was cloned successfully.", color='GREEN')
        cprint("The current branch is " + str(repo.active_branch), color='YELLOW')
        cprint(f"The directory {path} was created.\n")

    except Exception as error:
        # If there is an error during the cloning raise an exception
        cprint(str(error), color='RED')
        cprint(f"The repository could not be clone from the {url} to {path}.", color='RED')
        raise Exception()

    return repo


def validate_args():
    '''
        This function check the arguments passsed in command-line options and 
        define if the current travis test is a PUSH or PR.
        The url of repository is a positional argument. The name of branches are optional
        arguments.
        Raise and exception if the arguments are incorrect.
        Return a Namespace with repository url, target branch, origin branch, 
        default branch and travis test type.
    '''

    parse = argparse.ArgumentParser(description='This script takes as inputs the URL repository, '
                                    'and the branches TARGET, ORIGIN and DEFAULT, and determine if the travis'
                                    ' test correspond a PR or PUSH. Default values are taking from environment'
                                    ' variables TRAVIS_BRANCH and TRAVIS_PULL_REQUEST_BRANCH for TARGET and'
                                    ' ORIGIN branches, respectively. DEFAULT branch will be "development" or'
                                    ' "master", if no value is passed. If the current travis test correspond '
                                    'to a PUSH, then the script makes a checkout to TARGET branch, if not possible '
                                    'makes a checkout to DEFAULT branch. For a PR test, the script makes a merge '
                                    'between TARGET and ORIGIN branch, if not possible try to merge DEFAULT and '
                                    'ORIGIN branch, and finally try to checkout to TARGET or DEFAULT branch.'
                                    ' If TARGET and ORIGIN branches have not value, the execution finish.')
    
    # Define the optional and positiional arguments
    parse.add_argument('url', help='Repository URL.')
    parse.add_argument('-t', '--target-branch', dest='target', help='Target branch from'
                        ' PR or PUSH. Default value is the enviroment variable TRAVIS_BRANCH.')
    parse.add_argument('-d', '--default-branch', dest='default', help='Default branch if'
                        'the target branch does not exist. Default value is "development"'
                        ' or "master".')
    parse.add_argument('-o', '--origin-branch', dest='origin', nargs='?', const=None, 
                        help='Origin branch from PR. Default value is the enviroment variable'
                        ' TRAVIS_PULL_REQUEST_BRANCH.')

    # Get the variables
    args = parse.parse_args()

    # If default branch not passed set as constans["default_branch"]
    if args.default == None:
        args.default = constants['default_branch']

    # If target branch not passed set as TRAVIS_BRANCH enviroment variable
    if args.target == None:
        cprint("No target_branch provides.")
        args.target = os.environ.get('TRAVIS_BRANCH')
        
        if args.target:
            cprint(f"Found env variable TRAVIS_BRANCH with value '{args.target}'.")
        else:
            cprint(f"Not found env variable TRAVIS_BRANCH.", color='YELLOW')


    
    if args.origin:
        # Set the current travis test as 'PR'
        args.test = constants['pr']
    else:
        # If origin branch not passed set as TRAVIS_PULL_REQUEST_BRANCH enviroment variable
        cprint("No origin_branch provides.")
        args.origin = os.environ.get('TRAVIS_PULL_REQUEST_BRANCH')
        
        if args.origin:
            # If TRAVIS_PULL_REQUEST_BRANCH is set,
            # so the current travis test is 'PR'
            args.test = constants['pr']
            cprint(f"Found env variable TRAVIS_PULL_REQUEST_BRANCH with value '{args.origin}'.")
        else: 
            # If TRAVIS_PULL_REQUEST_BRANCH isn't set,
            # so the current travis test is 'PUSH'
            args.test = constants['push']
            cprint(f"Not found env variable TRAVIS_PULL_REQUEST_BRANCH.", color='YELLOW')

    return args


def cprint(string, color = None):
    '''
    This function print the argument string with color.
    The default value is WHITE, if the color argument is not
    an attribute of Fore, the default value is used.
    '''
    color = getattr(Fore, str(color), Fore.WHITE)
    print(color + str(string) + Fore.RESET)


def get_path(url_address):
    '''
        Take an url address of a repository and return the last name without ".git".
        Example:
            url_address = https://github.com/openworm/org.geppetto.git
            return =>  org.geppetto
    '''
    path = url_address.split('/')[-1]
    return path.replace(".git", "")


def main():
    
    # Take the arguments from command-line and set the variables.
    data = validate_args()
    clone_url = data.url
    target_branch = data.target
    origin_branch = data.origin
    default_branch = data.default
    test_type = data.test

    if not target_branch and not origin_branch:
        cprint("Exit execution.", color='YELLOW')
        return

    # Print some information
    cprint("\nINFO")
    cprint("###################################")
    cprint(f"Repository url:      {clone_url}.")
    cprint(f"Travis test mode:    {test_type}.")
    cprint("-----------------------------------")
    if test_type == constants['pr']:
        cprint(f"Origin branch:       {origin_branch}.")

    cprint(f"Target branch:       {target_branch}.")
    cprint(f"Default branch:      {default_branch}.")
    cprint("-----------------------------------\n")
    
    # Define the directory name for the repository cloned
    clone_to_path = get_path(clone_url)

    # Clone the repository
    repo = clone_repo(clone_url, clone_to_path)
    cprint("-----------------------------------\n")

    if test_type == constants['pr']:
        # Try to merge origin_branch into target_branch
        merge(repo, target_branch, origin_branch, default_branch)
    else: 
        # If test_type=='PUSH'
        # Try checkout to target_branch like 'git checkout target_branch'
        target_check = checkout(repo, target_branch)

        if not target_check:
            # If target_branch does not exists
            cprint(f"The target branch: {target_branch} does not exist.", color='YELLOW')
            cprint(f"Checkout to default branch: {default_branch}.", color='YELLOW')
            checkout(repo, default_branch)
        
    # Close the repo and delete de variable
    repo.close()
    del repo
    
    # Delete the ".git"
    cprint(f"Deleting the '.git'.")
    os.chdir(clone_to_path)
    shutil.rmtree('.git')
    cprint("-----------------------------------\n")


if __name__ == "__main__":

    main()