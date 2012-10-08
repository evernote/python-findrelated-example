#!/usr/bin/env python

# Copyright 2012 Evernote Corporation
# All rights reserved.

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

REL_NOTE_COUNT = 3
SEED_NOTE_COUNT = 1

def getSingleNote(authToken, noteStore):
	"""
	Retrieve the newest note from the user's account
	"""
	noteFilter = NoteStore.NoteFilter()
	noteFilter.ascending = True
	try:
		notes = noteStore.findNotes(authToken, noteFilter, 0, SEED_NOTE_COUNT)
		if notes.totalNotes:
			return notes.notes.pop()
	except Exception, e:
		print "Oops! Exception: ", e
		return None

def getRelatedNotes(parameter, authToken, noteStore):
	"""
	Get related notes from Evernote Cloud API based on supplied note or plain text.
	"""
	if not parameter:
		raise Exception("Paramter cannot be empty.")

	query = NoteStore.RelatedQuery()
	if hasattr(parameter,'guid'):
		query.noteGuid = parameter.guid # this is a Note
	else:
		query.plainText = parameter # this is probably plain text

	resultSpec = NoteStore.RelatedResultSpec()
	resultSpec.maxNotes = REL_NOTE_COUNT # 3, currently
	try:
		related = noteStore.findRelated(authToken, query, resultSpec)
		return (related if related.notes else None)
	except Exception, e:
		print "Exception:", e
		return None

def getNonEmptyUserInput(prompt):
	"""
	Prompt the user for input, disallowing empty responses
	"""
	uinput = raw_input(prompt)
	if uinput:
		return uinput
	print "This can't be empty. Try again."
	return getNonEmptyUserInput(prompt)

def displayRelatedNotes(related):
	if related:
		print "Found the following related notes:"
		for note in related.notes:
			print note.title
	else:
		print "No related notes found."

####
# Get auth token, connect to NoteStore and UserStore
####

authToken = "" # bypass the dev token prompt by populating this variable.

if not authToken:
	authToken = getNonEmptyUserInput("Enter your dev token: ")

evernoteHost = "sandbox.evernote.com"
userStoreUri = "https://" + evernoteHost + "/edam/user"

userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
userStore = UserStore.Client(userStoreProtocol)

noteStoreUrl = userStore.getNoteStoreUrl(authToken)

noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
noteStore = NoteStore.Client(noteStoreProtocol)

####
# The Main Event
####

# Get the most recent note from the user's account

print "Grabbing a note from your account..."
note = getSingleNote(authToken, noteStore)
if not note:
	print "Something went wrong; no note was found. Alert the authorities!"
	raise SystemExit
print "Found note:", note.title
print "Now looking for related notes..."

# Look for related notes based on the retrieved note and display them
related = getRelatedNotes(note, authToken, noteStore)
displayRelatedNotes(related)

# Ask for some text and use that to search for related notes
print "Now, let's try searching for notes related to random text."
text = getNonEmptyUserInput("Type something and we'll find notes related to it:")
trelated = getRelatedNotes(text, authToken, noteStore)
displayRelatedNotes(trelated)

print "Thanks for playing!"
