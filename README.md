# testing

Use GitPython to clone repositories from url address, makes checkouts and merges.

Use argparse to allow command-line arguments.

The necessary Python packages are in requirements.txt file.

The copy.py is a script to verify the arguments passed and define if the current travis test is a PUSH or a PR, then makes the corresponding checkouts and merges depending on the target, origin and default branches.
