from git import Repo
import os, shutil, argparse
from colorama import Fore

'''
$TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                * For builds triggered by a PR this is the name of the branch targered by the PR.
$TRAVIS_PULL_REQUEST_BRANCH: * For builds triggered by a PR this is the name of the branch origineted.
                             * For others, this is "" (empty string).

So, if the build is triggered by a PR the TRAVIS_PULL_REQUEST_BRANCH will be the name 
of origin branch and if the build is triggered by a PUSH TRAVIS_PULL_REQUEST_BRANCH 
will be an empty string.
'''

def checkout(repo, branch):
    '''
        This function checkout to branch.
        Return True if the checkout is successful and False if raise some error.
    '''
    try:
        response = repo.git.checkout(branch)
        print(Fore.GREEN + response + Fore.RESET)
        print(Fore.YELLOW + "The current branch is " + str(repo.active_branch) + Fore.RESET)

    except Exception as error:
        print(Fore.RED+str(error)+Fore.RESET)
        print(Fore.YELLOW + "The current branch is " + str(repo.active_branch) + Fore.RESET)
        return False
    return True


def merge(repo, from_branch):
    '''
        This function merge the from_branch into the cuurrent brach in the repo.
        The current branch is repo.active_branch.
        Return True if the merge is successful and False if raise some error.
    '''
    try:
        print("\n", Fore.YELLOW + f"Start merging {from_branch} into {repo.active_branch}." 
                + Fore.RESET)
        response = repo.git.merge(from_branch)
        # This print out all the message abour the merge.
        print("\n",response,"\n")
        print(Fore.GREEN + "Finish the merge.\n" + Fore.RESET)
    except Exception as error:
        print("\n", Fore.RED + str(error) + Fore.RESET,"\n")
        return False
    return True


def clone_repo(url, path):
    '''
    This function clone a repository form the url to the path.
    Return a Repo object. Raise and Exception if the repository could not be cloned.
    '''
    
    # Delete the repository, just to clone_from url and not get an error
    if os.path.exists(path):
        cprint(f"\nThe directory {path} already exist. Will be delete.\n")
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
        define if the test is a PUSH or PR.
        The url of repository is a positional argument. The name of branches are optional
        arguments.
        Raise and exception if the arguments are incorrect.
        Return a Namespace with repository url, target branch, origin branch, 
        default branch and test type.
    '''

    parse = argparse.ArgumentParser(description='This script takes as inputs the URL repository, '
                                    'and the branches TARGET, ORIGIN and DEFAULT, and determine if the test'
                                    ' correspond a PR or a PUSH.\n'
                                    'The default values are taking from environment variables TRAVIS_BRANCH'
                                    ' and TRAVIS_PULL_REQUEST_BRANCH for TARGET and ORIGIN branches, respectively.'
                                    ' DEFAULT branch will be "development" or "master" if no value is passed. '
                                    'For a PUSH the script makes a checkout to TARGET branch, if not possible '
                                    'makes a checkout to DEFAULT branch. '
                                    'For a PR the script makes a merge between TARGET and ORIGIN branch, if not '
                                    'possible try to merge DEFAULT and ORIGIN branch, and finally try to checkout to'
                                    ' TARGET or DEFAULT branch.')
    
    # Define the optional and positiional arguments
    parse.add_argument('url', help='This is the URL of the repository.')
    parse.add_argument('-t', '--target-branch', dest='target', help='This is the target branch '
                        'from PR or PUSH. The default value is the enviroment variable TRAVIS_BRANCH.')
    parse.add_argument('-d', '--default-branch', dest='default', help='This is the default branch if'
                        'the target branch does not exist or it isn\'t specified.'
                        ' The default value is development or master.')
    parse.add_argument('-o', '--origin-branch', dest='origin', nargs='?', const=None, help='This is the origin branch from PR or PUSH.'
                        ' The default value is the enviroment variable TRAVIS_PULL_REQUEST_BRANCH.')

    # Get the variables
    args = parse.parse_args()
    
    # Set test='PR' and later check if it's a PUSH
    args.test = 'PR'

    # If default branch not passed set as "development"
    if args.default == None:
        args.default = 'development'

    # If target branch not passed set as TRAVIS_BRANCH enviroment variable
    if args.target == None:
        cprint("No target_branch provides.")
        if os.environ.get('TRAVIS_BRANCH'):
            args.target = os.environ.get('TRAVIS_BRANCH')
            cprint(f"Found env variable TRAVIS_BRANCH with value '{args.target}'.")

    # If origin branch not passed set as TRAVIS_PULL_REQUEST_BRANCH enviroment variable
    if args.origin == None:
        # If TRAVIS_PULL_REQUEST_BRANCH is set, so it's a PR
        cprint("No origin_branch provides.")
        if os.environ.get('TRAVIS_PULL_REQUEST_BRANCH'):
            args.origin = os.environ.get('TRAVIS_PULL_REQUEST_BRANCH')
            args.test = 'PR'
            cprint(f"Found env variable TRAVIS_PULL_REQUEST_BRANCH with value '{args.origin}'.")
        else: # If TRAVIS_PULL_REQUEST_BRANCH isn't set, so it's a PUSH
            args.test = 'PUSH'
            cprint(f"Not found env variable TRAVIS_PULL_REQUEST_BRANCH.")

    return args


def cprint(string, color = 'WHITE'):
    '''
    This function print the string with color.
    '''
    color = eval('Fore.' + color)
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
    cprint(f"The repository is:     {clone_url}.")
    cprint(f"The test to run is:    {test_type}.")
    
    if test_type == 'PR':
        cprint(f"The origin_branch is:  {origin_branch}.")

    cprint(f"The target_branch is:  {target_branch}.")
    cprint(f"The default_branch is: {default_branch}.")

    # Define the directory name for the repository cloned
    clone_to_path = clone_url.split('/')[-1]
    clone_to_path = clone_to_path.replace(".git", "")

    # Clone the repository
    repo = clone_repo(clone_url, clone_to_path)

    if test_type == 'PR':
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
        target_check = checkout(repo, target_branch)

        if not target_check: # If target_branch does not exists
            checkout(repo, default_branch)
    
    repo.close()
    del repo


if __name__ == "__main__":

    main()