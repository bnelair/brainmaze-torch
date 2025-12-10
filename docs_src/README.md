# Documentation Source

This directory contains the source files for the BrainMaze-Torch documentation.

## Building Documentation Locally

To build the documentation locally:

```bash
# Install dependencies
pip install -r docs_src/requirements.txt
pip install -e .

# Build HTML documentation
sphinx-build -b html docs_src/source docs

# Or use the convenience script
./make_docs.sh
```

The built documentation will be in the `docs/` directory.

## Deployment

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch. The deployment is handled by the `.github/workflows/docs.yml` workflow.

**Note:** The `docs/` directory is excluded from version control (via `.gitignore`) and should not be committed to the repository.

## Configuration

- `source/conf.py` - Sphinx configuration file
- `source/*.rst` - Documentation source files
- `requirements.txt` - Python dependencies for building documentation

## Theme

The documentation uses the Sphinx Book Theme with custom branding (logo and favicon) from the `img/` directory.
