import base64
import rich_click as click
import yaml
from rich.console import Console
from rich.syntax import Syntax

console = Console()
click.rich_click.USE_RICH_MARKUP = True


@click.group()
def cli():
    """Kubernetes Secrets Base64 Encoder/Decoder CLI"""
    pass


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file to save the decoded YAML (defaults to overwrite input file)",
)
def decode(yaml_file, output):
    with open(yaml_file, "r") as f:
        secret = yaml.safe_load(f)

    if not secret or "data" not in secret:
        console.print("[bold red]No 'data' field found in the YAML file.[/bold red]")
        raise click.Abort()

    for key, b64val in secret["data"].items():
        try:
            decoded_bytes = base64.b64decode(b64val)
            decoded_str = decoded_bytes.decode("utf-8")
            secret["data"][key] = decoded_str
        except Exception as e:
            console.print(f"[bold red]Failed to decode {key}: {e}[/bold red]")
            secret["data"][key] = "<decoding error>"

    out_path = output if output else yaml_file
    with open(out_path, "w") as f:
        yaml.dump(secret, f, sort_keys=False)
    console.print(f"[bold green]Decoded YAML saved to[/bold green] {out_path}")


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file to save the encoded YAML (defaults to overwrite input file)",
)
def encode(yaml_file, output):
    with open(yaml_file, "r") as f:
        secret = yaml.safe_load(f)

    if not secret or "data" not in secret:
        console.print("[bold red]No 'data' field found in the YAML file.[/bold red]")
        raise click.Abort()

    for key, val in secret["data"].items():
        try:
            encoded_bytes = base64.b64encode(val.encode("utf-8"))
            encoded_str = encoded_bytes.decode("utf-8")
            secret["data"][key] = encoded_str
        except Exception as e:
            console.print(f"[bold red]Failed to encode {key}: {e}[/bold red]")
            secret["data"][key] = "<encoding error>"

    out_path = output if output else yaml_file
    with open(out_path, "w") as f:
        yaml.dump(secret, f, sort_keys=False)
    console.print(f"[bold green]Encoded YAML saved to[/bold green] {out_path}")


def load_env_file(env_file_path):
    """Load a simple .env file into a dict."""
    env_vars = {}
    with open(env_file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            env_vars[key.strip()] = val.strip()
    return env_vars


@cli.command()
@click.option("--name", required=True, help="Secret name")
@click.option("--namespace", required=True, help="Secret namespace")
@click.option(
    "--env-file", type=click.Path(exists=True), required=True, help="Path to .env file"
)
@click.option(
    "-o", "--output", type=click.Path(), help="Output YAML file (default: secret.yaml)"
)
def generate(name, namespace, env_file, output):
    """
    Generate a Kubernetes Secret YAML from a .env file,
    encoding the values in base64.
    """
    env_vars = load_env_file(env_file)
    if not env_vars:
        console.print("[bold red]No valid env vars found in the env file.[/bold red]")
        raise click.Abort()

    data_encoded = {}
    for key, val in env_vars.items():
        encoded = base64.b64encode(val.encode("utf-8")).decode("utf-8")
        data_encoded[key] = encoded

    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "data": data_encoded,
        "type": "Opaque",
    }

    out_path = output or "secret.yaml"
    with open(out_path, "w") as f:
        yaml.dump(secret, f, sort_keys=False)

    console.print(
        f"[bold green]Secret YAML generated and saved to[/bold green] {out_path}"
    )


def parse_k8s_yaml(file_path):
    """Parse a single YAML file and return kind, name, and data keys."""
    with open(file_path, "r") as f:
        doc = yaml.safe_load(f)

    if (
        not doc
        or "kind" not in doc
        or "metadata" not in doc
        or "name" not in doc["metadata"]
    ):
        raise ValueError(f"Invalid or missing kind/metadata/name in {file_path}")

    kind = doc["kind"]
    name = doc["metadata"]["name"]
    data = doc.get("data", {})

    if not isinstance(data, dict):
        raise ValueError(f"'data' field must be a dict in {file_path}")

    return kind, name, data


def generate_env_from_yaml_files(file_paths):
    """
    Given a list of secret/configmap YAML files,
    generate env entries splitting keys between secrets and configmaps.
    """
    secret_keys_map = {}  # key -> secret name
    configmap_keys_map = {}  # key -> configmap name

    for file_path in file_paths:
        try:
            kind, name, data = parse_k8s_yaml(file_path)
        except Exception as e:
            console.print(f"[bold red]Error parsing {file_path}: {e}[/bold red]")
            raise click.Abort()

        if kind == "Secret":
            for key in data.keys():
                secret_keys_map[key] = name
        elif kind == "ConfigMap":
            for key in data.keys():
                configmap_keys_map[key] = name
        else:
            # Ignore other kinds
            pass

    # Combine all keys
    all_keys = set(secret_keys_map.keys()) | set(configmap_keys_map.keys())

    env_list = []
    for key in sorted(all_keys):
        if key in secret_keys_map:
            env_list.append(
                {
                    "name": key,
                    "valueFrom": {
                        "secretKeyRef": {
                            "name": secret_keys_map[key],
                            "key": key,
                        }
                    },
                }
            )
        else:
            env_list.append(
                {
                    "name": key,
                    "valueFrom": {
                        "configMapKeyRef": {
                            "name": configmap_keys_map[key],
                            "key": key,
                        }
                    },
                }
            )
    return env_list


@cli.command()
@click.option(
    "--files",
    "-f",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="One or more Kubernetes Secret or ConfigMap YAML files",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file to save the env entries YAML snippet",
)
def generate_env_from_yamls(files, output):
    """
    Generate Kubernetes Deployment env: entries from provided Secret and ConfigMap YAML files.

    Automatically detects keys and references based on YAML contents.
    """
    try:
        env_entries = generate_env_from_yaml_files(files)
    except click.Abort:
        return

    yaml_snippet = yaml.dump(env_entries, sort_keys=False)

    if output:
        with open(output, "w") as f:
            f.write(yaml_snippet)
        console.print(f"[bold green]Env references saved to[/bold green] {output}")
    else:
        syntax = Syntax(yaml_snippet, "yaml", theme="monokai", line_numbers=False)
        console.print(syntax)


if __name__ == "__main__":
    cli()
