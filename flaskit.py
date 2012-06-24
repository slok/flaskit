from flask import Flask, render_template, request
from flaskext import gravatar, markdown


import sys
import pygit2
import settings
import filters
import stat


from dulwich.repo import Repo

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
    
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    #Get the branch (repo)
    prefix = 'refs/heads/'
    branch_name = branch
    branch = repo.lookup_reference(prefix + branch)
    branch = branch.resolve()
    
    #get the tree of files (here starts everything)
    tree = repo[branch.oid].tree
    
    # If the path isn't the root dir then we have to get the object for
    # the checks of file type, maybe is a regular file or maybe is dir
    if tree_path is not '':
        #Get the last file to display
        tree_files = tree_path.split('/')
    
        def get_entry_recursively(tree, path_file_keys):            
            
            #apply recursively this function until only one file remains for searching
            if len(path_file_keys) > 1:
                search_key = path_file_keys.pop(0)
                #search in our git tree for the name that we want
                for tree_entry in tree:
                    #if we have found the  name, then get that entry from the tree
                    if tree_entry.name == search_key:
                        tree_entry = tree_entry.to_object()
                        break
                #Call again this function to search in the found entry. This are paths so
                # this entry is a tree too and because of this we can do the same with this entry
                #until the las entry is found. In that case we return the entry, then outside of this
                #function we will check if is a directory or is a raw file
                return get_entry_recursively(tree_entry, path_file_keys)
                
            return tree[path_file_keys.pop(0)]
        


        tree_file = get_entry_recursively(tree, tree_files)
        #At this moment in tree_file we have the tree entry (we don't know if is a file or a dir)
    
    #Show tree if is a empty path (root folder) or a subforlder
    if (tree_path is '') or (stat.S_ISDIR(tree_file.attributes)):
        
        tree_files = {}
        readme = None
        readme_name = None
        
        # Check again if is a dir to prepare the subtree if not then the
        # root tree is in the tree var already
        if tree_path is not '':
            tree = repo[tree_file.oid]
        
        for tree_file in tree:
            #If is readme file do one more action
            if 'README' in tree_file.name.upper():
                readme = tree_file.to_object().read_raw().decode("utf-8")
                readme_name = tree_file.name
                
            #if the file is a dir, then mark as directory (for the icon :)
            #FIXME: Sort the dict
            if stat.S_ISDIR(tree_file.attributes):
                tree_files[tree_file] = True
            else:
                tree_files[tree_file] = False
        
        
        #Little hack for the url generating
        tree_path = tree_path + '/' if tree_path is not '' else tree_path
                
        return render_template('repo-dashboard.html', repo_key=repo_key, branch=branch_name, 
                                tree_files=tree_files, readme=readme, readme_name=readme_name, 
                                tree_path=tree_path)
                                
    #Show file content if isn't a directory
    else:
        
        file_code = repo[tree_file.oid].read_raw().decode("utf-8")
        return render_template('file-detail.html', repo_key=repo_key, branch=branch, file_code=file_code)
            
                            

@app.route('/<repo_key>/commits/<branch>')
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
    
    return render_template('commit-history.html', commits=commits, repo_key=repo_key, 
                            references = references, selected_branch=selected_branch)


@app.route('/<repo_key>/commit/<commit_key>/')
def commit_detail(repo_key, commit_key):
    
    repo = pygit2.Repository(settings.REPOS[repo_key])
    
    commit = repo[commit_key]
        
    return render_template('commit-detail.html', commit=commit)


if __name__ == "__main__":
    app.run(debug=settings.DEBUG)
