#!/usr/bin/python2.5 -u
# coding=utf-8

#
# queue_candidate_survey_email_invites.py:
# Sets up tasks to invite specfied sets of candidates
#
# Copyright (c) 2010 UK Citizens Online Democracy. All rights reserved.
# Email: francis@mysociety.org; WWW: http://www.mysociety.org/
#

import sys
import csv
import os
import getpass
import datetime
import optparse

sys.path = ["../", "../google_appengine/"] + sys.path
from google.appengine.ext import db
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.api.datastore_types import Key

# XXX remember to migrate this when the API becomes stable
from google.appengine.api.labs import taskqueue

from models import Party, Candidate, Seat, Candidacy, RefinedIssue

######################################################################
# Helpers

def log(msg):
    print datetime.datetime.now(), msg.encode('utf-8')

def group_by_n(lst, n):
    return [lst[i:i+n] for i in range(0,len(lst),n)]

######################################################################
# Actions

def get_seats_list_from_options(options):
    seats_list = []
    if options.constituency != None:
        log("Getting individual constituency " + options.constituency)
        seat = db.Query(Seat).filter("name =", options.constituency).get()
        seats_list.append(seat)

    if options.constituency_list != None:
        for seat_name in open(options.constituency_list):
            seat_name = seat_name.strip()
            # DemocracyClub doesn't have accent on this seat name
            seat_name = seat_name.replace("Ynys Mon", "Ynys Môn")
            seat_name = seat_name.decode('utf-8')
            log("Getting list constituency " + seat_name)
            seat = db.Query(Seat).filter("name =", seat_name).get()
            if not seat:
                raise Exception("Couldn't find seat: " + seat_name)
            seats_list.append(seat)

    if len(seats_list) == 0:
        log("Getting all constituencies")
        seats_list = db.Query(Seat).order('name').fetch(1000)
        assert len(seats_list) != 1000

    return seats_list

def filter_query_from_options(candidacies, options):
    candidacies.filter("deleted = ", False)
    candidacies.filter("survey_invite_emailed = ", False)
    candidacies.filter("survey_filled_in = ", False)

    return candidacies

global_email_delta = 0
def do_for_candidacy(candidacy, seat):
    global global_email_delta

    assert seat.frozen_local_issues

    if not candidacy.candidate.validated_email():
        log("Not queueing, invalid email " + str(candidacy.candidate.email) + " for candidacy " + seat.name + ", " + candidacy.candidate.name)
    else:
        global_email_delta += 2 # two seconds between sending each mail, try to keep within GAE limits
        if options.real:
            log(str(global_email_delta) + " queued invite for candidacy " + seat.name + ", " + candidacy.candidate.name + " email: " + candidacy.candidate.email)
            eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=global_email_delta) # AppEngine servers use UTC
            taskqueue.Queue('survey-email').add(taskqueue.Task(url='/task/invite_candidacy_survey/' + str(candidacy.key().name()), eta = eta))
            candidacy.log("Queued task to send survey invite email")
        else:
            log(str(global_email_delta) + " would queue invite for candidacy " + seat.name + ", " + candidacy.candidate.name+ " email: " + candidacy.candidate.email)

def do_for_some_seats(seats, options):
    # Can only do IN for a small number of constituencies at a time (max, I
    # think, 25), so do in smaller groups
    c = 0
    for seat in seats:
        log(str(c) + "/" + str(len(seats)) + " - Doing constituency: " + seat.name)
        c += 1

        frozen = seat.frozen_local_issues
        if not frozen and options.freeze:
            if options.real:
                seat.frozen_local_issues = True
                seat.put()
                log("Frozen local issues for seat: " + seat.name)
            else:
                log("Would freeze local issues for seat: " + seat.name)
            frozen = True

        if frozen:
            candidacies = seat.candidacy_set
            candidacies = filter_query_from_options(candidacies, options)
            for candidacy in candidacies:
                do_for_candidacy(candidacy, seat)
        else:
            log("Skipping, seat isn't frozen for local issues: " + seat.name)

        log("") # spacing to make it look nicer


######################################################################
# Main

parser = optparse.OptionParser()

parser.set_usage('''Queue tasks to email a bunch of candidates with an invitation to do the survey.

Doesn't send to candidacies who:
  * have been deleted
  * have already been invited by email
  * have invalid email addresses
  * are not in a constituency whose local issues have been fronen
  * already filled in the survey
In addition, you can limit which candidates are invited by constituency and
various other ways using the parameters below.''')
parser.add_option('--constituency', type='string', dest="constituency", help='Name of constituency, default is all constituencies', default=None)
parser.add_option('--constituency_list', type='string', dest="constituency_list", help='File containing names of constituencies one per line, default is all constituencies', default=None)
parser.add_option('--real', action='store_true', dest="real", help='Really queue the emails, default is dry run', default=False)
parser.add_option('--freeze', action='store_true', dest="freeze", help='', default=False)
parser.add_option('--host', type='string', dest="host", help='domain:port of application, default is localhost:8080. e.g. election.theyworkforyou.com', default="localhost:8080")
parser.add_option('--email', type='string', dest="email", help='email address for authentication to application', default="francis@flourish.org")

(options, args) = parser.parse_args()

if options.real:
    log("Real run, will trigger actual email sends")
else:
    log("Dry run only, no emails will be triggered")

# Configure connection via remote_api to datastore - after this
# data store calls are remote
log("Connecting to " + options.host)
def auth_func():
    return (options.email, getpass.getpass('Password:'))
remote_api_stub.ConfigureRemoteDatastore('theyworkforyouelection', '/remote_api', auth_func, servername=options.host)

# Do the action
seats = get_seats_list_from_options(options)
assert len(seats) > 0
do_for_some_seats(seats, options)


