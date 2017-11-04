from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.db import connection, IntegrityError, transaction
from datetime import datetime, date
import re

def home(request):
		return render(request,'home.html')

def signup(request):
	if request.POST:
		email = request.POST['email']
		fname = request.POST['fname']
		lname = request.POST['lname']
		password = request.POST['psw']
		username = request.POST['uname']
		repasssword = request.POST['rpsw']
		phone = request.POST['phone']
		address = request.POST['address']
		if not re.match(r"[^@]+@[^@]+\.[^@]+",email):
			messages.error(request, 'E-Mail is not valid.')
			return render(request,"signup.html")
		if not phone.isdigit():
			messages.error(request, 'Phone number must be a number.')
			return render(request,"signup.html")
		if len(phone)!=10:
			messages.error(request, 'Please enter a valid mobile number.')
			return render(request,"signup.html")
		if len(password)<6:
			messages.error(request, 'Password must be greater than 6 characters.')
			return render(request,"signup.html")
		if password!=repasssword:
			messages.error(request, 'Passwords entered do not match.')
			return render(request,"signup.html")
		cursor = connection.cursor()
		cursor.execute("SELECT username FROM auth_user where username='%s';" %(username))
		uname = cursor.fetchall()

		if len(uname)!=0:
			messages.error(request, 'Username already exists. Please choose another one.')
			return render(request,"signup.html")
		u = User.objects.create_user(username=username,password=password,first_name=fname,last_name=lname,email=email)
		cursor.execute("INSERT INTO customer(name,email,phone,address,user) values('%s','%s','%s','%s',%d)" %(fname+" "+lname,email,phone,address,u.id))
		us = auth.authenticate(username=username, password=password)
		auth.login(request,us)
		messages.success(request, 'Successfully Registered!')
		return render(request,"home.html")
	else:
		return render(request,"signup.html")

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		messages.success(request, 'Successfully logged out.')
	return HttpResponseRedirect(reverse('login'))

@csrf_protect
def login(request):
	if request.user.is_authenticated():				# Check if user is already logged in
			return HttpResponseRedirect(reverse('home'))
	if request.POST:								# GET.get Method
		username = request.POST['uname']
		password = request.POST['psw']
		if username == '':
			return render(request, 'login.html')

		cursor = connection.cursor()				# Establish connection with MySQL database
		cursor.execute("SELECT * from auth_user where username='"+(username)+"';")
		data = cursor.fetchone()
		connection.close()

		if data is not None:				# Check if user is registered
			username = data[4]
			user = auth.authenticate(username=username, password=password)			# Authenticates the username and password
			if user is not None:
				auth.login(request, user)											# Logs in
				return HttpResponseRedirect(reverse('home'))
			else:																	# User exists but password is incorrect
				messages.error(request, 'The username and password combination is incorrect.')
		else:
			messages.error(request, 'Username not registered.')							# User does not exist
	return render(request, 'login.html')

def dashboard(request):
	if not request.user.is_authenticated():								# Directs to login page if user is not logged in
		return HttpResponseRedirect(reverse('login'))
	if request.user.is_staff:
		return HttpResponseRedirect(reverse('admin_dashboard'))			# Directs to admin dashboard if user is admin
	cursor = connection.cursor()
	cursor.execute("SELECT * from faculty_member where faculty_id='"+request.user.username+"';")
	data = cursor.fetchone()
	cursor.execute("SELECT dept_name, faculty from department where dept_id='"+data[2]+"';")
	dep = cursor.fetchone()
	connection.close()

	# Sends details of user to be displayed
	details = {'f_id':data[0], 'name':data[3]+' '+data[4]+' '+data[5], 'desig':data[6], 'email':data[8], 'dept':dep[0], 'fac':dep[1]}
	return render(request, 'dashboard.html', details)


def items(request):
	cursor = connection.cursor()
	s = "SELECT * from items "
	
	if request.GET:
		if request.user.is_superuser():
			dealerid = request.GET.get('dealerid')
		if request.GET.get('name') or request.GET.get('category') or request.GET.get('price'):
			s = s + "where "
			if request.GET.get('name'):
				s = s + "name='" + request.GET.get('name') + "' and "
			if request.GET.get('category'):
				s = s + "category='" + request.GET.get('category') + "' and "
			if request.GET.get('price'):
				s = s + "price<=" + str(request.GET.get('price')) + " and "
			s = s[:-5]+";"
		else:
			cursor.execute(s)
			items_list = cursor.fetchall()
			return render(request,"items.html",{"item":items_list,'dealerid':dealerid})

	cursor.execute(s)
	items_list = cursor.fetchall()
	return render(request,"items.html",{"item":items_list})

def additems(request):
	if request.GET:
		cursor = connection.cursor()
		i = ()
		cursor.execute("SELECT item_id FROM items where name='%s' and brand='%s'" %(request.GET.get('nam'),request.GET.get('bran')))
		i = cursor.fetchall()
		if len(i)!=0:
			messages.error(request,'This item already exists.')
			return HttpResponseRedirect(reverse('items'))
		if request.GET.get('descriptio'):
			s = "INSERT INTO items(name,category,price,brand,quantity,description) values ('" + request.GET.get('nam') + "','" + request.GET.get('categor') + "'," + request.GET.get('pric') + ",'" + request.GET.get('bran') + "'," + request.GET.get('qty') + ",'" + request.GET.get('descriptio') + "');"
		else:
			s = "INSERT INTO items(name,category,price,brand,quantity,description) values ('" + request.GET.get('nam') + "','" + request.GET.get('categor') + "'," + request.GET.get('pric') + ",'" + request.GET.get('bran') + "'," + request.GET.get('qty') + ",'" + 'There is no description available for this product.' + "');"	
		print
		print s
		cursor.execute(s)
		return HttpResponseRedirect(reverse('items'))

def edititems(request):
		cursor = connection.cursor()
		if request.GET.get('nam'):
			cursor.execute("UPDATE items set name='" + request.GET.get('nam') + "' where item_id=" + request.GET.get('id') + ";")
		if request.GET.get('categor'):
			cursor.execute("UPDATE items set category='" + request.GET.get('categor') + "' where item_id=" + request.GET.get('id') + ";")
		if request.GET.get('pric'):
			cursor.execute("UPDATE items set price=" + request.GET.get('pric') + " where item_id=" + request.GET.get('id') + ";")
		if request.GET.get('bran'):
			cursor.execute("UPDATE items set brand='" + request.GET.get('bran') + "' where item_id=" + request.GET.get('id') + ";")
		if request.GET.get('qty'):
			cursor.execute("UPDATE items set quantity=" + request.GET.get('qty') + " where item_id=" + request.GET.get('id') + ";")
		if request.GET.get('descriptio'):
			cursor.execute("UPDATE items set description='" + request.GET.get('descriptio') + "' where item_id=" + request.GET.get('id') + ";")
		return HttpResponseRedirect(reverse('items'))

def delitems(request):
	print
	print request.GET.get('delid')
	print
	cursor = connection.cursor()
	cursor.execute("DELETE FROM items where item_id=" + request.GET.get('delid') + ";")
	return HttpResponseRedirect(reverse('items'))

def addtocart(request):
	if request.user.is_superuser:
		cursor = connection.cursor()
		userid = request.user.id
		cursor.execute("SELECT dealer_id FROM dealer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
		s = cursor.fetchone()
		cursor.execute("SELECT max(order_id) FROM customerorder where customer_id="+str(s[0])+";")
		orderid = cursor.fetchone()
		already_present=()
		cursor.execute("SELECT item_id FROM corderline where order_id=%s and item_id=%s" %(orderid[0],request.GET.get('cartitemid')))
		already_present = cursor.fetchall()
		if len(already_present)!=0:
			p = "UPDATE corderline SET quantity = quantity+%s where order_id=%s and item_id=%s" %(request.GET.get('quantit'),orderid[0],request.GET.get('cartitemid'))
		else:
			p = "INSERT INTO corderline values("+str(orderid[0])+","+request.GET.get('cartitemid')+","+request.GET.get('quantit')+");"
		cursor.execute(p)

	elif request.user.is_authenticated():
		cursor = connection.cursor()
		userid = request.user.id
		cursor.execute("SELECT customer_id FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
		s = cursor.fetchone()
		cursor.execute("SELECT max(order_id) FROM customerorder where customer_id="+str(s[0])+";")
		orderid = cursor.fetchone()
		already_present=()
		cursor.execute("SELECT item_id FROM corderline where order_id=%s and item_id=%s" %(orderid[0],request.GET.get('cartitemid')))
		already_present = cursor.fetchall()
		cursor.execute("SELECT quantity FROM items where item_id=%s" %(request.GET.get('cartitemid')))
		q = cursor.fetchone()
		if len(already_present)!=0:
			cursor.execute("SELECT quantity FROM corderline where order_id=%s and item_id=%s" %(orderid[0],request.GET.get('cartitemid')))
			qt = cursor.fetchone()
			if q[0] < qt[0] + int(request.GET.get('quantit')):
				messages.error(request,"Currently the item is not available in that much quantity. Please enter a smaller quantity.")
				return HttpResponseRedirect(reverse('items'))
			p = "UPDATE corderline SET quantity = quantity+%s where order_id=%s and item_id=%s" %(request.GET.get('quantit'),orderid[0],request.GET.get('cartitemid'))
		else:
			if q[0] < int(request.GET.get('quantit')):
				messages.error(request,"Currently the item is not available in that much quantity. Please enter a smaller quantity.")
				return HttpResponseRedirect(reverse('items'))
			p = "INSERT INTO corderline values("+str(orderid[0])+","+request.GET.get('cartitemid')+","+request.GET.get('quantit')+");"
		cursor.execute(p)
		#cursor.execute("UPDATE items SET quantity=quantity-%s where item_id=%s;" %(request.GET.get('quantit'),request.GET.get('cartitemid')))
		return HttpResponseRedirect(reverse('items'))

total = 0
def checkout(request):
	cursor = connection.cursor()
	userid = request.user.id
	cursor.execute("SELECT customer_id,name,email,phone,address,points FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
	customerid = cursor.fetchone()
	cursor.execute("SELECT max(order_id) FROM customerorder where customer_id="+str(customerid[0])+";")
	orderid = cursor.fetchone()
	cursor.execute("SELECT item_id FROM corderline where order_id="+str(orderid[0])+";")
	itemid = cursor.fetchall()
	cursor.execute("SELECT quantity FROM corderline where order_id="+str(orderid[0])+";")
	quantity = cursor.fetchall()
	itemlist = []
	count=0
	for i in itemid:
		for j in i:
			cursor.execute("SELECT * FROM items where item_id="+str(j)+";")
			q = list(cursor.fetchone())
			q.append(quantity[count][0])
			count = count + 1
			itemlist.append(q)
	count = 0
	discount = 0
	global total
	entry = 1
	p=0
	subtotal=0
	for i in itemlist:
		itemlist[count][3] = itemlist[count][3]*itemlist[count][7]
		subtotal = subtotal + itemlist[count][3]
		count = count + 1
	if subtotal<=500:
		discount = 0
	elif subtotal<=1000 and subtotal>=500:
		discount = 10
	elif subtotal<=2000:
		discount = 20
	elif subtotal<=3000:
		discount = 30
	else:
		discount = 50
	if request.GET.get('enter')=='1':
		if int(customerid[5]) < 10:
			messages.error(request,"You have less than 10 points in your account.")
			total = subtotal - (subtotal*discount/100)
			entry = 0
		else:
			cursor.execute("UPDATE customer SET points=0 where customer_id=%s;" %(customerid[0]))
			total = subtotal - (subtotal*discount/100) - int(customerid[5])/10
			p = int(customerid[5])/10
			cursor.execute("SELECT customer_id,name,email,phone,address,points FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
			customerid = cursor.fetchone()
			entry = 2
	else:
		total = subtotal - (subtotal*discount/100)
	return render(request,"checkout.html",{'adddiscount': p,'entry':entry,'customerdetails':customerid, 'item':itemlist, 'oid':orderid[0],'total':total,'subtotal':subtotal,'discount':discount})

def remove(request):
	cursor = connection.cursor()
	cursor.execute("DELETE FROM corderline where item_id="+request.GET.get('iid')+" and order_id="+request.GET.get('oid')+";")
	return HttpResponseRedirect(reverse('checkout'))

def place(request):
	global total
	cursor = connection.cursor()
	userid = request.user.id
	cursor.execute("SELECT customer_id,name,email,phone,address FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
	customerid = cursor.fetchone()
	cursor.execute("SELECT order_id,date FROM customerorder where customer_id="+str(customerid[0])+" order by order_id desc;")
	orderid = cursor.fetchone()
	cursor.execute("UPDATE customerorder SET total=%d,placed=1 where order_id=%s;" %(total,orderid[0]))
	cursor.execute("UPDATE customer SET points=points+%d,purchases=purchases+1 where customer_id=%s;" %(total/10,customerid[0]))
	cursor.execute("SELECT item_id,quantity FROM corderline where order_id="+str(orderid[0])+";")
	itemid = cursor.fetchall()
	for i in itemid:
		cursor.execute("UPDATE items SET quantity=quantity-%s where item_id=%s" %(i[1],i[0]))
	return render(request,"place.html",{'oid':orderid[0],'total':total,'date':orderid[1]})

def order(request):
	if request.user.is_superuser:
		return HttpResponseRedirect(reverse('items'))
	elif request.user.is_authenticated():
		cursor = connection.cursor()
		userid = request.user.id
		cursor.execute("SELECT customer_id,name,email,phone,address FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
		customerid = cursor.fetchone()
		cursor.execute("INSERT INTO customerorder(customer_id) values(%s);" %(customerid[0]))
		return HttpResponseRedirect(reverse('items'))

def profile(request):
	if request.user.is_superuser:
		cursor = connection.cursor()
		cursor.execute("SELECT count(*) FROM customerorder;")
		totalorder = cursor.fetchone()
		cursor.execute("SELECT sum(total) FROM customerorder;")
		totalamount = cursor.fetchone()
		return render(request,"profile.html",{'totalorder':totalorder[0],'enter':0,'totalamount':totalamount[0],'enter':0})
	elif request.user.is_authenticated():
		cursor = connection.cursor()
		userid = request.user.id
		cursor.execute("SELECT customer_id,name,email,phone,address,points,purchases FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
		customerid = cursor.fetchone()
		return render(request,"profile.html",{'cdetails':customerid,'enter':0})

def pending(request):
	cursor = connection.cursor()
	cursor.execute("SELECT order_id,name,address,phone,status FROM customer,customerorder where customer.customer_id=customerorder.customer_id and customerorder.status='Pending';" )
	details = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM customerorder;")
	totalorder = cursor.fetchone()
	cursor.execute("SELECT sum(total) FROM customerorder;")
	totalamount = cursor.fetchone()
	return render(request,"profile.html",{'enter':1,'details':details,'totalorder':totalorder[0],'totalamount':totalamount[0]})

def allorder(request):
	cursor = connection.cursor()
	cursor.execute("SELECT order_id,name,address,phone,status FROM customer,customerorder where customer.customer_id=customerorder.customer_id;" )
	details = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM customerorder;")
	totalorder = cursor.fetchone()
	cursor.execute("SELECT sum(total) FROM customerorder;")
	totalamount = cursor.fetchone()
	return render(request,"profile.html",{'enter':2,'details':details,'totalorder':totalorder[0],'totalamount':totalamount[0]})

def changestatus(request):
	cursor = connection.cursor()
	cursor.execute("UPDATE customerorder SET status='Delivered' where order_id=%s;" %(request.GET.get('oid')))
	if request.GET.get('enter')=='1':
		return HttpResponseRedirect(reverse('pending'))
	else:
		return HttpResponseRedirect(reverse('allorder'))

def deleteorder(request):
	cursor = connection.cursor()
	cursor.execute("DELETE FROM customerorder where order_id=%s;" %(request.GET.get('oid')))
	if request.GET.get('enter')=='1':
		return HttpResponseRedirect(reverse('pending'))
	elif request.GET.get('enter')=='2':
		return HttpResponseRedirect(reverse('allorder'))
	else:
		return HttpResponseRedirect(reverse('prevorder'))

def editdetails(request):
	cursor = connection.cursor()
	cursor.execute("UPDATE customer SET name='%s',email='%s',phone='%s',address='%s' where customer_id=%s" %(request.GET.get('nam'),request.GET.get('emai'),request.GET.get('phon'),request.GET.get('addres'),request.GET.get('id')))
	messages.success(request,"Details Successfully Updated!")
	return HttpResponseRedirect(reverse('profile'))

def prevorder(request):
	cursor = connection.cursor()
	userid = request.user.id
	cursor.execute("SELECT customer_id,name,email,phone,address FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
	customerid = cursor.fetchone()
	cursor.execute("SELECT order_id,date,status,total FROM customerorder where customer_id="+str(customerid[0])+" and placed=1"+" order by order_id desc;")
	orderid = cursor.fetchall()
	l = []
	for i in orderid:
		k = []
		k.append(i)
		cursor.execute("SELECT name,brand,category,price,quantity from items,corderline where corderline.order_id=%s and corderline.item_id=items.item_id;" %(i[0]))
		display = list(cursor.fetchall())
		k.append(display)
		l.append(k)
	print l
	return render(request,"profile.html",{'display':l,'oid':orderid,'t':'1','cdetails':customerid})

def offers(request):
	return render(request,"offers.html")

# def points(request):
# 	cursor = connection.cursor()
# 	userid = request.user.id
# 	cursor.execute("SELECT points FROM customer where user="+str(userid)+";") # place this ("+str(userid)+";") instead of (1;")
# 	points = cursor.fetchone()
# 	global point_discount
# 	point_discount = int(points[0])/10
# 	return HttpResponseRedirect(reverse('checkout'))

def test(request):
	return render(request,"test.html",{'dat':234})






