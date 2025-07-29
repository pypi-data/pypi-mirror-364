# StackGen Distribution

Logic/manifest for assembling the StackGen Distributable package(s)

## Artifacts

- `stackgen` Docker image for containerized deployment
- `stackgen-v*.zip` for docker compose based installation available for download in [latest release](https://github.com/appcd-dev/appcd-dist/releases/latest).
- `stackgen.tar.gz` local installation package (?)

## StackGen

```sh
# Start the services
make dev

```

### Compose

Checkout [sample.env](./sample.env) for a sample env file which contains necessary environment variables for appcd to work with source code management softwares.

```sh
## Update the image to latest
docker compose pull

## Up the services
docker compose up

## Folders of interest
# tmp/data/iac : This is where the appStack specific IAC files are stored
# tmp/data/.appcd/appstacks: All appStack json files are saved here.
# tmp/data/.appcd/appstacks/topology: All topology files are saved here.
```

## Enabling Auth

```sh

#.env entry
GOOGLE_CLIENT_ID=**********
GOOGLE_CLIENT_SECRET=**********


docker compose -f ./compose-auth.yaml --env-file .env up
```

## Release

```sh
sh scripts/tag-components.sh --release
sh scripts/changelog.sh >  dist-changelog.md
```

- [ ] TODO: update release notes on gh, for now manually update the release with the notes from `dist-changelog.md`

## Running in different modes

### Cloud

Checkout [compose.cloud.yaml](./compose.cloud.yaml) that contains the necessary configuration for running StackGen in cloud mode.