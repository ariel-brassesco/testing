import pytest
from git import Repo
from copy_ import *
import os, shutil
import random

URL_GEPPETTO = 'https://github.com/openworm/org.geppetto.git'
URL_LIST = ['https://github.com/openworm/org.geppetto.git',
            'https://github.com/openworm/org.geppetto.model.git',
            'https://github.com/openworm/org.geppetto.core.git',
            'https://github.com/openworm/org.geppetto.model.neuroml.git',
            'https://github.com/openworm/org.geppetto.simulation.git',
            'https://github.com/openworm/org.geppetto.frontend.git',
            'https://github.com/openworm/geppetto-application.git']


def gen_random_branch(branch):

    lst = list(branch)
    random.shuffle(lst)

    return ''.join(lst)

#7 Test
class TestFunctions():

    def test_get_env_var(self):
        os.environ['TRAVIS'] = 'TRAVIS'

        assert get_env_var('TRAVIS') == 'TRAVIS'
        assert get_env_var('TRAVIS1', default='BRANCH') == 'BRANCH'

        del os.environ['TRAVIS']

    def test_get_parse_args_defaultvalues(self):
        # Input
        data = get_parse_args([URL_GEPPETTO, '-o', '-t', '-d'])
        # Check default values
        assert data.target == None
        assert data.origin == None
        assert data.default == None
        assert data.url == URL_GEPPETTO
        assert data.pr == False
        assert data.push == False

    def test_get_parse_args_branchvalues(self):
        data = get_parse_args([URL_GEPPETTO, '-o', 'origin_branch',
                                '-t', 'target_branch', '-d', 'default_branch'])
        # Check default values
        assert data.target == 'target_branch'
        assert data.origin == 'origin_branch'
        assert data.default == 'default_branch'

    def test_get_parse_args_actionvalues(self):
        data = get_parse_args([URL_GEPPETTO, '--pr'])
        assert data.pr == True
        
        # Check mutually exclusive between '-pr' and '-push'
        with pytest.raises(SystemExit) as e:
            data = get_parse_args([URL_GEPPETTO, '--pr', '--push'])

    def test_validate_args_defaultvalues(self):
        # Set environ variables
        os.environ['TRAVIS_PULL_REQUEST'] = "false"
        os.environ['TRAVIS_BRANCH'] = "target_branch"
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = "origin_branch"
        
        data = validate_args([URL_GEPPETTO])
        # Check set env var
        assert data.travis_action_type == 'push'
        assert data.default == 'master'
        assert data.target == 'target_branch'
        assert data.origin == 'origin_branch'

        # Reset env var
        os.environ['TRAVIS_PULL_REQUEST'] = ""
        os.environ['TRAVIS_BRANCH'] = ""
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = ""
    
    def test_validate_args_pr(self):
        os.environ['TRAVIS_PULL_REQUEST'] = "1254asd63"
        os.environ['TRAVIS_BRANCH'] = "target_branch"
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = "origin_branch"
        os.environ['TRAVIS_DEFAULT_BRANCH'] = "default_branch"
        
        data = validate_args([URL_GEPPETTO, '-d', 'default',
                                '-t', 'target', 
                                '-o', 'origin'])
        # Check set from input
        assert data.travis_action_type == 'pr'
        assert data.default == 'default'
        assert data.target == 'target'
        assert data.origin == 'origin'

        # Reset env var
        os.environ['TRAVIS_PULL_REQUEST'] = ""
        os.environ['TRAVIS_BRANCH'] = ""
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = ""

    def test_validate_args_push(self):
        os.environ['TRAVIS_PULL_REQUEST'] = "1254asd63"
        os.environ['TRAVIS_BRANCH'] = "target_branch"
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = "origin_branch"
        os.environ['TRAVIS_DEFAULT_BRANCH'] = "default_branch"
        
        data = validate_args([URL_GEPPETTO, '-d', 'default',
                                '-t', 'target', 
                                '-o', 'origin', '--push'])
        # Check set from input
        assert data.travis_action_type == 'push'
        assert data.default == 'default'
        assert data.target == 'target'
        assert data.origin == 'origin'

        # Reset env var
        os.environ['TRAVIS_PULL_REQUEST'] = ""
        os.environ['TRAVIS_BRANCH'] = ""
        os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = ""

#6 Test
class TestTravisRepoAction():

    REPO_LIST = [TravisRepoAction(url, clone_repo=False) for url in URL_LIST]

    def test_clone_repository(self):
        true_repo = []
        for r in TestTravisRepoAction.REPO_LIST:
            r.clone_repository()
            true_repo.append(isinstance(r.repo, Repo))

        assert all(true_repo)

        # Delete the repos
        for r in TestTravisRepoAction.REPO_LIST:
            shutil.rmtree(r.path)

    def test_wrong_url_to_clone(self):
        url_wrong = 'github.com/openworm/org.geppetto.git'

        with pytest.raises(Exception) as e:
            TravisRepoAction(url_wrong, clone_repo=True)

    def test_generate_path(self):
        
        result = ['org.geppetto', 'org.geppetto.model', 'org.geppetto.core',
            'org.geppetto.model.neuroml', 'org.geppetto.simulation',
            'org.geppetto.frontend', 'geppetto-application']

        res = [r.path for r in TestTravisRepoAction.REPO_LIST]
        
        assert res == result

    def test_no_target_nor_origin_branch(self):

        travis_repo = TravisRepoAction(URL_GEPPETTO, clone_repo=False)
        with pytest.raises(NotTargetNorOrigin) as e:
            travis_repo.run()

    def test_default_branch_no_exist(self):
        
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=False,
                                        target_branch='target_branch',
                                        default_branch='NoExistBranch')
        with pytest.raises(DefaultBranchNotExists) as e:
            
            travis_repo.run()

    def test_wrong_action_type(self):
        
        with pytest.raises(ActionTypeError) as e:
            travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=False,
                                        target_branch='target_branch',
                                        action_type='action_type')
        
        with pytest.raises(ActionTypeError) as e:
            travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=False,
                                        target_branch='target_branch')
            travis_repo.action_type = 'PUSH'
            travis_repo.run()

#2 Test
class TestTravisRepoActionPush():

    def test_push_action_with_target_exist(self):
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='push')
        
        branches = travis_repo.get_repo_available_branches()
        branches.remove('HEAD')
        random.shuffle(branches)
        #pick_1 = random.randint(0,len(self.branches))
        default_branch = 'development'
        target_exist = branches.pop()#self.branches[pick_1]

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_exist
        
        # Check the push return True
        assert travis_repo.push()
        # Check the active_branch is target
        assert str(travis_repo.repo.active_branch) == target_exist

        del travis_repo

    def test_push_action_with_target_not_exist(self):
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='push')
        
        branches = travis_repo.get_repo_available_branches()
        branches.remove('HEAD')
        random.shuffle(branches)

        default_branch = 'development'
        target_not_exist = gen_random_branch(branches.pop())

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_not_exist

        # Check the push return True
        assert travis_repo.push()#pick_1 = random.randint(0,len(self.branches))#pick_1 = random.randint(0,len(self.branches))
        # Check the active_branch is default
        assert str(travis_repo.repo.active_branch) == default_branch

        del_path = travis_repo.path
        del travis_repo
        shutil.rmtree(del_path)

#4 Test
class TestTravisRepoActionPr():

    def test_pr_action_target_origin_exist(self):
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='pr')

        default_branch = 'development'
        target_exist = 'feature_623'
        origin_exist = 'feature/621'

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_exist
        travis_repo.origin_branch = origin_exist

        # Check the pr return True
        assert travis_repo.pr()
        # Check the active_branch is target_exist
        assert str(travis_repo.repo.active_branch) == target_exist

        del travis_repo

    def test_pr_action_no_origin_exist(self):
        
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='pr')
        
        branches = travis_repo.get_repo_available_branches()
        branches.remove('HEAD')
        random.shuffle(branches)
        
        default_branch = 'development'
        target_exist = 'feature_623'
        origin_no_exist = gen_random_branch(branches.pop())

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_exist
        travis_repo.origin_branch = origin_no_exist

        # Check the pr return False
        assert not travis_repo.pr()
        # Check the active_branch is target_exist
        assert str(travis_repo.repo.active_branch) == target_exist

        del travis_repo

    def test_pr_action_no_target_exist(self):
        
        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='pr')
        
        branches = travis_repo.get_repo_available_branches()
        branches.remove('HEAD')
        random.shuffle(branches)

        default_branch = 'development'
        target_no_exist = gen_random_branch(branches.pop())
        origin_exist = 'feature/621'

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_no_exist
        travis_repo.origin_branch = origin_exist

        # Check the pr return True
        assert travis_repo.pr()
        # Check the active_branch is default_branch
        assert str(travis_repo.repo.active_branch) == default_branch

        del travis_repo

    def test_pr_action_no_target_no_origin_exist(self):

        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='pr')
        
        branches = travis_repo.get_repo_available_branches()
        branches.remove('HEAD')
        random.shuffle(branches)

        default_branch = 'development'
        target_no_exist = gen_random_branch(branches.pop())
        origin_no_exist = gen_random_branch(branches.pop())

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_no_exist
        travis_repo.origin_branch = origin_no_exist

        # Check the pr return False
        assert not travis_repo.pr()
        # Check the active_branch is default_target
        assert str(travis_repo.repo.active_branch) == default_branch

        del_path = travis_repo.path
        del travis_repo
        shutil.rmtree(del_path)

    def test_pr_merge_conflict(self):

        travis_repo = TravisRepoAction(URL_GEPPETTO,
                                        clone_repo=True,
                                        action_type='pr')

        default_branch = 'development'
        target_branch_conflict = 'debugging_dockers_branch'
        origin_branch_conflict = 'feature/35'

        travis_repo.default_branch = default_branch
        travis_repo.target_branch = target_branch_conflict
        travis_repo.origin_branch = origin_branch_conflict

        # Check raise MergeError
        with pytest.raises(MergeError):
            travis_repo.pr()
        
        del_path = travis_repo.path
        del travis_repo
        shutil.rmtree(del_path)
