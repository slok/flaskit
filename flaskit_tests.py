import os
import flaskit
import unittest
import tempfile

class FlaskitTestCase(unittest.TestCase):

    def setUp(self):
        flaskit.app.config['TESTING'] = True
        self.app = flaskit.app.test_client()

    def tearDown(self):
        pass
        
    def test_list_repos(self):
        rv = self.app.get('/')
        assert '<a href="/flaskit/tree/master/">' in rv.data
    
    def test_list_repo_files(self):
        rv = self.app.get('/flaskit/tree/master/')
        
        #Check that are some files and the readme
        assert '<a href="/flaskit/tree/master/README.md/">' in rv.data
        assert '<a href="/flaskit/tree/master/requirements.txt/">' in rv.data
        assert '<a href="/flaskit/tree/master/filters.py/">' in rv.data
        assert '<a href="/flaskit/tree/master/flaskit.py/">' in rv.data
        assert '<a href="/flaskit/tree/master/.gitignore/">' in rv.data
        assert '<a href="/flaskit/tree/master/templates/">' in rv.data
        assert '<a href="/flaskit/tree/master/static/">' in rv.data
        assert '<a href="/flaskit/tree/master/settings.py/">' in rv.data
        assert '<h2>  <i class="icon-book"></i>   README.md</h2>' in rv.data
        
if __name__ == '__main__':
    unittest.main()
