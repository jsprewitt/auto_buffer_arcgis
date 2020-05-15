# auto_buffer_and_backup

Python flask app that uses the ArcGIS Online REST API to automatically buffer Survey123 and Collecor entries when called by web hook. It also now records them to a Google Sheet.

I created a flask app to run this program whenever any HTML request is sent to example.com/run.

Be sure to update your survey and buffer layers if you want to use this. You'll also need to register client_id and secret_ids for the program to be able to use the ARCGIS REST API.

If you want to use the google sheet functionality, you'll need to register with Google Sheets API. Review the gspread library on how to do that.
