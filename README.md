## GAFE Usernames Proxy
Uses a Service Account to fetch usernames of non-suspended accounts in
a list of organization units.


## Project Setup and Development Server Testing
To customize this project, you'll have to set up your own Google App Engine project in the
Google Developers Console.

1. Clone this repository.

2. Use the [Google Developers Console](https://console.developers.google.com) to create a
    project, with a unique app id. For purposes of this README, we use "gafe-conferences"
    as the app id. (App id and project id are identical)

3. Go to the API Manager section. On the APIs tab, add credentials for a "Service account" 
    and download the JSON credentials to "service_account.json" in the top level folder of the repository.

4. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
    See the README file for directions. You'll need python 2.7 and 
    [pip 1.4 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

5. Install dependencies in the project's lib directory.
    Note: App Engine can only import libraries from inside your project directory.
    ```
    cd <project directory>
    rm -rf lib/*
    pip install -r requirements.txt -t lib
    ```

5. Copy config-sample.py to config.py and edit according to your domain. 

6. Run the project locally from the command line:
    ```
    dev_appserver.py -A gafe-usernames --port=8188 app.yaml
    ```

Congratulations, your project should be running now!

Visit the application [http://localhost:8188](http://localhost:8188)

See [the development server documentation](https://developers.google.com/appengine/docs/python/tools/devserver)
for options when running dev_appserver.

## Deployment
To deploy the application on appspot.com:

1. In the [Google Developers Console](https://console.developers.google.com) console, add
    the appspot.com URIs for the "Authorized Javascript origins" and "Authorized redirect URIs". 


3. [Deploy the application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with:
    ```
    appcfg.py -A gafe-conferences --oauth2 update .
    ```

Congratulations! Your application is now live at gafe-conferences.appspot.com

