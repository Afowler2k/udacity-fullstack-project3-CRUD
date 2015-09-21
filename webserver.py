from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from database_setup import Base, Restaurant

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			# display list of restaurants
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				self.displayRestaurants()
				return

			# display page to make a new restaurant
			if self.path.endswith("/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='create'><h2>Make a New Restaurant</h2>"
				output += "<input name='name'type='text' placeholder='new restaurant name'>"
				output += "<input type='submit' value='Create'></form>"	
				output += "</body></html>"	
				self.wfile.write(output)
				print output
				return

			#display page to edit restaurant name
			if self.path.endswith("/edit"):
				parts = self.path.split('/')
				print parts
				print len(parts)
				if len(parts) >= 2:
					restaurantID = parts[len(parts)-2]
					restaurant = session.query(Restaurant).filter(Restaurant.id==restaurantID).first()
					print restaurant.name
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
				
					output = ""
					output += "<html><body>"
					output += "<form method='POST' enctype='multipart/form-data' action='%s/rename'><h2>%s</h2>" % (restaurantID, restaurant.name)
					output += "<input name='name'type='text' placeholder='%s'>" % restaurant.name
					output += "<input type='submit' value='Rename'></form>"	
					output += "</body></html>"	
					self.wfile.write(output)
					print output
					return

			# display confirmation page to delete the restaurant
			if self.path.endswith("/delete"):
				parts = self.path.split('/')
				print parts
				print len(parts)
				if len(parts) >= 2:
					restaurantID = parts[len(parts)-2]
					print restaurantID
					restaurant = session.query(Restaurant).filter(Restaurant.id==restaurantID).first()
					print restaurant.name
				
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
				
					output = ""
					output += "<html><body>"
					output += "<form method='POST' enctype='multipart/form-data' action='%s/delete'><h2>Are you sure you want to delete %s?</h2>" % (restaurantID, restaurant.name)
					output += "<input type='submit' value='Delete'></form>"	
					output += "</body></html>"	
					self.wfile.write(output)
					print output
					return

		except:
			self.send_error(404, "File Not Found %s" % self.path)				

	# helper function to display all restaurants
	def displayRestaurants(self):

		output = ""
		output += "<html><body>"
		output += "Restaurants"
		output += "<br>"
		output += '<a href="http://localhost:8080/restaurants/new">Make a new Restaurant here</a>'

		restaurants = session.query(Restaurant).all()
		if len(restaurants) > 0:
			output += "<ul>"
			for restaurant in restaurants:
				output += "<li>%s" % restaurant.name
				output += "<br>"
				output += '<a href="%s/edit">Edit</a>' % restaurant.id
				output += "<br>"
				output += '<a href="%s/delete">Delete</a>' % restaurant.id
				output += "</li>"
				output += "&nbsp;"
			output += "</ul>"

		output += "</body></html>"	
		self.wfile.write(output)	
		print output
		return


	# handler for POST commands
	def do_POST(self):
		try:
			#handle the create new restaurant
			if self.path.endswith("/restaurants/create"):
				self.send_response(301)	
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newRestaurantName = fields.get('name')
					restaurant = Restaurant(name=newRestaurantName[0])
					session.add(restaurant)
					session.commit()

				self.displayRestaurants();

			# handle renaming a restaurant
			if self.path.endswith("rename"):
				parts = self.path.split('/')
				print parts
				print len(parts)
				if len(parts) >= 2:
					restaurantID = parts[len(parts)-2]
					print restaurantID				

					ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
					if ctype == 'multipart/form-data':
						fields = cgi.parse_multipart(self.rfile, pdict)
						newRestaurantName = fields.get('name')
						restaurant = session.query(Restaurant).filter(Restaurant.id == restaurantID).one()
						restaurant.name = newRestaurantName[0]
						session.add(restaurant)
						session.commit()
						self.send_response(301)	
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()
						return

			# handle deleting a restaurant
			if self.path.endswith("delete"):
				parts = self.path.split('/')
				print parts
				print len(parts)
				if len(parts) >= 2:
					restaurantID = parts[len(parts)-2]
					print restaurantID				

					ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
					if ctype == 'multipart/form-data':
						restaurant = session.query(Restaurant).filter(Restaurant.id == restaurantID).delete()
						session.commit()
						self.send_response(301)	
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()
						return
		except:
			pass


def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered stopping web server..."
		server.socket.close()



if __name__ == '__main__':
	main()

