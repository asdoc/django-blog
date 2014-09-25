import pymongo
import gridfs
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bson.objectid import ObjectId

def save(name,content,file_store):
	client = pymongo.MongoClient('localhost',27017).new
	fs = gridfs.GridFS( client )

	fileID = fs.put( file_store )
	file_entry = { 'name':file_store.name, 'file_id':fileID }
	new_entry = { 'author':name , 'content':content , 'hits':0 , 'file':file_entry }
	client.new.insert(new_entry)
	
def get():
	blogs = []
	client = pymongo.MongoClient('localhost',27017).new
	fs = gridfs.GridFS( client )
	x = client.new.find()
	for i in x:
		blog_data = {}
		blog_data['id']=i['_id']
		blog_data['author']=i['author']
		blog_data['content']=i['content']
		blog_data['hits']=str(i['hits'])
		blog_data['file_path']= (str(i['file']['file_id'])+"/"+i['file']['name'])

		tmp = os.system("mkdir app/static/"+str(i['file']['file_id']))
		to_write = open( "app/static/"+(str(i['file']['file_id'])+"/"+i['file']['name']) , 'w' )
		to_write.write(fs.get(i['file']['file_id']).read())
		to_write.close()

		blogs.append(blog_data)
	return blogs

def get_blog(id_blog):
	blogs = []
	client = pymongo.MongoClient('localhost',27017).new
	fs = gridfs.GridFS( client )
	x = client.new.find({'_id':ObjectId(id_blog)})
	client.new.update( {'_id':ObjectId(id_blog)} , { '$inc': {'hits':1}})
	
	for i in x:
		blog_data = {}
		blog_data['id']=i['_id']
		blog_data['author']=i['author']
		blog_data['content']=i['content']
		blog_data['hits']=str(i['hits'])

		blog_data['file_name']=i['file']['name']
		blog_data['file_path']= (str(i['file']['file_id'])+"/"+i['file']['name'])

		tmp = os.system("mkdir app/static/"+str(i['file']['file_id']))
		to_write = open( "app/static/"+(str(i['file']['file_id'])+"/"+i['file']['name']) , 'w' )
		to_write.write(fs.get(i['file']['file_id']).read())
		to_write.close()

		blogs.append(blog_data)
	return blogs
  
def home(request):
	context = { 'blogs': get() }
	return render(request,'home.html',context)
	
def graph(request):
	blogs = []
	max_hits=0
	client = pymongo.MongoClient('localhost',27017).new
	fs = gridfs.GridFS( client )
	x = client.new.find()
	for i in x:
		max_hits=max(max_hits,i['hits'])
		blogs.append(i)
	
	for i in xrange(len(blogs)):
		blogs[i]['percent'] = ((100*float(blogs[i]['hits']))/max_hits)
	context = {'blogs':blogs}
	return render(request,'graph.html',context)
	
@csrf_exempt
def add(request):
	if request.method=="POST":
		author = request.POST['author']
		content = request.POST['content']
		file_store = request.FILES['file']
		save(author,content,file_store)
		return HttpResponse("<html><h1>Saved successfully</h1><br/>Go to <a href='/'>home</a></html>")	
	return render(request,'add.html')
	
def blog(request,id_blog):
	blog_data = get_blog(id_blog)
	print blog_data[0]['file_name']
	blog_ext = blog_data[0]['file_name'].split('.')
	blog_ext = blog_ext[len(blog_ext)-1]
	if blog_ext=='mp4':
		blog_data[0]['video']=True
	else:
		blog_data[0]['video']=False
	context = { 'blogs': blog_data }
	return render(request,'blog.html',context)
