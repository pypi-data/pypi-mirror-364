import os
from typing import List, Optional, cast
import json

import click
import subprocess
from python_on_whales.docker_client import DockerClient
from python_on_whales.components.compose.models import ComposeConfig
from python_on_whales.utils import ValidPath
from python_on_whales.exceptions import NoSuchImage

import marops_config
from marops_config import MarOpsConfig

from marops_cli.helpers import (
    docker_compose_path,
    get_project_root,
    call,
    get_marops_version,
)

PYTHON_PACKAGES = [
    "marops-config",
    "marops-cli"
]

SERVICES = [
    "marops_ui",
    "marops_core",
    "marops_docs",
    "marops_hasura",
    "marops_chart_tiler",
    "marops_chart_api",
    "marops_rsync",
    "postgres",
    "plugins",
    "studio",
    "traefik"
]

def marops_config_read():
    config = marops_config.read()
    version = get_marops_version()

    if version != "latest" and not config.prod:
        click.echo(click.style(f"Setting config.prod to True.", fg="red"))
        click.echo(click.style(f"You cannot run MarOps in developer mode when using the production vesion of marops-cli", fg="red"))
        config.prod = True

    return config


def _get_compose_files(config: MarOpsConfig) -> List[ValidPath]:
    compose_files: List[ValidPath] = [
        docker_compose_path("./docker-compose.base.yaml")
    ]
    if config.prod:
        compose_files.append(docker_compose_path("./docker-compose.prod.yaml"))
    else:
        compose_files.append(docker_compose_path("./docker-compose.dev.yaml"))
    
    if config.proxy:
        compose_files.append(docker_compose_path("./docker-compose.demo.yaml"))

    return compose_files


def _log_config(config: MarOpsConfig):
    click.echo(click.style("[+] MarOps Config:", fg="green"))
    for attr, value in config.__dict__.items():
        click.echo(
            click.style(f" ⠿ {attr}: ".ljust(26), fg="white") + click.style(str(value), fg="green")
        )

def _set_config_to_env(config: MarOpsConfig):
    os.environ["MAROPS_VERSION"] = get_marops_version()
    os.environ["MAROPS_DATA_PATH"] = config.data_path
    os.environ["MAROPS_BACKUP_PATH"] = config.backup_path
    os.environ["SECURE_COOKIE"] = "true" if config.secure_cookie else "false"
    os.environ["HASURA_GRAPHQL_ADMIN_SECRET"] = config.hasura_admin_secret
    os.environ["COMPOSE_PROJECT_NAME"] = "marops"

    # key must be at least 32 characters long
    os.environ["HASURA_GRAPHQL_JWT_SECRET"] = json.dumps({
        "type":"HS256",
        "key": f"{config.hasura_admin_secret.zfill(32)}-:^)",
        "header":{"type": "Cookie", "name": "token" }
    })
    os.environ["PROXY_HOST"] = config.proxy_host

    return os.environ


@click.command(name="build")
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def build(services: List[str]):
    """Builds MarOps"""
    config = marops_config_read()
    _set_config_to_env(config)

    docker_dev = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    services_list = list(services) if services else None
    docker_dev.compose.build(cache=True, services=services_list)


@click.command(name="up")
@click.option(
    "--build",
    help="Should we do a docker build",
    is_flag=True,
)
@click.option(
    "--pull",
    help="Should we do a docker pull",
    is_flag=True,
)
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def up(build: bool, pull: bool, services: List[str]):
    """Starts MarOps"""
    config = marops_config_read()
    _log_config(config)
    _set_config_to_env(config)

    docker = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    services_list = list(services) if services else None
    docker.compose.up(detach=True, build=build, services=services_list, pull="always" if pull else "missing")
   
@click.command(name="restart")
@click.argument(
    "services",
    required=False,
    nargs=-1,
    type=click.Choice(SERVICES),
)
def restart(services: List[str]):
    """Starts MarOps"""
    config = marops_config_read()
    _log_config(config)
    _set_config_to_env(config)

    docker = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    services_list = list(services) if services else None
    docker.compose.restart(services=services_list)
   


@click.command(name="down")
@click.argument("args", nargs=-1)
def down(args: List[str]):
    """Stops MarOps"""
    config = marops_config_read()
    _log_config(config)
    _set_config_to_env(config)

    docker = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    docker.compose.down()


@click.command(name="upgrade")
@click.option("--version", help="The version to upgrade to.")
def upgrade(version: str):
    """Upgrade MarOps CLI"""
    click.echo(f"Current version: {get_marops_version()}")
    result = click.prompt(
        "Are you sure you want to upgrade?", default="y", type=click.Choice(["y", "n"])
    )
    if result == "n":
        return

    if version:
        click.echo(click.style("Upgrading marops-config...", fg="blue"))
        call(f"pip install --upgrade marops-config=={version}")
        click.echo(click.style("Upgrading marops-cli...", fg="blue"))
        call(f"pip install --upgrade marops-cli=={version}")
    else:
        click.echo(click.style("Upgrading marops-config...", fg="blue"))
        call("pip install --upgrade marops-config")
        click.echo(click.style("Upgrading marops-cli...", fg="blue"))
        call("pip install --upgrade marops-cli")

    click.echo(click.style("Upgrade of MarOps CLI complete.", fg="green"))
    click.echo(
        click.style(
            "Run `marops up` to upgrade MarOps.", fg="green"
        )
    )


@click.command(name="authenticate")
@click.option(
    "--username",
    help="The username to use for authentication.",
    required=True,
    prompt=True,
)
@click.option("--token", help="The token to use for authentication.", required=True, prompt=True)
def authenticate(username: str, token: str):
    """
    Authenticate with the MarOps package repository so that you can pull images.

    To get a username and token you'll need to contact a Greenroom Robotics employee.
    """
    call(f"echo {token} | docker login ghcr.io -u {username} --password-stdin")


@click.command(name="configure")
@click.option("--default", is_flag=True, help="Use default values")
def configure(default: bool):  # type: ignore
    """Configure MarOps"""

    if default:
        config = MarOpsConfig()
        marops_config.write(config)
    else:
        # Check if the file exists
        if os.path.exists(marops_config.get_path()):
            click.echo(
                click.style(
                    f"MarOps config already exists: {marops_config.get_path()}",
                    fg="yellow",
                )
            )
            result = click.prompt(
                "Do you want to overwrite it?", default="y", type=click.Choice(["y", "n"])
            )
            if result == "n":
                return

        try:
            config_current = marops_config_read()
        except Exception:
            config_current = MarOpsConfig()

        config = MarOpsConfig(
            prod=click.prompt(
                "Prod Mode",
                default=config_current.prod,
                type=bool,
            ),
            data_path=click.prompt(
                "Data Path", default=config_current.data_path
            ),
            backup_path=click.prompt(
                "Backup Path", default=config_current.backup_path
            ),
            hasura_admin_secret=click.prompt(
                "Hasura Admin Secret", default=config_current.hasura_admin_secret
            ),
            secure_cookie=click.prompt(
                "Secure Cookie", default=config_current.secure_cookie, type=bool,
            ),
            proxy=click.prompt(
                "Proxy Mode", default=config_current.proxy, type=bool,
            ),
            proxy_host=click.prompt(
                "Proxy Host", default=config_current.proxy_host,
            ),
        )
        marops_config.write(config)



@click.command(name="config")
def config():  # type: ignore
    """Read Config"""
    config = marops_config_read()
    _log_config(config)
    _set_config_to_env(config)
    click.echo(click.style(f"path: {marops_config.get_path()}", fg="blue"))

@click.command(name="env")
@click.argument("args", nargs=-1)
def env(args: List[str]):  # type: ignore
    """Source env and run a command"""
    config = marops_config_read()
    _log_config(config)
    _set_config_to_env(config)
    subprocess.run(args, shell=True, check=True)

@click.command(name="download")
@click.option(
    "--include-deps",
    help="Should we include the deps",
    is_flag=True,
    default=False,
    
)
@click.argument(
    "output-directory",
    required=False,
    nargs=1,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
)
def download(include_deps: bool, output_directory: Optional[ValidPath]):
    """ Saves off the marops docker images to a tar file and optionally downloads the deps
    """
    marops_version = get_marops_version()
    if marops_version == "latest":
        raise click.ClickException(
            "You must install a pinned version of marops-cli to use this command.")
        
    _set_config_to_env(marops_config_read())
    
        
    docker_client = DockerClient(
        compose_files=_get_compose_files(marops_config_read()),
    )
    
    docker_config = cast(ComposeConfig, docker_client.compose.config())
    docker_services = docker_config.services or {}
    docker_images = [docker_services[service].image for service in docker_services.keys()]
    docker_images = [image for image in docker_images if image]
    
        
    if not output_directory:
        output_directory = os.getcwd()

    if include_deps:
        # Download the deps
        click.echo(click.style(f"Downloading deps", fg="green"))

        # Download debians for the docker install
        os.makedirs(f"{output_directory}/debs", exist_ok=True)

        # Get all the dependencies for docker and save to a folder
        # This gross thing parses the output from apt-rdepends so ALL the dependencies are downloaded
        subprocess.call(
            "apt-rdepends \
            docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
            | awk '/^[^ ]/ {print $1}' \
            | sort -u \
            | xargs apt download",
            shell=True,
            cwd=f"{output_directory}/debs"
        )
        click.echo(click.style(f"Debians saved to {output_directory}/debs", fg="green"))
        
        # Download the python deps
        click.echo(click.style(f"Downloading python deps", fg="green"))

        python_folder = "marops_packages"
        os.makedirs(f"{output_directory}/{python_folder}", exist_ok=True)
        if marops_version == "latest":
            python_packages = PYTHON_PACKAGES
        else:
            python_packages = [f"{package}=={marops_version}" for package in PYTHON_PACKAGES]
        subprocess.call(
            f"pip download --dest={output_directory}/{python_folder}/ " + ' '.join(python_packages),
            shell=True
        )
    else:
        click.echo(click.style(f"Skipping deps download", fg="yellow"))
    
    click.echo(click.style(f"Found images from docker compose: {docker_images}.", fg="green"))

    docker_download_dir = os.path.join(output_directory, "docker_images")
    # Create the directory if it doesn't exist
    os.makedirs(docker_download_dir, exist_ok=True)

    try:
        click.echo(click.style(f"Downloading images to {docker_download_dir}. This takes a while...", fg="green"))
        docker_client.save(docker_images, output=os.path.join(output_directory, "docker_images", "docker_images.tar"))
    except NoSuchImage as e:
        click.echo(click.style(f"Image not found: {e}", fg="white"))
        click.echo(click.style(f"At least one image wasn't found locally. Run `marops install` to download the images.", fg="red"))
        return

    # Save the images to a tar file
    click.echo(click.style(f"Images saved to {output_directory}/docker_images.tar", fg="green"))


@click.command(name="install")
@click.option(
    "--image-path",
    help="The path to the image tar file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
)
def install(image_path: Optional[ValidPath]):
    """Install MarOps"""
    config = marops_config_read()
    _set_config_to_env(config)
    docker = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    if image_path:
        click.echo(click.style(f"Loading images from {image_path}", fg="green"))
        docker.image.load(image_path)
    else:
        # Get the required containers from the docker-compose file
        docker_config = cast(ComposeConfig, docker.compose.config())
        docker_services = docker_config.services or {}
        try:
            docker.compose.pull(docker_services)
        except Exception:
            click.echo(
                click.style(
                    "Failed to pull MarOps files. Have you ran `marops authenticate` ?",
                    fg="yellow",
                )
            )


@click.command(name="install")
@click.option(
    "--image-path",
    help="The path to the image tar file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
)
def install(image_path: Optional[ValidPath]):
    """Install MarOps"""
    config = marops_config_read()
    _set_config_to_env(config)
    docker = DockerClient(
        compose_files=_get_compose_files(config),
        compose_project_directory=get_project_root(),
    )
    if image_path:
        click.echo(click.style(f"Loading images from {image_path}", fg="green"))
        docker.image.load(image_path)
    else:
        # Get the required containers from the docker-compose file
        docker_config = cast(ComposeConfig, docker.compose.config())
        docker_services = docker_config.services or {}
        try:
            docker.compose.pull(docker_services)
        except Exception:
            click.echo(
                click.style(
                    "Failed to pull MarOps files. Have you ran `marops authenticate` ?",
                    fg="yellow",
                )
            )