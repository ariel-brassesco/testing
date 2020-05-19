from git import Repo
import os, shutil, argparse, sys
#from colorama import Fore

'''
NAME
    copy_

DESCRIPTION
    This module aims to execute git commands to clone a repository, checkout and merge 
    branches, taking into account if the request is a PUSH or PULL REQUEST. 

    It can works with travis env variables, and if the action type (PUSH or PULL REQUEST) 
    is not passed it will be determine based on DEFAULT TRAVIS ENVIRONMENT VARIABLES:

    TRAVIS_BRANCH: * For push or builds not triggered by a PR this is the name of the branch.
                   * For builds triggered by a PR this is the name of the branch targered by the PR.
                   * For builds triggered by a TAG, this is the same as the name of the TAG (TRAVIS_TAG).
    TRAVIS_PULL_REQUEST_BRANCH: * For builds triggered by a PR this is the name of the branch origineted.
                                * For others, this is "" (empty string).
    TRAVIS_PULL_REQUEST:   * It is the number of PR.
                           * For PUSH is set to "false".
    (See https://docs.travis-ci.com/user/environment-variables/#default-environment-variables)
    
    The module use argparse to allow command-line arguments. Run 'python copy_.py --help'
    for more information.

    Use GitPython module to execute the git commands and handle the repository. 
    See https://gitpython.readthedocs.io/en/stable/ for more information about that module.

    See https://github.com/ariel-brassesco/testing/blob/master/README.md for more 
    information.

FUNCTIONS:
    get_env_var
    get_parse_args
    main
    print_colored
    validate_args
        
CLASSES:
    TravisRepoAction

GLOBAL VARIABLES:
    DEFAULT_BRANCH
    TRAVIS_ORIGIN_ENV_NAME
    TRAVIS_PULL_REQUEST
    TRAVIS_TARGET_ENV_NAME
    TRAVIS_TYPE_PR
    TRAVIS_TYPE_PUSH

EXCEPTIONS:
    ActionTypeError(Exception)
    DefaultBranchNotExists(Exception)
    DefaultBranchNotFound(Exception)
    MergeError(Exception)
    NotTargetNorOrigin(Exception)
'''

# Define some constants
TRAVIS_PULL_REQUEST = 'TRAVIS_PULL_REQUEST'
TRAVIS_ORIGIN_ENV_NAME = 'TRAVIS_PULL_REQUEST_BRANCH'
TRAVIS_TARGET_ENV_NAME = 'TRAVIS_BRANCH'
TRAVIS_TYPE_PR = 'pr'
TRAVIS_TYPE_PUSH = 'push'
DEFAULT_BRANCH = os.getenv('DEFAULT_BRANCH')

if not DEFAULT_BRANCH:
    DEFAULT_BRANCH = 'master'

# Define Exceptions
class DefaultBranchNotFound(Exception):
    pass

class DefaultBranchNotExists(Exception):
    pass

class ActionTypeError(Exception):
    pass

class NotTargetNorOrigin(Exception):
    pass

class MergeError(Exception):
    pass

# Define Classes
class TravisRepoAction():
    '''
    Parameters:
        url: str.
            The url repository.
        path: str, default None.
            The directory where clone the repository. If None, generate the path from url 
            see the method 'generate_path'.
        clone_repo: bool, default False.
            If is True clone the repository from url to path when instance the object.
        target_branch: str, default None.
            The target branch name.
        origin_branch: str, default None.
            The origin branch name.
        default_branch: str, default 'master'.
            The default branch name.
        action_type: str, default 'push'.
            The travis action type. Only accept 'push' and 'pr' values, otherwise
            raise ActionTypeError.
    
    Attributes:
        url: str.
            Store the url of repository.
        path: str.
            Store the path where the repository will be cloned.
        target_branch: str, None.
            Store the target branch name.
        origin_branch: str, None.
            Store the origin branch name.
        default_branch: str.
            Store the default branch name.
        action_type: str.
            Store the travis action type.
        repo: class Repo, None.
            Store the class git.Repo of the repository cloned from url.
        ACTION_TYPES: list(str).
            Class attribute. Store the travis action types allowed.
        
    Raises:
        ActionTypeError:
            The action_type is not 'push' nor 'pr'.
    '''
    ACTION_TYPES = ['push', 'pr']

    def __init__(self,
                url,
                path=None,
                clone_repo=False,
                target_branch=None,
                origin_branch=None,
                default_branch='master',
                action_type='push'):
        
        self.url = url
        
        if path:
            self.path = path
        else:
            self.path = self.generate_path()
        
        if clone_repo:
            self.clone_repository()
        else:
            self.repo = None

        self.target_branch = target_branch
        self.origin_branch = origin_branch
        self.default_branch = default_branch
        self.action_type = self.check_action_type(action_type)

    def clone_repository(self):
        '''
        Clone a repository from the url attribute to the path attribute with the method 
        'git.Repo.clone_from' and store the class git.Repo returned in attribute repo.
            
        Parameters:
            None.
            
        Raises:
            Exception:
                The repository could not be cloned.
            
        Returns:
            None.
        '''

        # Delete the repository, just to clone_from url and not get an error
        if os.path.exists(self.path):
            print_colored("The directory {} already exist. Will be delete.".format(self.path))
            shutil.rmtree('/'.join([os.getcwd(), self.path]))

        # Clone the repo
        try:
            print_colored("Cloning {}.".format(self.url))
            
            # Clone the master branch
            self.repo = Repo.clone_from(url=self.url, to_path=self.path)
            
            print_colored("The repository was cloned successfully.", color='GREEN')

        except Exception as error:
            print_colored("The repository could not be clone from the {0} to {1}.".format(self.url, self.path),
                        color='RED')
            print_colored(str(error), color='RED')
            raise Exception()

    def del_git_file(self):
        '''
        Delete the '.git' in the path.
        '''
        print_colored("Deleting the '.git'.")
        shutil.rmtree('/'.join([os.getcwd(), self.path, '.git']))
        print_colored("-----------------------------------\n")

    def generate_path(self):
        '''
        Take the url attribute and return the last name without '.git'. 

        Parameters:
            None.
        
        Return: 
            path: str.
                The name of directory.
            
        Example:
            self.url = https://github.com/openworm/org.geppetto.git
            return =>  org.geppetto
        '''
        
        path = self.url.split('/')[-1]
        return path.replace(".git", "")

    def get_repo_available_branches(self):
        '''
        Return a list with the names of remotes branches in repo attribute.
        '''
        branches = []
        
        for branch in self.repo.remotes.origin.refs:
            branches.append(branch.name.replace('origin/', ''))
        
        return branches

    def get_repo_available_tags(self):
        '''
        Return a list with the names of tags in repo attribute.
        '''
        return [tag.name for tag in self.repo.tags]

    def is_repo_branch(self, branch):
        '''
        Return True if branch argument is a branch of repo attribute, else False.

        Parameters:
            branch: str.
                The branch name to check it's in repo attribute.
        
        Return:
            bool.
        '''
        
        branches = self.get_repo_available_branches()
        return branch in branches

    def is_repo_tag(self, tag):
        '''
        Return True if tag argument is a tag of repo attribute, else False.

        Parameters:
            tag: str.
                The tag name to check it's in repo attribute.
        
        Return:
            bool.
        '''
        
        tags = self.get_repo_available_tags()
        return tag in tags

    def is_not_target_nor_origin(self):
        '''
        Return True if target_branch and origin_branch attributes are None, else False.
        '''
        
        return not self.target_branch and not self.origin_branch

    def check_default_branch(self, default_branch):
        '''
        Check if default_branch if a branch of repo attirbute.
        Return the default_branch argument if it's a branch, else raise an exception.

        Parameters:
            default_branch: str.
                The default branch name to check.

        Raises:
            DefaultBranchNotExists:
                If default_branch argument is not a branch of repo attribute.
            DefaultBranchNotFound:
                If default_branch argument is 'master' and is not a branch of 
                repo attribute.

        Return:
            default_branch: str.
                The default_branch argument.
        '''
        if not self.is_repo_branch(default_branch):

            if default_branch == 'master':
                raise DefaultBranchNotFound('default_branch={} does not exist. '
                                        'Set a valid default_branch.'.format(default_branch))
        
            raise DefaultBranchNotExists('default_branch provided does not exist.')
        
        return default_branch

    def check_action_type(self, action_type):
        '''
        Check if action_type is in class attribute ACTION_TYPES list.
        Return the action_type argument if it's, else raise an exception.

        Parameters:
            action_type: str.
                The travis action type to check.

        Raises:
            ActionTypeError:
                If action_type argument is not in class attribute ACTION_TYPES list.

        Return:
            action_type: str.
                The travis action type.
        '''
        if action_type not in TravisRepoAction.ACTION_TYPES:
            raise ActionTypeError("The 'action_type' must be {}.".format(' or '.join(TravisRepoAction.ACTION_TYPES)))
        return action_type

    def print_input_data(self):
        '''
        Print into stdout the attribute data of the instance.
        '''
        if not self.target_branch:
            print_colored("Not TARGET BRANCH was provided.")
        
        if not self.origin_branch:
            print_colored("Not ORIGIN BRANCH was provided.")

        print_colored("\nDATA INPUT")
        print_colored("###################################")
        print_colored("Repository url:         {}".format(self.url))
        print_colored("Travis action type:     {}".format(self.action_type))
        print_colored("-----------------------------------")
        print_colored("Origin branch:          {}".format(self.origin_branch))
        print_colored("Target branch:          {}".format(self.target_branch))
        print_colored("Default branch:         {}".format(self.default_branch))
        print_colored("-----------------------------------\n")

    def set_credentials(self, name='Your Name', email='you@example.com'):
        '''
        Set your name and email credentials for git repository.
        '''
        self.repo.config_writer().set_value("user", "name", name).release()
        self.repo.config_writer().set_value("user", "email", email).release()

    def checkout(self, branch):
        '''
        Check if branch argument is in repo attribute, and then checkout. 
        The argument branch could be a tag.
        Return True if the checkout is successful and False if the branch or tag 
        does not exist in repo attribute.
        
        Parameters:
            branch: str.
                The branch name to checkout.

        Return:
            bool.
        '''
        if self.is_repo_branch(branch):
            self.repo.git.checkout(branch)
            print_colored("Checkout " + str(self.repo.active_branch), color='GREEN')
            return True
        elif self.is_repo_tag(branch):
            self.repo.git.checkout('tags/' + branch)
            print_colored("Checkout tags/{}".format(branch), color='GREEN')
            return True
        
        return False

    def merge(self):
        '''
        Merge the origin_branch attribute into the target_branch attribute and return True.
        If the target_branch attribute is not in the repo attribute, merge into the 
        default_branch attribute and return True.
        If the origin_branch attribute is not in the repo attribute, checkout to target_branch 
        attribute or default_branch and return False.
        If there is any error with 'git.merge', for example merge conflics, raise MergeError.

        Parameters:
            None.

        Raises:
            MergeError:
                If there is an error during the merge, like Merge Conflicts.

        Return:
            bool.
        '''
        # Try checkout to origin like 'git checkout origin'
        o_check = self.checkout(self.origin_branch)
        # Try checkout to target like 'git checkout target'    
        t_check = self.checkout(self.target_branch)

        if not t_check:
            self.checkout(self.default_branch)

        if o_check:
            try:
                print_colored("Merge {0} into {1}.".format(self.origin_branch, self.repo.active_branch))
                response = self.repo.git.merge(self.origin_branch)
                # This print out all the message about the merge.
                print_colored(response)
                return True
            except Exception as error:
                raise MergeError(str(error))
                #print_colored(str(error), color='RED')
        else:
            print_colored("The origin branch: {} does not exist.".format(self.origin_branch))
            print_colored("Not need to merge.")
            pass

        return False

    def pr(self):
        '''
        Execute the PULL REQUEST actions. These are:
            -Clone the url repository if the repo attribute is None.
            -Check the default_branch attribute.
            -Print the input data.
            -Merge the origin_branch attirbute into the target_branch attribute.
        
        See merge method.

        Parameters:
            None

        Return:
            merge. See the merge method.
        '''
        if not isinstance(self.repo, Repo):
            self.clone_repository()
        
        self.check_default_branch(self.default_branch)
        self.print_input_data()

        return self.merge()

    def push(self):
        '''
        Execute the PUSH actions. These are:
            -Clone the url repository if the repo attribute is None.
            -Check the default_branch attribute.
            -Print the input data.
            -Checkout to target_branch attirbute if exists, else checkout to 
             default_branch attribute.

        Parameters:
            None

        Raises:
            See check_default_branch method.

        Return:
            True.
        '''
        if not isinstance(self.repo, Repo):
            self.clone_repository()
        
        self.check_default_branch(self.default_branch)
        self.print_input_data()

        if self.checkout(self.target_branch):
            return True
        
        return self.checkout(self.default_branch)      

    def run(self):
        '''
        Run the corresponding method for travis action type defined by action_type attribute.
        For PUSH, calls push method, and for PULL REQUEST calls pr method.
        If origin_branch attribute and target_branch attribute are None, raise an Exception.
            
        Parameters:
            None.
        
        Raises:
            ActionTypeError:
                If action_type attribute is not in class attribute ACTION_TYPES list.
            NotTargetNorOrigin:
                If target_branch attribute and origin_branch attribute are None.
        
        Return:
            None
        '''
        if self.is_not_target_nor_origin():
            raise NotTargetNorOrigin("target_branch and origin_branch were not provide.")

        if self.action_type == TravisRepoAction.ACTION_TYPES[0]:
            self.push()
        elif self.action_type == TravisRepoAction.ACTION_TYPES[1]:
            self.pr()
        else:
            raise ActionTypeError("The 'action_type' must be {}".format(' or '.join(TravisRepoAction.ACTION_TYPES)))

# Define Functions
def print_colored(string, color = 'WHITE'):
    '''
    Print in stdout the argument string colored by argument color.
    The default color is WHITE.
    '''
    COLORS = {
            'GREEN': "\033[1;32;40m",
            'RED': "\033[1;31;40m",
            'DEFAULT': "\033[0;37;40m"
    }
    
    if str(color).upper() in COLORS:
        print(COLORS.get(color) + str(string) + COLORS.get('DEFAULT'))
    else:
        print(COLORS.get('DEFAULT') + str(string) + COLORS.get('DEFAULT'))

def get_env_var(var_name, default = None):
    '''
    Return the environment variable of argument var_name if exists, 
    or argument default otherwise.
    '''
    if var_name in os.environ:
        env_var = os.getenv(var_name)
        print_colored("env var {0} found: '{1}'.".format(var_name, env_var))
    else:
        env_var = default
        print_colored("env var {0} not found. Set default value: {1}".format(var_name, default))
    return env_var

def get_parse_args(args=None):
    '''
    Implement the command-line arguments. The options are:
     url (postional): URL of repository.
     [-t, --target-branch] (optional): Target branch name.
     [-o, --origin-branch] (optional): Origin branch name.
     [-d, --default-branch] (optional): Default branch name.
     [--pr, --push] (optional, mutually_exclusive_group): A bool value.
        
    Run 'python copy_.py --help' for more information.

    Parameters:
        args : list, default None
            The arguments parse in command-line, or passed as list.
        
    Return:
        parse_args: namespace
            A namespaces with arguments parse.
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
    
    # Define the optional and positional arguments
    parse.add_argument('url', help='Repository URL.')
    parse.add_argument('-t', '--target-branch', dest='target', nargs='?', const=None, 
                        help='Target branch from PR or PUSH. Default value is the' 
                        ' enviroment variable TRAVIS_BRANCH.')
    parse.add_argument('-d', '--default-branch', dest='default', nargs='?', const=None, 
                        help='Default branch when target branch does not exist.'
                        ' Default value is the enviroment variable TRAVIS_DEFAULT_BRANCH or "master".')
    parse.add_argument('-o', '--origin-branch', dest='origin', nargs='?', const=None, 
                        help='Origin branch from PR. Default value is the enviroment variable'
                        ' TRAVIS_PULL_REQUEST_BRANCH.')
    group_travis_action_type = parse.add_mutually_exclusive_group()
    group_travis_action_type.add_argument('--pr', action='store_true', help='Set TRAVIS TEST as PULL REQUEST.')
    group_travis_action_type.add_argument('--push', action='store_true', help='Set TRAVIS TEST as PUSH.')

    # Return the variables
    return parse.parse_args(args)

def validate_args(args=None):
    '''
    Check the arguments args passed and determine the branches names and 
    travis action type. If some branch name or travis action type is 'None' take 
    the default value (for default_branch) or DEFAULT TRAVIS ENVIRONMENT VARIABLES.
        
    Take the arguments from 'get_parse_args' functions if 'args=None'.

    Return a Namespace with repository url, target branch, origin branch, 
    default branch and travis action type.

    Parameters:
        args: list, default None.
            See function 'get_parse_args' for args parse.
        
    Return:
        A namespace with the arguments parse.
    '''
    args = get_parse_args(args)
    
    if args.default == None:
        args.default = DEFAULT_BRANCH

    if args.target == None:
        args.target = get_env_var(TRAVIS_TARGET_ENV_NAME)
    
    if args.origin == None:
        args.origin = get_env_var(TRAVIS_ORIGIN_ENV_NAME)
    
    # Set the travis test type
    if args.pr:
        args.travis_action_type = TRAVIS_TYPE_PR
    elif args.push or (os.getenv('TRAVIS_PULL_REQUEST') == 'false'):
        args.travis_action_type = TRAVIS_TYPE_PUSH
    else: 
        args.travis_action_type = TRAVIS_TYPE_PR

    return args

def main():
    
    # Take the arguments from command-line and set the variables.
    data = validate_args(sys.argv[1:])
    travis_repo = TravisRepoAction(url=data.url,
                                path=None,
                                clone_repo=True,
                                target_branch=data.target,
                                origin_branch=data.origin,
                                default_branch=data.default,
                                action_type=data.travis_action_type)

    # Run the TravisCI test
    travis_repo.set_credentials()
    travis_repo.run()
    travis_repo.del_git_file()
    
    del travis_repo

if __name__ == "__main__":

    main()