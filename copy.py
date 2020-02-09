from git import Repo
from git.exc import GitCommandError, NoSuchPathError
import os, sys, shutil
from colorama import Fore


'''
$TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                * For builds triggered by a PR this is the name of the branch targered by the PR.
$TRAVIS_PULL_REQUEST_BRANCH: * For builds triggered by a PR this is the name of the branch origineted.
                             * For others, this is "" (empty string).

So, if the build is triggered by a PR the sys.argv will have 5 arguments and
if the build is triggered by a push the sys.argv will have 4 arguents.
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

def define_test(repo_info):
    '''
        This function check the arguments and define if the test is a push or PR.
        Raise and exception if the len of arguments are incorrect.
        Return a tuple with repo_url, target_branch, origin_branch, 
        default_branch and test type.
    '''
    # Check the arguments are correct
    if (len(repo_info) < 4):
        # The size of repo_info is incorrect
        raise Exception("Not enough arguments")

    elif len(repo_info) == 4:
        # If it's a push TRAVIS_PULL_REQUEST_BRANCH = '' (empty string)
        # and will be 4 arguments
        test = 'PUSH'
        repo_url = repo_info[1]
        target_branch = repo_info[2]
        origin_branch = ''
        default_branch = repo_info[3]

    elif len(repo_info) == 5:
        # If it's a Pull Request will be 5 arguments
        test = 'PR'
        repo_url = repo_info[1]
        target_branch = repo_info[2]
        origin_branch = repo_info[3]
        default_branch = repo_info[4]

    else:
        # The size of repo_info is incorrect
        raise Exception("Too many arguments")
    
    return (repo_url, target_branch, origin_branch, default_branch, test)

if __name__ == "__main__":  

    # Take the arguments and pass to function define_test.
    data = sys.argv
    clone_url, target_branch, origin_branch, default_branch, tesp_type = define_test(data)

    # Print some information
    print(f"The repository is:     {clone_url}.")
    print(f"The test to run is:    {test_type}.")
    
    if test_type == 'PR':
        print(f"The origin_branch is:  {origin_branch}.")

    print(f"The target_branch is:  {target_branch}.")
    print(f"The default_branch is: {default_branch}.")

    # Define the directory name for the repository cloned
    clone_to_path = clone_url.split('/')[-1]
    clone_to_path = clone_to_path.replace(".git", "")

    # Delete the repository, just to clone_from url and not get an error
    if os.path.exists(clone_to_path):
        print(f"\nThe directory {clone_to_path} already exist. Will be delete.\n")
        shutil.rmtree(clone_to_path)

    # Clone the repo
    try:
        print(Fore.YELLOW + f"Start cloning {clone_url}." + Fore.RESET)
        repo = Repo.clone_from(url=clone_url, to_path=clone_to_path, branch = default_branch)
        print(Fore.GREEN + "The repository was cloned successfully." + Fore.RESET)
        print(Fore.YELLOW + "The current branch is " + str(repo.active_branch) + Fore.RESET)
        print(f"The directory {clone_to_path} was created.\n")

    except Exception as error:
        # If there is an error during the cloning raise an exception
        print(Fore.RED + str(error) + Fore.RESET)
        raise Exception(Fore.RED + 
                        f"The repository could not be clone from the {clone_url} to {clone_to_path}." + 
                        Fore.RESET)

    if test_type == 'PR':
        # Try checkout to origin_branch like 'git checkout origin_branch'
        origin_check = checkout(repo, origin_branch)

        # Try checkout to target_branch like 'git checkout target_branch'
        target_check = checkout(repo, target_branch)

        # Merge origin_branch into target_branch
        #merge(repo, origin_branch)

        if not target_check: # If target_branch does not exists

            # Checkout to default_branch
            checkout(repo, default_branch)

            if origin_check: # If origin_branch exists, merge into default_branch
                merge(repo, origin_branch)
        
        else: # If target_branch exists

            if origin_check: # If origin_branch exists, merge into target_branch
                merge(repo, origin_branch)
            
    else: # This is test=='PUSH'
        
        # Try checkout to target_branch like 'git checkout target_branch'
        target_check = checkout(repo, target_branch)

        if not target_check: # If target_branch does not exists
            checkout(repo, default_branch)
    
    repo.close()
    del repo
