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

def getSingleNote(authToken, noteStore):
	"""
	Retrieve the newest note from the user's account
	"""
	noteFilter = NoteStore.NoteFilter()
	noteFilter.ascending = True
	notes = noteStore.findNotes(authToken, noteFilter, 0, 1)
	if notes.totalNotes:
		return notes.notes.pop()
	return None

def getRelatedNotes(parameter, authToken, noteStore):
	"""
	Get related notes from Evernote Cloud API based on supplied note.
	"""
	query = NoteStore.RelatedQuery()
	if hasattr(parameter,'guid'):
		# this is a Note 
		print "you passed a Note object"
		query.noteGuid = parameter.guid
	else:
		# this is probably plain text
		query.plainText = parameter

	resultSpec = NoteStore.RelatedResultSpec()
	resultSpec.maxNotes = 3
	try:
		related = noteStore.findRelated(authToken, query, resultSpec)
		return (related if related.notes else None)
	except Exception, e:
		print "Exception:", e
		return None
		
def getAuthToken():
	"""
	Get dev token from user.
	"""
	token = raw_input("Enter your dev token: ")
	if token:
		return token
	print "Dev token can't be empty."
	return getAuthToken()

def getPlainText():
	"""
	Ask the user for some text to use as a seed for a related note search
	"""
	plaintext = raw_input("Type something and we'll find notes related to it:")	
	if plaintext:
		return plaintext
	print "You need to type something."
	return getPlainText()

def displayRelatedNotes(related):
	if related:
		print "Found the following related notes:"
		for note in related.notes:
			print note.title
	else:
		print "No related notes found."

authToken = "" # bypass the dev token prompt by populating this variable.

if not authToken:
	authToken = getAuthToken()

evernoteHost = "sandbox.evernote.com"
userStoreUri = "https://" + evernoteHost + "/edam/user"

userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
userStore = UserStore.Client(userStoreProtocol)

noteStoreUrl = userStore.getNoteStoreUrl(authToken)

noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
noteStore = NoteStore.Client(noteStoreProtocol)

# notebook = getNonEmptyNotebook(noteStore, authToken)

# if not notebook:
# 	print "Couldn't find a non-empty notebook. Add some notes."
# 	raise SystemExit

print "Grabbing a note from your account..."

note = getSingleNote(authToken, noteStore)

if not note:
	print "Something went wrong; no note was found. Alert the authorities!"
	raise SystemExit

print "Found note:", note.title

print "Now looking for related notes..."

related = getRelatedNotes(note, authToken, noteStore)

displayRelatedNotes(related)

print "Now, let's try searching for notes related to random text."

text = getPlainText()

trelated = getRelatedNotes(text, authToken, noteStore)

displayRelatedNotes(trelated)

print "Thanks for playing!"
