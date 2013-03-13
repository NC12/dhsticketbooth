# Filename: main.py
# Name: Ng Cheryl
# Description: receive ticket orders from user and write to sqlite database
import webapp2
import jinja2
import os
import datetime
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
from google.appengine.api import mail	# send email

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def format_datetime(value):
    return value.strftime("%d-%m-%Y %H:%M")

jinja_environment.filters['datetime'] = format_datetime

class Person(db.Expando):
    ''' User profile '''
    pid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    user_class = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)


class MainHandler(webapp2.RequestHandler):
    ''' Home page '''
    def get(self):
        user = users.get_current_user()
        if user:
            query = Person.all().filter("email=", user.email())
            #query = Person.gql("WHERE email = :1", user.email())
            result = query.fetch(1)
            if result: # record exists
                person = result[0]
		url = users.create_logout_url(self.request.uri)
                url_linktext = "Logout"
            else: # not found
                person = False
                url = users.create_logout_url(self.request.uri)
                url_linktext = "Logout"
        else: # not logged in
            person = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        template_values = {
	    'person': person,
	    'url': url,
	    'url_linktext': url_linktext,
		}

        if user:
            template = jinja_environment.get_template('index.html')
        else:
            template = jinja_environment.get_template('404.html')
        self.response.write(template.render(template_values))

class Order(db.Model):
    """Models an individual ticket order with name, email, number of tickets and date."""
    name = db.StringProperty(required=True)
    user_class = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    ticketNum = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)

class OrderTickets(webapp2.RequestHandler):
    def get(self):
        """Show the order form"""
        template_values = {}
        template = jinja_environment.get_template('order.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        if self.request.get("confirm"):
            user = users.get_current_user()
            query = Person.all().filter("email=", user.email())
            #query = Person.gql("WHERE email = :1", user.email())
            result = query.fetch(1)
            if result:
                person = result[0]
                t = Order(name = person.name, user_class = person.user_class, email = person.email, ticketNum = cgi.escape(self.request.get('tickets')))
                t.put()
            # go back to home page
            self.redirect('/view')

class ViewOrder(webapp2.RequestHandler):
    def get(self):
        orders = db.GqlQuery("SELECT * "
                            "FROM Order "
                            'WHERE email = :1',
                            users.get_current_user().email())
        if orders:
	    for order in orders:
                self.response.out.write('Number of tickets:')
                self.response.out.write('<b>%s</b>' % cgi.escape(order.ticketNum))
        else:
	    self.response.out.write('You have no orders')   
        template_values = {}
        template = jinja_environment.get_template('view.html')
        self.response.write(template.render(template_values))

# main
# example of person
# p0 = Person(pid='lim.ahseng',name='LIM AH SENG',user_class='13Y5C',email='lim.ahseng@person.com')
# p0.put()
                
app = webapp2.WSGIApplication([('/', MainHandler), ('/order', OrderTickets), ('/view', ViewOrder)], debug=True)
