# roamingmantis

A collection of scripts to make a surface analysis of Roaming Mantis related malware families.

## Requirements

- Python 3.8+
- Poetry

## Install

```bash
git clone https://github.com/ninoseki/roamingmantis
cd roamingmantis
poetry install
```

## FakeSpy

- Features:
  - Extract a hidden dex.
  - Extract C2 destinations.
  - Send a command to C2.

```bash
$ fakespy --help
Usage: fakespy [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  analyze-apk
  send-command
```

```bash
moqhao analyze-apk /path/to/apk
```

You can send the following commands.

- GetMessage
- [GetMessage2](https://github.com/ninoseki/fakespy/wiki#getmessage2)(`sendSms`)
- [GetMoreMessage](https://github.com/ninoseki/fakespy/wiki#getmoremessage)(`sendAll`)
- [GetMoreConMessge](https://github.com/ninoseki/fakespy/wiki#getmoreconmessage)(`sendCon`)


```bash
moqhao send-command GetMessage2 foo.bar.com
```


### MoqHao

- Features:
  - Extract a hidden dex.
  - Extract C2 destinations.
  - Extract URLs of phishing websites.

```bash
$ moqhao --help
Usage: moqhao [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  analyze-apk
```

```bash
moqhao analyze-apk /path/to/apk
```
