import click


def get_banner(mode: str, version: str):
    return "\n".join(
        [
            "\b",
            click.style("MarOps CLI", bg="green"),
            "\b",
            "Mode: "
            + click.style(mode, fg="green")
            + " - Version: "
            + click.style(version, fg="yellow"),
            "Powered by: " + click.style("Greenroom Robotics", fg="green"),
        ]
    )
