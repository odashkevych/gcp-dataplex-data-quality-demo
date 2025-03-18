
## DQ Python compiler

### Python virtual environment

Create virtual env

```shell
python3.9 -m venv .migration-venv
```

To activate the virtual environment, you'll need to source the activate script located in the bin directory within the
environment. The exact command differs based on your operating system:

On Linux/macOS:

```shell
source .venv/bin/activate
```

On Windows (Command Prompt):

```shell
.venv\Scripts\activate.bat
```

On Windows (PowerShell):

```shell
.\.venv\Scripts\Activate.ps1
```

### Install pip packages

```shell
pip3 install -r requirements.txt
```

### DQ Tests

Compile 

```shell
python compile_rule.py event.yaml event-compiled.yaml
```


# DQ Tests

DQ dimensions https://www.datagaps.com/blog/what-are-data-quality-dimensions/

Compile generic tests and deploy to DQ bucket.

Events
```shell
python compile_rule.py models/event.yaml compiled dev
./copy_rules.sh compiled/models
```

Sales
```shell

```
