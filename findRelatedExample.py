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

def getNonEmptyNotebook(noteStore, authToken):
	"""
	Iterate over user's account until it finds a notebook with at least one note in it.
	If found, returns that notebook. Returns None otherwise.
	"""
	notebooks = noteStore.listNotebooks(authToken)
	c = len(notebooks)
	print "Found %d %s" % (c, ("notebook" if c == 1 else "notebooks"))

	for notebook in notebooks:
		filter = NoteStore.NoteFilter()
		filter.notebookGuid = notebook.guid
		counts = noteStore.findNoteCounts(authToken, filter, False)
		ncount = counts.notebookCounts[notebook.guid]
		if ncount:
			print "Found notes in %s" % notebook.name
			return notebook
	return None 

def getSingleNoteFromNotebook(notebook, authToken):
	"""
	Get a single note from notebook and return it. Return None if no note is found.
	"""
	filter = NoteStore.NoteFilter()
	filter.notebookGuid = notebook.guid
	notes = noteStore.findNotes(authToken, filter, 0, 10)
	if notes.totalNotes:
		return notes.notes.pop()
	return None

def getRelatedNotes(note, authToken, noteStore):
	"""
	Get related notes from Evernote Cloud API based on supplied note.
	"""
	query = NoteStore.RelatedQuery()
	query.noteGuid = note.guid
	resultSpec = NoteStore.RelatedResultSpec()
	resultSpec.maxNotes = 3
	try:
		related = noteStore.findRelated(authToken, query, resultSpec)
		return related
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

notebook = getNonEmptyNotebook(noteStore, authToken)

if not notebook:
	print "Couldn't find a non-empty notebook. Add some notes."
	raise SystemExit

note = getSingleNoteFromNotebook(notebook, authToken)

if not note:
	print "Something went wrong; no note was found. Alert the authorities!"
	raise SystemExit

related = getRelatedNotes(note, authToken, noteStore)

if related:
	print "Found these related notes:"
	for rnote in related.notes:
		print note.title
else:
	print "No related notes found."

print "Thanks for playing!"
