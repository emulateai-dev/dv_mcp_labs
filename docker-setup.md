# Docker Setup for Damn Vulnerable MCP

This document provides instructions for building and running the Damn Vulnerable Model Context Protocol (DVMCP) project using Docker.

## Overview

The Docker container includes all 10 MCP challenge servers running simultaneously in a single container, managed by supervisord. Each challenge server listens on its own port (9001-9010).

## Prerequisites

- Docker installed on your system
- Basic knowledge of Docker commands

## Files

The Docker setup consists of three main files:

1. **Dockerfile**: Defines the container image, including the base image, dependencies, and configuration.
2. **supervisord.conf**: Configures supervisord to manage all 10 MCP challenge servers.
3. **startup.sh**: Initializes the environment for all challenges before starting the servers.

## Building the Docker Image

To build the Docker image:

```bash
docker build -t dvmcp .
```

This command builds a Docker image named "dvmcp" using the Dockerfile in the current directory.

## Running the Container

To run the container:

```bash
docker run -p 8001-8010:8001-8010 dvmcp
```

This command:
- Starts a container from the "dvmcp" image
- Maps ports 8001-8010 from the container to the same ports on your host machine
- Runs all 10 MCP challenge servers simultaneously

## Accessing the Challenges

Once the container is running, you can access each challenge using an MCP client (e.g., Claude Desktop or MCP Inspector):

- Challenge 1 (Basic Prompt Injection): http://localhost:9001
- Challenge 2 (Tool Poisoning): http://localhost:9002
- Challenge 3 (Excessive Permission Scope): http://localhost:9003
- Challenge 4 (Rug Pull Attack): http://localhost:9004
- Challenge 5 (Tool Shadowing): http://localhost:9005
- Challenge 6 (Indirect Prompt Injection): http://localhost:9006
- Challenge 7 (Token Theft): http://localhost:9007
- Challenge 8 (Malicious Code Execution): http://localhost:9008
- Challenge 9 (Remote Access Control): http://localhost:9009
- Challenge 10 (Multi-Vector Attack): http://localhost:9010

## Viewing Logs

To view the logs for a specific challenge:

```bash
docker exec -it <container_id> cat /var/log/supervisor/challenge1.log
```

Replace `<container_id>` with the actual container ID and `challenge1.log` with the log file for the challenge you want to view.

## Stopping the Container

To stop the running container:

```bash
docker stop <container_id>
```

Replace `<container_id>` with the actual container ID.

## Troubleshooting

If you encounter issues:

1. **Port conflicts**: Ensure ports 9001-9010 are not already in use on your host machine.
2. **Container not starting**: Check the Docker logs with `docker logs <container_id>`.
3. **Challenges not accessible**: Verify that the container is running with `docker ps` and that the ports are correctly mapped.

## Advanced Usage

### Running in Detached Mode

To run the container in the background:

```bash
docker run -d -p 9001-9010:9001-9010 dvmcp
```

### Custom Port Mapping

If you need to use different ports on your host machine:

```bash
docker run -p 9001:8001 -p 9002:8002 -p 9003:8003 -p 9004:8004 -p 9005:8005 -p 9006:8006 -p 9007:8007 -p 9008:8008 -p 9009:8009 -p 9010:8010 dvmcp
```

This maps the container ports to ports 9001-9010 on your host machine.
