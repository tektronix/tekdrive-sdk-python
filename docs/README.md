## Documentation
The documentation is built using Sphinx. Assuming you have Python 3.8 and [pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)
installed, run the following:

```shell
pipenv install --dev
```

#### Running the Development Server
You can run a local development server to preview changes using the following:

```shell
pipenv run serve
```

#### Running Manually
You can build the docs manually by running:
```shell
pipenv run make html
```
