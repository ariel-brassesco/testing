from git import Repo
import os, shutil, argparse
from colorama import Fore

'''
This script use argparse, run 'python copy.py --help' to have more information.

$TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                * For builds triggered by a PR this is the name of the branch targered by the PR.
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



def checkout(repo, branch):
    '''
        This function checkout to branch.
        Return True if the checkout is successful and False if raise some error.
    '''
    try:
        response = repo.git.checkout(branch)
        cprint(response, 'GREEN')
        cprint("The current branch is " + str(repo.active_branch), color='YELLOW')

    except Exception as error:
        cprint(str(error), 'RED')
        cprint("The current branch is " + str(repo.active_branch), color='YELLOW')
        return False
    return True


def merge(repo, from_branch):
    '''
        This function merge the from_branch into the cuurrent brach in the repo.
        The current branch is repo.active_branch.
        Return True if the merge is successful and False if raise some error.
    '''
    try:
        cprint(f"Start merging {from_branch} into {repo.active_branch}.", color='YELLOW')
        response = repo.git.merge(from_branch)
        # This print out all the message abour the merge.
        cprint(response)
        cprint("Finish the merge.", color='GREEN')
    except Exception as error:
        cprint(str(error), color='RED')
        return False
    return True


def clone_repo(url, path):
    '''
    This function clone a repository form the url to the path.
    Return a Repo object. Raise and Exception if the repository could not be cloned.
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
            cprint(f"Not found env variable TRAVIS_PULL_REQUEST_BRANCH.")

    return args


def cprint(string, color = None):
    '''
    This function print the string with color.
    The default value is WHITE, is the color argument is not
    an attribute of Fore, the default value is used.
    '''
    color = getattr(Fore, str(color), Fore.WHITE)
    print(color + string + Fore.RESET)

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
    clone_to_path = clone_url.split('/')[-1]
    clone_to_path = clone_to_path.replace(".git", "")

    # Clone the repository
    repo = clone_repo(clone_url, clone_to_path)
    cprint("-----------------------------------\n")

    if test_type == constants['pr']:
        # Try checkout to origin_branch like 'git checkout origin_branch'
        if origin_branch:
            origin_check = checkout(repo, origin_branch)
        else:
            origin_check = False
        
        
        # Try checkout to target_branch like 'git checkout target_branch'
        if target_branch:
            target_check = checkout(repo, target_branch)
        else:
            target_check = False
        

        if not target_check: # If target_branch does not exists

            # Checkout to default_branch
            checkout(repo, default_branch)
            

            if origin_check: # If origin_branch exists, merge into default_branch
                merge(repo, origin_branch)
        
        else: # If target_branch exists

            if origin_check: # If origin_branch exists, merge into target_branch
                merge(repo, origin_branch)
        

    else: # This is test_type=='PUSH'
        
        # Try checkout to target_branch like 'git checkout target_branch'
        if target_branch:
            target_check = checkout(repo, target_branch)
        else:
            target_check = False
        
        if not target_check: # If target_branch does not exists
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