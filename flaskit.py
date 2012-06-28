from flask import Flask, render_template, request
from flaskext import gravatar, markdown


import sys
import settings
import filters

import utils

from dulwich.repo import Repo
from dulwich.objects import Blob

app = Flask(__name__)

#Extensions
gravatar = gravatar.Gravatar(app,
                    size=50,
                    rating='g',
                    default='mm',
                    force_default=False,
                    force_lower=False)

markdown.Markdown(app)



#Configuration
LOCAL_BRANCH_PREFIX = "refs/heads/"
REMOTE_BRANCH_PREFIX = "refs/remotes/"

#View
@app.route('/')
def index():
    
    # Compound statements only available in 2.7 (http://docs.python.org/reference/compound_stmts.html)
    #repos = {key:pygit2.Repository(path) for key, path in settings.REPOS.iteritems()}
    
    repos = {}
    for key, path in settings.REPOS.iteritems():
        repos[key] = Repo(path)
    
    return render_template('index.html', repos=repos)

@app.route('/<repo_key>/tree/<branch>/')
@app.route('/<repo_key>/tree/<branch>/<path:tree_path>/')
def repo_dashboard(repo_key, branch, tree_path=''):
    
    #Get repo & branch
    repo = Repo(settings.REPOS[repo_key])
    try:
        branch_or_sha = repo.get_refs()[LOCAL_BRANCH_PREFIX+branch]
    except KeyError:
        #If there is no branch then is a commit sha
        branch_or_sha = branch
    
    branch_name = branch
    
    selected_commit = repo[branch_or_sha]
    
    #Get files
    tree_files={}
    splitted_path = tree_path.split('/')
    #Get filename (maybe we need fo the blob)
    file_name = splitted_path[len(splitted_path)-1]
    #if we are root folder then empty list
    if len(splitted_path) == 1 and splitted_path[0] =='':
        splitted_path = []
    else:    
        splitted_path.reverse()
    
    tree = repo[selected_commit.tree]
    #for tree_file in tree.iteritems():
    #    tree_files[tree_file] = stat.S_ISDIR(tree_file[1])
    
    tree_files = utils.get_repo_files(repo, tree, splitted_path)
    
    
    #Show file content if is a blob (raw file, not dir)
    if isinstance(tree_files, Blob):
        file_code = tree_files.as_raw_string()

        return render_template('file-detail.html', repo_key=repo_key, branch=branch_name,
                                file_code=file_code, file_name=file_name)
    #Show tree if is a empty path (root folder) or a subforlder
    else:
        #Check readme
        readme = ''
        readme_name = ''
        for maybe_readme, directory in tree_files.iteritems():
            if 'readme' in maybe_readme[0].lower():
                readme_name = maybe_readme[0]
                readme = repo[maybe_readme[2]].as_raw_string()
                break
        
        #Little hack for the url generating
        tree_path = tree_path + '/' if tree_path is not '' else tree_path
        
        return render_template('repo-dashboard.html', repo_key=repo_key, branch=branch_name, 
                                tree_files=tree_files, readme=readme, readme_name=readme_name, 
                                tree_path=tree_path)
                        

@app.route('/<repo_key>/commits/<branch>/')
def commit_history(repo_key, branch):
    
    repo = Repo(settings.REPOS[repo_key])
    
    #get all the branches and set the name branch in a ref list (don't 
    #add the selected one, this will be added sepparetly in the template)
    references = []
    selected_branch = branch
    for ref, sha in repo.get_refs().iteritems():
        #get the name of the branch without the pefix
        if (LOCAL_BRANCH_PREFIX in ref):
            references.append(ref.replace(LOCAL_BRANCH_PREFIX, '', 1))
    
    #Get the branch walker
    walker = repo.get_walker(include = [repo.get_refs()[LOCAL_BRANCH_PREFIX+branch], ])
    
    
    #Start getting all the commits from the branch
    commits = []
    commits_per_day = []
    previous_commit_time = None
    
    #Group commits by day (I use list instead of a dict because the list is ordered already, so I don't need to sort the dict)
    for i in walker:
        
        commit = i.commit
        commit_time = filters.convert_unix_time_filter(commit.commit_time, '%d %b %Y')
        
        #if is new or like the previous one time, then add to the list, if not then save the list and create a new one
        if (previous_commit_time is None) or (commit_time == previous_commit_time):
            commits_per_day.append(commit)
        else:
            commits.append(commits_per_day)
            commits_per_day = [commit,]
        
        previous_commit_time = commit_time
        
    #Add last ones
    commits.append(commits_per_day)
    return render_template('commit-history.html', commits=commits, repo_key=repo_key, 
                            references = references, selected_branch=selected_branch)


@app.route('/<repo_key>/commit/<commit_key>/')
def commit_detail(repo_key, commit_key):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    commit = repo[commit_key]
        
    return render_template('commit-detail.html', commit=commit)


if __name__ == "__main__":
    app.run(debug=settings.DEBUG)
