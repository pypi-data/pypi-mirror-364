## Test notebooks for templates

First, install voila-nbgallery and start Voila:

```
# Install voila-nbgallery:
pip install .

# For the qgrid test notebook:
pip install qgrid pandas
jupyter nbextension enable --py --sys-prefix qgrid

# Voila should serve nbextensions instead of relying on CDN:
voila --port 8888 --VoilaConfiguration.enable_nbextensions=True ./notebooks

# Or to see the nbgallery template on the tree page:
voila --port 8888 --VoilaConfiguration.enable_nbextensions=True --template nbgallery-material ./notebooks
```

Next, **turn off your internet**, then compare the following URLs:

```
# Qgrid widget will not appear with default template
# (The browser console will have an error about base/js/dialog.js and falling back to unpkg.com.)
http://localhost:8888/voila/render/qgrid.ipynb
http://localhost:8888/voila/render/qgrid.ipynb?voila-template=offline-lab

# Font-awesome button icons will not appear with default template
# (You may need to clear your browser cache or force reload)
http://localhost:8888/voila/render/font-awesome.ipynb
http://localhost:8888/voila/render/font-awesome.ipynb?voila-template=offline-lab

# Gridstack template will not display the grid properly
http://localhost:8888/voila/render/gridstack.ipynb?voila-template=gridstack
http://localhost:8888/voila/render/gridstack.ipynb?voila-template=offline-gridstack

# Gridstack + font-awesome + qgrid
http://localhost:8888/voila/render/gridstack-plus.ipynb?voila-template=gridstack
http://localhost:8888/voila/render/gridstack-plus.ipynb?voila-template=offline-gridstack

# nbgallery template
http://localhost:8888/voila/render/nbgallery-metadata.ipynb?voila-template=nbgallery-material
```
