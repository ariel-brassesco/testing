import pytest
from git import Repo
import repo_copy as rc
import os, shutil    

def test_get_parse_args():
    # Input
    url = 'https://github.com/openworm/org.geppetto.git'
    data = rc.get_parse_args([url, '-o', '-t', '-d'])
    # Check default values
    assert data.target == None
    assert data.origin == None
    assert data.default == None
    assert data.url == url

    data = rc.get_parse_args([url, '-o', 'origin_branch',
                            '-t', 'target_branch', '-d', 'default_branch'])
    # Check default values
    assert data.target == 'target_branch'
    assert data.origin == 'origin_branch'
    assert data.default == 'default_branch'

def test_validate_args():
    # Input
    url = 'https://github.com/openworm/org.geppetto.git'
    # Set environ variables
    os.environ['TRAVIS_PULL_REQUEST'] = "false"
    os.environ['TRAVIS_BRANCH'] = "target_branch"
    os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = "origin_branch"
    data = rc.validate_args([url])
    # Check set env var
    assert data.test == 'PUSH'
    assert data.default == 'development'
    assert data.target == 'target_branch'
    assert data.origin == 'origin_branch'
    
    os.environ['TRAVIS_PULL_REQUEST'] = "1254asd63"
    data = rc.validate_args([url, '-d', 'default_branch',
                            '-t', 'target_branch', 
                            '-o', 'origin_branch'])
    # Check set from input
    assert data.test == 'PR'
    assert data.default == 'default_branch'
    assert data.target == 'target_branch'
    assert data.origin == 'origin_branch'

    # Reset env var
    os.environ['TRAVIS_PULL_REQUEST'] = ""
    os.environ['TRAVIS_BRANCH'] = ""
    os.environ['TRAVIS_PULL_REQUEST_BRANCH'] = ""

def test_get_path():
    data = ['https://github.com/openworm/org.geppetto.git',
        'https://github.com/openworm/org.geppetto.model.git',
        'https://github.com/openworm/org.geppetto.core.git',
        'https://github.com/openworm/org.geppetto.model.neuroml.git',
        'https://github.com/openworm/org.geppetto.simulation.git',
        'https://github.com/openworm/org.geppetto.frontend.git',
        'https://github.com/openworm/geppetto-application.git']

    result = ['org.geppetto', 'org.geppetto.model', 'org.geppetto.core',
        'org.geppetto.model.neuroml', 'org.geppetto.simulation',
        'org.geppetto.frontend', 'geppetto-application']
    
    res = [rc.get_path(url) for url in data]
    
    assert (res == result)

def test_clone_repo():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    url_wrong = 'github.com/openworm/org.geppetto.git'
    path_wrong = rc.get_path(url_wrong) 

    # Check raise exception if could not clone the repository
    with pytest.raises(Exception) as e:
        rc.clone_repo(url_wrong, path_wrong)
    
    # Clone existing repository
    repo = rc.clone_repo(url, path)
    # Check the repo is an instance of Repo class 
    assert isinstance(repo, Repo)

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_checkout():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)

    branch_exist = 'feature_623'
    branch_not_exist = 'feature/33'
    default = 'development'

    # Check the checkout function return True
    assert rc.checkout(repo, default)
    # Check the active brach of repo is default
    assert str(repo.active_branch) == default
    # Check the checkout function return False
    assert not rc.checkout(repo, branch_not_exist)
    # Check the active brach of repo is still default
    assert str(repo.active_branch) == default
    # Check the checkout function return True
    assert rc.checkout(repo, branch_exist)
    # Check the active brach of repo is branch_exist
    assert str(repo.active_branch) == branch_exist

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_merge():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)
    
    target_exist = 'feature_623'
    target_no_exist = 'feature_72'
    origin_exist = 'feature/621'
    origin_merge_conflict = 'feature/35'
    origin_no_exist = 'feature/33'
    default = 'development'

    # Check merge() return False if target and origin not exist
    # and checkout to 'development' as default
    assert not rc.merge(repo, target_no_exist, origin_no_exist)
    assert str(repo.active_branch) == 'development'
    # Check merge() return True if target and origin exist
    # and active branch is target
    assert rc.merge(repo, target_exist, origin_exist)
    assert str(repo.active_branch) == target_exist
    # Check merge() return False if target exists but not origin
    # and checkout to target
    assert not rc.merge(repo, target_exist, origin_no_exist)
    assert str(repo.active_branch) == target_exist
    # Check merge() return True if target not exists but origin exist
    # and active branch is default
    assert rc.merge(repo, target_no_exist, origin_exist, default)
    assert str(repo.active_branch) == default
    # Check merge() raise Exception when MERGE CONFLICT OCCUR
    # and active branch is target
    with pytest.raises(rc.MergeError) as e:
        rc.merge(repo, target_exist, origin_merge_conflict)
        assert str(repo.active_branch) == target_exist

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_no_default_branch():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)
    default_branch = None
    origin_branch = None
    target_branch = None
    
    with pytest.raises(rc.DefaultBranchNotProvided) as e:
        rc.pr(repo, target_branch, origin_branch, default_branch)
    
    with pytest.raises(rc.DefaultBranchNotProvided) as e:
        rc.push(repo, target_branch, default_branch)

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_no_exist_default_branch():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)
    default_branch = 'feature/33'
    origin_branch = None
    target_branch = None
    
    with pytest.raises(rc.DefaultBranchNotFound) as e:
        rc.pr(repo, target_branch, origin_branch, default_branch)
    
    with pytest.raises(rc.DefaultBranchNotFound) as e:
        rc.push(repo, target_branch, default_branch)

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_push():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)
    default_branch = 'development'
    target_exist = 'feature/72'
    target_not_exist = 'feature_72'

    # Check the push return True
    assert rc.push(repo, target_exist, default_branch)
    # Check the active_branch is target
    assert str(repo.active_branch) == target_exist
    
    # Check the push return True
    assert rc.push(repo, target_not_exist, default_branch)
    # Check the active_branch is target
    assert str(repo.active_branch) == default_branch
    
    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)

def test_pr():
    # Input data
    url = 'https://github.com/openworm/org.geppetto.git'
    path = rc.get_path(url)
    repo = rc.clone_repo(url, path)
    default_branch = 'development'
    target_exist = 'feature/72'
    target_no_exist = 'feature_72'
    origin_exist = 'feature/621'
    origin_no_exist = 'feature/33'

    # Check the pr return False
    assert not rc.pr(repo, None, None, default_branch)
    # Check the active_branch is default_target
    assert str(repo.active_branch) == default_branch

    # Check the pr return False
    assert not rc.pr(repo, target_no_exist, origin_no_exist, default_branch)
    # Check the active_branch is default_target
    assert str(repo.active_branch) == default_branch

    # Check the pr return True
    assert rc.pr(repo, target_exist, origin_exist, default_branch)
    # Check the active_branch is target_exist
    assert str(repo.active_branch) == target_exist

    # Check the pr return False
    assert not rc.pr(repo, target_exist, origin_no_exist, default_branch)
    # Check the active_branch is target_exist
    assert str(repo.active_branch) == target_exist

    # Check the pr return True
    assert rc.pr(repo, target_no_exist, origin_exist, default_branch)
    # Check the active_branch is target_exist
    assert str(repo.active_branch) == default_branch

    # Delete the repo
    repo.close()
    del repo
    if os.path.exists(path):
        shutil.rmtree(path)
