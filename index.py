from google.appengine.api import users

import webapp2
from jinja2env import jinja_environment as je
import make_test

    
class MainPage(webapp2.RequestHandler):

    def get(self):
    
        user = users.get_current_user()

        if user:
            make_test.test_band()    
            template = je.get_template('index.html')
            self.response.write( template.render(
                title='fishy'
            ) )        
        else:
            self.redirect(users.create_login_url(self.request.uri))