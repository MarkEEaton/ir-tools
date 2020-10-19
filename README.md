# ir-tools

This script is intended to support scholarly communications librarians by producing a spreadsheet to track publications that have been identified via google alerts. It does this by drawing data from the *unread* messages in gmail folder full of google alerts. It parses these alerts and turns them into a spreadsheet. 

It will also attempt to fetch rights for each item from the Sherpa RoMEO API. The success rate for pulling the rights is quite low, because it requires an exact match between the journal title as it appears in the google alert and as it appears in the RoMEO API, which seems to happen infrequently.

- You will have to set up a gmail API key. Instructions are here: https://developers.google.com/gmail/api/quickstart/python. You only need to do Step 1 (Turn on the Gmail API) and Step 2 (Install the Google Client Library).

- You will also have to set up a Sherpa RoMEO API key for the v2 API: https://v2.sherpa.ac.uk/api/.

Some of the code is drawn from https://developers.google.com/gmail/api/quickstart/python, and is not modified, so those sections are under an Apache License 2.0. 

Otherwise this code is released under the MIT License, copyright (c) 2019 Mark Eaton.
