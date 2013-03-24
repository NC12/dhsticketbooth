# Filename: main.py
# Name: Ng Cheryl
# Description: receive ticket orders from user and write to datastore
import webapp2
import jinja2
import os
import datetime
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
from google.appengine.api import mail	# send email
import cgi

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
            query = Person.gql("WHERE email = :1", users.get_current_user().email())
            result = query.fetch(1)
            template = jinja_environment.get_template('index.html')
            if result: # record exists
                student = result[0]
                person = student.name + "'s"
                url = users.create_logout_url(self.request.uri)
                url_linktext = "Logout"
            else: # not found
                person = False
                url = users.create_logout_url(self.request.uri)
                url_linktext = "Unauthorised"
                template = jinja_environment.get_template('404.html')
        else: # not logged in
            person = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"
            template = jinja_environment.get_template('404.html')
        template_values = {
	    'person': person,
	    'url': url,
	    'url_linktext': url_linktext,
		}
        self.response.write(template.render(template_values))

class Order(db.Expando):
    """Ticket order with name, class, email, number of tickets and date"""
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
            if user:
                query = Person.gql("WHERE email = :1", users.get_current_user().email())
                result = query.fetch(1)
                if result:
                    person = result[0]
                    tickets = int(self.request.get('tickets'))
                    if tickets:
                        # Create an order in the datastore
                        t = Order(name = person.name, user_class = person.user_class, email = person.email, ticketNum = tickets)
                        t.put()
                        self.redirect('/')    
                else:
                    self.redirect('/order')            
            

class ViewOrder(webapp2.RequestHandler):
    def get(self):
        query = Order.gql("WHERE email = :1", users.get_current_user().email()) 
        result = query.fetch(1)
        if result:
            orders = result[0]
            self.response.out.write('Number of tickets:')
        else:
            orders = False
            self.response.out.write('You have no orders')   
        template_values = {'orders':orders}
        template = jinja_environment.get_template('view.html')
        self.response.write(template.render(template_values))

class EditOrder(webapp2.RequestHandler):
    def post(self):
        if self.request.get("edit"):
            updated_tickets = int(self.request.get('updated_tickets'))
            query = Order.gql("WHERE email = :1", users.get_current_user().email())
            result = query.fetch(1)
            if result:
                orders = result[0]
                orders.ticketNum = updated_tickets
                orders.put()
                self.redirect('/')
            else:
                self.response.out.write('Error in saving.')
                
class DeleteOrder(webapp2.RequestHandler):
    def post(self):
        if self.request.get("delete"):
            query = Order.gql("WHERE email = :1", users.get_current_user().email())
            result = query.fetch(1)
            db.delete(result)
            self.redirect('/')
        else:
            self.response.out.write('Error in editing')
# main
# example of person
# p0 = Person(pid='lim.ahseng',name='LIM AH SENG',user_class='13Y5C',email='lim.ahseng@person.com')
# p0.put()               
app = webapp2.WSGIApplication([('/', MainHandler), ('/order', OrderTickets), ('/view', ViewOrder), ('/edit', EditOrder), ('/delete', DeleteOrder)], debug=True)
