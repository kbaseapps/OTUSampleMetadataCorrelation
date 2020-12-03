FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN echo 'disrupt caching here'

RUN apt-get update && apt-get install -y vim

# R installations
RUN apt-key adv --keyserver keys.gnupg.net --recv-key 'E19F5F87128899B192B1A2C2AD5F960A256A04AF' && \
echo "deb http://cloud.r-project.org/bin/linux/debian stretch-cran35/" >> /etc/apt/sources.list && \
apt-get update
RUN apt-get install r-base r-base-dev -y
RUN R -e "install.packages(c('ggplot2', 'cowplot', 'knitr', 'rmarkdown'))"
RUN cd /opt && \
curl --location https://github.com/jgm/pandoc/releases/download/2.10.1/pandoc-2.10.1-1-amd64.deb > pandoc.deb && \
dpkg -i pandoc.deb
RUN R -e "install.packages('BiocManager')"
RUN R -e "BiocManager::install('phyloseq')"

# R phyloseq
RUN conda install -c conda-forge -y libiconv
ENV LD_LIBRARY_PATH=/miniconda/lib
RUN R -e "BiocManager::install('phyloseq')" 

# TODO
# We recommend you use --use-feature=2020-resolver to test your packages with the new resolver before it becomes the default.
RUN pip install --upgrade pip
RUN pip install dotmap numpy==1.15.4 pandas

RUN apt-get install -y libcurl4-openssl-dev libssl-dev
RUN R -e "install.packages(c('curl','openssl','httr','plotly'))"

ENV PYTHONUNBUFFERED=1

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
