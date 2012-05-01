from flask import Flask, render_template, request
from flaskext import gravatar, markdown


import sys
import pygit2
import settings
import filters

app = Flask(__name__)

#Extensions
gravatar = gravatar.Gravatar(app,
                    size=50,
                    rating='g',
                    default='mm',
                    force_default=False,
                    force_lower=False)

markdown.Markdown(app)

#View
@app.route('/')
def index():
    
    # Compound statements only available in 2.7 (http://docs.python.org/reference/compound_stmts.html)
    #repos = {key:pygit2.Repository(path) for key, path in settings.REPOS.iteritems()}
    
    repos = {}
    for key, path in settings.REPOS.iteritems():
        repos[key] = pygit2.Repository(path)
    
    return render_template('index.html', repos=repos)

@app.route('/<repo_key>/tree/<branch>/')
def repo_dashboard(repo_key, branch):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    #Get the branch
    prefix = 'refs/heads/'
    branch = repo.lookup_reference(prefix + branch)
    branch = branch.resolve()
    
    #get the tree of files
    tree = repo[branch.oid].tree
    tree_files = {}
    
    for tree_file in tree:
        if 'README' in tree_file.name.upper():
            readme = tree_file.to_object().read_raw().decode("utf-8")
    
    return render_template('repo-dashboard.html', repo_key=repo_key, branch=branch, 
                            tree_files=tree_files, readme=readme)
                            

@app.route('/<repo_key>/tree/<branch>/commits/')
def commit_history(repo_key, branch):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    #get all teh branches and set the name branch in a ref list (don't 
    #add the selected one, this will be added sepparetly in the template)
    references = []
    prefix = 'refs/heads/'
    selected_branch = branch
    for ref in repo.listall_references():
        #get the name of the branch without the pefix
        if (prefix in ref):
            references.append(ref.replace(prefix, '',1))
    
    
    
    #Get the branch
    branch = repo.lookup_reference(prefix + branch)
    branch = branch.resolve()
    
    
    #Start getting all the commits from the branch
    commits = []
    commits_per_day = []
    previous_commit_time = None
    
    #Group commits by day (I use list instead of a dict because the list is ordered already, so I don't need to sort the dict)
    for commit in repo.walk(branch.oid, pygit2.GIT_SORT_TIME):
        
        commit_time = filters.convert_unix_time_filter(commit.author.time, '%d %b %Y')
        
        #if is new or like the previous one time, then add to the list, if not then save the list and create a new one
        if (previous_commit_time is None) or (commit_time == previous_commit_time):
            commits_per_day.append(commit)
        else:
            commits.append(commits_per_day)
            commits_per_day = [commit,]
        
        previous_commit_time = commit_time
    
    return render_template('commit-history.html', commits=commits, repo_key=repo_key, 
                            references = references, selected_branch=selected_branch)


@app.route('/<repo_key>/commit/<commit_key>/')
def commit_detail(repo_key, commit_key):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    commit = repo[commit_key]
        
    return render_template('commit-detail.html', commit=commit)


if __name__ == "__main__":
    app.run(debug=settings.DEBUG)
