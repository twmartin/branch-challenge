#!/usr/bin/env python3

"""This module can be used to build a Docker image, start up to 5 containers
using the image, and stop/remove any related containers"""

import sys
import time
import argparse
import docker
import requests


def build_image(docker_client):
    """Builds a Docker image with the tag 'branchchallenge:latest'

    Returns:
        None
    """
    docker_build = docker_client.images.build(path='.', tag='branchchallenge:latest', pull=True)
    print('Docker image built: {image_id}'.format(image_id=docker_build[0].id))


def start_containers(docker_client, container_count):
    """Starts the desired number of containers

    Returns:
        None
    """
    existing_containers = docker_client.containers.list(
        filters={'ancestor':'branchchallenge:latest'}
    )
    print('Found {running_count} running containers'.format(running_count=len(existing_containers)))
    if container_count + len(existing_containers) > 5:
        print('The count of existing plus new containers may be no greater than 5')
        sys.exit(1)

    index = 1 + len(existing_containers)
    while index <= container_count + len(existing_containers):
        print('Starting container{index}'.format(index=index))
        docker_client.containers.run(
            'branchchallenge:latest',
            ports={'9090/tcp': None},
            volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'ro'}},
            detach=True
        )
        index += 1

    time.sleep(1)
    healthcheck(docker_client)


def healthcheck(docker_client):
    """Runs a simple health check against running containers

    Returns:
        None
    """
    existing_containers = docker_client.containers.list(
        filters={'ancestor':'branchchallenge:latest'}
    )
    api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    for container in existing_containers:
        port_data = api_client.inspect_container(container.id)['NetworkSettings']['Ports']
        host_port = port_data['9090/tcp'][0]['HostPort']
        print('Container {c_id} is mapped to {host_port}'.format(
            c_id=container.id,
            host_port=host_port
        ))
        container_address = 'http://127.0.0.1:{host_port}'.format(host_port=host_port)
        healthy = False
        retry = 0
        while not healthy and retry < 3:
            try:
                request = requests.get(container_address)
                if container.id == request.json()['DockerContainerID']:
                    healthy = True
                    print('Container {c_id} is healthy'.format(c_id=container.id))
            except Exception as exception:
                print(str(exception))

            retry += 1
            time.sleep(2)



def delete_containers(docker_client):
    """Stops and removes any containers with ancestor 'branchchallenge:latest'

    Returns:
        None
    """
    all_containers = docker_client.containers.list(
        'all', filters={'ancestor':'branchchallenge:latest'}
    )
    for container in all_containers:
        if container.status == 'running':
            print('Stopping container {container_id}'.format(container_id=container.id))
            container.stop()
        print('Deleting container {container_id}'.format(container_id=container.id))
        container.remove()


def parse_args():
    """Parse command line arguments

    Returns:
        parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Audit s3 buckets for best practices'
    )

    parser.add_argument(
        'mode',
        metavar='MODE',
        type=str,
        help='Run mode: "build", "start", or "stop"'
    )

    parser.add_argument(
        '-c',
        '--count',
        type=int,
        help='Number of containers to start in "build" mode'
    )

    return parser.parse_args()


def main():
    """Runs the build, start, and delete functions based on the passed args

    Returns:
        None
    """
    args = parse_args()
    docker_client = docker.from_env()
    if args.mode == 'build':
        build_image(docker_client)
    elif args.mode == 'start':
        start_containers(docker_client, args.count)
    elif args.mode == 'delete':
        delete_containers(docker_client)
    else:
        print('Unsupported execution mode')
        sys.exit(1)


if __name__ == "__main__":
    main()
