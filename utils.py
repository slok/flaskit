import stat
from dulwich.objects import Blob

def get_repo_files(repo, tree, path):        
    #Check each file if is in our path
    if len(path) != 0:
        directory = path.pop()
        for tree_file in tree.iteritems():
            if tree_file[0] == directory:
                tree = repo[tree_file[2]]
                #Inception!!! Call again with the new tree and the the cutted path
                final_tree = get_repo_files(repo, tree, path)
                return final_tree
            
        raise Exception("Illegal state in the file path")
    #If not return the files in the subdirectory or the file
    else:
        tree_helper = {}
        #If is a blob then return the blob and don't do a list of files
        if isinstance(tree, Blob):
            return tree
        else:
            for tree_file in tree.iteritems():
                tree_helper[tree_file] = stat.S_ISDIR(tree_file[1])
            return tree_helper