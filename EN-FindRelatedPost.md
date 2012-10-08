# A brief overview of the new findRelated API

Recently at the 2012 [Evernote Trunk Conference](http://blog.evernote.com/tag/evernote-trunk-conference/), we announced a new API available to third-party developers and partners, `NoteStore.findRelated`. As the name implies, this function allows the client to request notes, notebooks and tags that are related to the supplied data (either a specific Note or a block of plain text). 

We believe that giving users context for their memories and personal information provides a richer Evernote experience. This API function simplifies the search for and retrieval of such context. Let's quickly look over this function in practice.

Over on [Github](http://github.com/evernote), you'll find [an example Python application](https://github.com/evernote/python-findrelated-example) that uses `findRelated`. The code in this post will be boosted directly from the example application, so feel free to follow along and get your hands dirty.

Assuming you've already authenticated with the Evernote Cloud API and have a note you'd like to use as the basis for your request, this is what a basic implementation might look like:

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

Aside from our auth token (either a dev token used during testing or an auth token acquired using OAuth), we need to create and populate two objects that we'll pass as parameters to `findRelated`: `Related Query` and `RelatedResultSpec`.

### RelatedQuery

This class allows us to enumerate the thing (a single note or block of text) for which we'd like to see related items. In the above snippet, we've defined an intentionally-vague `parameter` argument which could be either a Note object or a block of text. When we define our `RelatedQuery`, we'll use either the GUID of our "base note" (assuming `parameter` is a Note) and assign it to the `noteGuid` member of `RelatedQuery` or, if `parameter` is something other than a Note, we'll use it to populate the `plainText` field of our `RelatedQuery`.

It's important to note that we must choose either `plainText` or `noteGuid`; we can't use both, nor can we use neither. 

*(For more information on `RelatedQuery`, see [the API reference](http://dev.evernote.com/documentation/reference/NoteStore.html#Struct_RelatedQuery)).*

### RelatedResultSpec

`RelatedResultSpec` gives us control over the types and number of results returned by the Evernote Cloud API when we call `findRelated`. We can populate one or more of the following members:

* `maxNotes`
* `maxNotebooks`
* `maxTags`

It works how you think it would; if we give a number for `maxNotes`, we'll get that number of notes (or fewer). Same with notebooks and tags. The only caveat is if you don't provide a value for one or more of these, no results of that type will be returned. 

In our example, we only define `maxNotes`. This means that our `RelatedResult` (the type returned by `findRelated`) will not contain any notebooks or tags.

*(For more information on `RelatedResultSpec`, see [the API reference](http://dev.evernote.com/documentation/reference/NoteStore.html#Struct_RelatedResultSpec)).*

### Potential Uses

This API can be useful in a variety of contexts. At Evernote, `findRelated` is used in many of our Web clippers to show the user notes from their account that are potentially to the web page they're viewing. 

If you're building an app specializing in meeting notes, `findRelated` could be useful in quickly showing meeting notes with similar content to the current document. Use cases like this are suited quite nicely to `findRelated` and, in many cases, it can increase the utility of your application with relatively little effort.

### Conclusion

It's smooth sailing from here. Assuming nothing blew up, you'll have a `RelatedResult` object populated with—in our case—up to three related notes. These are `Note` objects, so you can query them for their name, GUID, metadata, all that stuff.

The function definition for `findRelated` can be found in [our API reference documentation](http://dev.evernote.com/documentation/reference/NoteStore.html#Fn_NoteStore_findRelated).

For more information about our API or to learn how to develop software that works with Evernote, visit our [developer site](http://dev.evernote.com) or say hello to [@evernote_dev](https://twitter.com/evernote_dev) on Twitter.

