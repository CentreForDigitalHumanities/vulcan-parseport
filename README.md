# VULCAN -- ParsePort

[![DOI](https://zenodo.org/badge/881050880.svg)](https://doi.org/10.5281/zenodo.17974273)

This is a fork of the original repository of VULCAN (Visualizations for Understanding Language Corpora and model predictioNs), developed and maintained by [dr. Jonas Groschwitz (jgroschwitz)](https://github.com/jgroschwitz). Please refer to the [original repo](https://github.com/jgroschwitz/vulcan) for the original documentation, including setup and usage instructions. More information about VULCAN can be found in the original paper: [Introducing VULCAN: A Visualization Tool for Understanding Our Models and Data by Example (Groschwitz, BlackboxNLP 2023)](https://aclanthology.org/2023.blackboxnlp-1.15/).

This fork adapts VULCAN to be used within the ParsePort project as a visualization tool for syntactic parses made by the Minimalist Parser developed by [dr. Meaghan Fowlie (megodoonch)](https://github.com/megodoonch) at Utrecht University. More documentation on ParsePort, developed at the Centre For Digital Humanities at Utrecht University, can be found [here](https://github.com/CentreForDigitalHumanities/parseport).

This project contains the code for a web-based visualization tool, run on a Flask webserver. The server accepts both regular HTTP requests and WebSocket connections. In addition, there is a small SQLite database to keep track of individual parse results.

## Aim and functionality

The server is designed to receive parse results from the Minimalist Parser and turn them into so-called 'Layout' objects that can be sent to a client. In the browser, these Layouts are used to build navigable trees representing the parse result in the shape of syntactic tree structures. 

The server is designed to be run in a Docker container but can also be run locally for development purposes, see below for instructions.

The client-side files for Vulcan are also available in this repository (in `/vulcan/client`) for reference purposes only. They are not served by the Flask server. In the context of the ParsePort project, these files are served by the NGINX server that is part of the ParsePort container network.

## API architecture

### HTTP

The server's main HTTP endpoint is `/`, which is used to register new parse results and create new Layout objects. It only accepts POST requests with a JSON object of the following form.

  ```json
  {
    "id": "unique-identifier-for-parse",
    "parse_data": "base64-encoded-parse-result",
  }
  ```

The server decodes the parse result data, turns it into a Layout object and stores it in a SQLite database together with the ID and a timestamp. The server then sends a JSON response of the shape `{"ok": True}` with a status code of 200.

In addition, HTTP GET requests to the `/status/` endpoint will return `{"ok": "true"}` if the server is running and ready to receive connections.

### WebSocket

As soon as a user downloads and opens the Vulcan client-side HTML + JS in their browser, the client will establish a WebSocket connection with the server. All communications go through the `/socket.io/<id>` endpoint, with an optional ID route parameter used to identify Layouts in the SQLite database. If an ID is provided, the server will look up the corresponding Layout and send it back to the client. If no ID is provided, the server will instead return a standard Layout object, based on a pre-parsed corpus containing sentences from the Wall Street Journal. 

The server handles the following WebSocket events:

- `connect`: tells the server to establish a connection. The server will return a stored Layout (if an ID is provided) or the standard Layout to the client, where it can be rendered on screen.
- `disconnect`: tells the server to close the connection.
- `instance_requested`: provides a page number, or index, to the server. The server will return a Layout object based on the sentence at that index in the pre-parsed corpus.
- `perform_search`: provides search parameters. The server then uses these parameters to perform a search on the standard Layout. The resulting new Layout object is stored in the database alongside a unique identifier, which is sent back to the client. The client uses the identifier to construct a new URL where it can find the search result. This URL can be shared with other users, who will then see the same search result.
- `clear_search`: retrieves the base Layout for the current Layout. This is used to clear the search results and return the standard Layout.

## Layout cleanup

Layouts that are stored in the database will be marked for cleanup if they have not been consulted for 90 days, as measured by the timestamp associated with the Layout in the database. Whenever Layout is requested, its timestamp is updated to the current time.

It is recommended to periodically clean up the database by running `remove_old_layouts.py`. This script will remove all Layouts that have been marked for cleanup. It is recommended to run this script periodically. The file `Crontab` can be used to schedule this script to run automatically on Linux-based machines that host the ParsePort Docker network.

## Running a local development server

The server can be run in three different ways:

1. Locally, using Flask's built-in development server.
2. In a standalone Docker container.
3. As part of the ParsePort container network, using Docker Compose. Refer to the [ParsePort documentation](https://github.com/CentreForDigitalHumanities/parseport) for more information.

NB: if you run the server within the ParsePort network, the application files in `/vulcan/client` are not used. Instead, the ParsePort backend application serves its own version of these files.

To run the server locally, you need to have Python 3.12 or higher installed (lower versions may work but have not been tested).

### Running the server locally

1. Recommended: set up a virtual environment. You can do this by running the following commands in the root directory of the project:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    On Windows, you can use the following commands:

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    This will create a virtual environment in the `venv` directory and activate it. You can deactivate the virtual environment by running `deactivate`.

2. Install the required dependencies. You can do this by running the following command:

    ```bash
    pip install -r requirements.txt
    ```

3. Generate a secret key and set it as the value of the VULCAN_SECRET_KEY environment variable. How this is done differs per operating system.

    On Linux-based systems:
    ```bash
    export VULCAN_SECRET_KEY='<your-secret-key-here>'
    ```

    In PowerShell on Windows:
    ```powershell
    $Env:VULCAN_SECRET_KEY='<your-secret-key-here>'
    ```


4. Start the development server by running the following command in the `/app` folder:

    ```bash
    flask run --host 0.0.0.0
    ```

    This will start the server on `http://localhost:5000`. Visit `http://localhost:5000/status/` to check if the server is running.


### Running the server in a Docker container

The server can be run in a Docker container in two ways, either as a standalone container or as part of the ParsePort container network. This requires Docker to be installed on your machine. 

#### Running Vulcan-ParsePort in a standalone Docker container

The project expects an `.env` file in the root directory of the project. This file should contain at least the following line. (Consult `.env.example` for an example.)

```properties
VULCAN_SECRET_KEY='your-secret-key-here'
```

Optionally, you may add:

```properties
# Starts the server in debug mode.
FLASK_DEBUG=1

# Specifies the port on which the application will run (default is 32771).
VULCAN_PORT=your-port-here
```

Then, build and run your container using the following commands:

```bash
docker build -t vulcan-parseport .
docker run -d -p 5000:32771 --env-file .env --name vulcan-parseport vulcan-parseport
```

If you specified a different port in the `.env` file, replace `32771` with that port number.

**Tip:** Add `-d` to run the container in detached mode and keep your terminal clean.

**Tip:** If you are running the Flask server in debug mode (with live reloading), adding `-v .:/app:rw` to the `docker run` command in Step 6 will mount the current directory to the container. Upon making changes to the code, the server will automatically reload.

The server should now be running and reachable on `http://localhost:5000`.

#### Running Vulcan-ParsePort within the ParsePort container network

No `.env` file is needed in this case, as the ParsePort container network will provide the necessary environment variables. Please consult the [ParsePort documentation](https://github.com/CentreForDigitalHumanities/parseport) for more information.


## Changes

In addition to changes specified in individual files, the following changes have been made in this fork with regard to the original VULCAN repository:
- Deleted `launch_vulcan.py`, `debugging_main.py`, `setup.py`, `visualize_amr_corpus.py`
- Moved files in `vulcan/` to `app/vulcan/`.
- Added the following files (in addition to generic housekeeping files such as `.gitignore` and `README.md`):
  - `Dockerfile`
  - `app/services/`
  - `db/models.py`
  - `Crontab`
  - `remove_old_layouts.py`
  - `logger.py`
  - `app.py`
