# Wedding Website Application

We've decided to build our own
wedding website for fun!

### Getting started

**Create Virtual Environment**

Create a virtual environment and install the
necessary packages. In your repository a
directory `wedding` will be created with a the nencessary
things needed for this project.

```
python -m venv wedding
wedding\Scripts\activate.bat
pip install -r requirements.in
```

On Mac replace `wedding\Scripts\activate.bat` with `source wedding/bin/activate`

**Pre-commit Hooks**

Pre-commit hooks are used to lint code, check for possible
errors and enforce a style guide on a project.
To get pre-commit hooks working run `pre-commit install` in your terminal.

When you run any `git commit -m "my message"` the commit hook  script will
run before you commit is completed. If you have errors (likely you will) you
need to fix your scripts before committing again.
