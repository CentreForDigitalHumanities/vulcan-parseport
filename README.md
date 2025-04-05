# VULCAN -- ParsePort

This is a fork of the original repository of VULCAN (Visualizations for Understanding Language Corpora and model predictioNs), developed and maintained by [dr. Jonas Groschwitz (jgroschwitz)](https://github.com/jgroschwitz). Please refer to the [original repo](https://github.com/jgroschwitz/vulcan) for the original documentation, including setup and usage instructions.

This fork adapts VULCAN to be used within the ParsePort project as a visualization tool for syntactic parses made by the Minimalist Parser developed by [dr. Meaghan Fowlie (megodoonch)](https://github.com/megodoonch) at Utrecht University. More documentation on ParsePort, developed at the Centre For Digital Humanities at Utrecht University, can be found [here](https://github.com/CentreForDigitalHumanities/parseport).

This project contains the code for a web-based visualization tool, run on a Flask webserver. The server accepts both regular HTTP requests and WebSocket connections. In addition, there is a small SQLite database to keep track of individual parse results.

## Aim and functionality

The server is designed to receive parse results from the Minimalist Parser and turn them into Layout objects that can be rendered in the browser. The server is designed to be run in a Docker container, and it is part of the ParsePort container network.

## API architecture

### HTTP

The server's main HTTP endpoint is `/`. It only accepts POST requests with a JSON object of the following form.

  ```json
  {
    "id": "unique-identifier-for-parse",
    "parse_data": "base64-encoded-parse-result",
  }
  ```

The server decodes the parse result data, turns it into a Layout object and stores it in a SQLite database together with the ID and a timestamp. The server then sends a JSON response of the shape `{"ok": True}` with a status code of 200.

In addition, HTTP GET requests to the `/status/` endpoint will return `{"ok": "true"}` if the server is running and ready to receive connections.

### WebSocket

When a client connects to the server through WebSocket, it will do so at the `/socket.io/<id>` endpoint. The ID route parameter is optional.

If no ID is provided, the server will return a standard Layout object, based on a pre-parsed corpus containing sentences from the Wall Street Journal. If an ID is provided, the server will look up the corresponding Layout object in the SQLite database and send it to the client.


## Running a local development server

The server can be run in three different ways:

1. Locally, using Flask's built-in development server.
2. In a Docker container.
3. As part of the ParsePort container network, using Docker Compose.

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

3. Start the development server by running the following command in the `/app` folder:

    ```bash
    flask run --host 0.0.0.0
    ```

    This will start the server on `http://localhost:5000`. Visit `http://localhost:5000/status/` to check if the server is running.


### Running the server in a Docker container

To run the server in a stand-alone container, run the following commands in the root directory of the project:

```bash
docker build -t vulcan-parseport .
docker run -d -p 5000:5000 --name vulcan-parseport vulcan-parseport
```

This will build the Docker image and run a container with the image. The server will be available at `http://localhost:5000`. You can add `-v ./app:/app:rw` to the `docker run` command to mount the `app` directory to the container, which enables auto-reload whenever the code in `app` is changed.

### Running the server as part of the ParsePort container network

Please refer to the ParsePort documentation for instructions on how to run the server as part of the ParsePort container network.
