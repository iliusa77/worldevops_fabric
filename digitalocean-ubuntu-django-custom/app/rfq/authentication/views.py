from django.contrib.auth import authenticate, login as authlogin, logout
from django.contrib import auth
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from django.db.models import Q

from userprofile.models import *
from quote.models import *
from .models import *

from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

#@csrf_exempt   # Need to be removed
def login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        print 'user', user, request.user
        if user is not None:
            authlogin(request, user)
            prof = Profile.objects.get(user = user)
            request.session['type'] = prof.type

            #return HttpResponseRedirect('/')
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response('registration/login.html', {'eid':True}, context_instance=RequestContext(request))            


    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')      

    return render_to_response('registration/login.html', {}, context_instance=RequestContext(request))


def logout1(request):
    auth.logout(request)
    return HttpResponseRedirect('/')



def home(request):

    c = {}
    if request.user.is_authenticated():
        if request.user.profile.type in [Profile.UserTypes.ADMIN]:
            quote_items = QuoteInfo.objects.filter(alert=True)
        elif request.user.profile.type == Profile.UserTypes.ADMINISTRATOR:
            quote_items = QuoteInfo.objects.filter(status="po_issued",alert=True)
        elif request.user.profile.type == Profile.UserTypes.USER:
            quote_items = QuoteInfo.objects.filter(requester=request.user,alert=True)
        elif request.user.profile.type == Profile.UserTypes.APPROVER:
            quote_items = QuoteInfo.objects.filter(alert=True)
        elif request.user.profile.type == Profile.UserTypes.OTHERUSER:
            quote_items = QuoteInfo.objects.filter(Q(status__icontains="po_issued") | Q(status__icontains="generate_po") | Q(status__icontains="order_in_production") | Q(status__icontains="order_complete"),alert=True)

        nots = quote_items
        c['nots'] = nots
    else:
        return HttpResponseRedirect(reverse(login))


    news = New.objects.filter(display=True)
    c['news'] = news

    return render(request, 'home.html', c)



import sys
import os.path
import os
import logging
from datetime import datetime

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

import cStringIO as StringIO

BACKUP_DIR =  "backups"
DATABASE_NAME = "choice_portal"
DATABASE_USER = "root"
DATABASE_PASSWORD = "rooted"




@login_required
def dbbackup(request):

    _setup()
    file_name = _backup_name()
    _run_backup(file_name)

    x = _zip_backup(file_name)

    print file_name

    file_path = BACKUP_DIR+"/"+file_name + ".zip"

    print file_path

    # generate the file
    response = HttpResponse(FileWrapper(file(file_path, "r")), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + file_name + ".zip"
    return response



logging.basicConfig(level=logging.INFO, stream=sys.stdout)


MYSQL_CMD = 'mysqldump'
ZIP_CMD = 'zip'

def _setup():
    if not os.path.exists(BACKUP_DIR):
        logging.debug("Created backup directory %s" % BACKUP_DIR)
        os.mkdir(BACKUP_DIR)
    else:
        logging.debug("Using backup directory %s" % BACKUP_DIR)
    
def _backup_name():
    now = datetime.now()
    day_name = now.strftime("%A")
    file_name = "%s.sql" % day_name.lower() 
    logging.debug("Setting backup name for day name %s as %s" % (day_name, file_name))
    return file_name

def _run_backup(file_name):
    cmd = "%(mysqldump)s -u %(user)s --password=%(password)s %(database)s > %(log_dir)s/%(file)s" % {
        'mysqldump' : MYSQL_CMD,
        'user' : DATABASE_USER,
        'password' : DATABASE_PASSWORD,
        'database' : DATABASE_NAME,
        'log_dir' : BACKUP_DIR,
        'file': file_name}
    logging.debug("Backing up with command %s " % cmd)
    return os.system(cmd)

def _zip_backup(file_name):
    backup = "%s/%s" % (BACKUP_DIR, file_name)
    zipfile_name = "%s.zip" % (backup)

    if os.path.exists(zipfile_name):
        logging.debug("Removing previous zip archive %s" % zipfile_name)
        os.remove(zipfile_name)
    zip_cmds = {'zip' : ZIP_CMD, 'zipfile' : zipfile_name, 'file' : backup }

    # Create the backup
    logging.debug("Making backup as %s " % zipfile_name)
    os.system("%(zip)s -q -9 %(zipfile)s %(file)s" % zip_cmds)

    # Test our archive
    logging.debug("Testing zip archive")
    if not os.system("%(zip)s -T -D -q %(zipfile)s" % zip_cmds):
        # If there was no problem, then delete the unzipped version
        os.remove(backup)
        return True
    else:
        return False