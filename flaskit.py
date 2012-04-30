from flask import Flask, render_template
from flaskext import gravatar
import sys
import pygit2
import settings
import filters

app = Flask(__name__)

gravatar = gravatar.Gravatar(app,
                    size=50,
                    rating='g',
                    default='mm',
                    force_default=False,
                    force_lower=False)

#View
@app.route('/')
def index():
    
    # Compound statements only available in 2.7 (http://docs.python.org/reference/compound_stmts.html)
    #repos = {key:pygit2.Repository(path) for key, path in settings.REPOS.iteritems()}
    
    repos = {}
    for key, path in settings.REPOS.iteritems():
        repos[key] = pygit2.Repository(path)
    
    return render_template('index.html', repos=repos)


@app.route('/<repo_key>')
def repo_details(repo_key):
    
   
    
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    head = repo.lookup_reference('HEAD')

    head = head.resolve()
    
    commits = []
    commits_per_day = []
    previous_commit_time = None
    
    #Group commits by day (I use list instead of a dict because the list is ordered already, so I don't need to sort the dict)
    for commit in repo.walk(head.oid, pygit2.GIT_SORT_TIME):
        
        commit_time = filters.convert_unix_time_filter(commit.author.time, '%d %b %Y')
        
        #if is new or like the previous one time, then add to the list, if not then save the list and create a new one
        if (previous_commit_time is None) or (commit_time == previous_commit_time):
            commits_per_day.append(commit)
        else:
            commits.append(commits_per_day)
            commits_per_day = [commit,]
        
        previous_commit_time = commit_time
    
    return render_template('commit-history.html', commits=commits, repo_key=repo_key)


@app.route('/<repo_key>/commit/<commit_key>')
def commit_detail(repo_key, commit_key):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    commit = repo[commit_key]
        
    return render_template('commit-detail.html', commit=commit)


if __name__ == "__main__":
    app.run(debug=settings.DEBUG)
