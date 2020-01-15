FROM python:3.6.9-stretch

# ---------------------------------------------------------------------------------------------------------------------
# Install Java
RUN apt-get update && apt-get install openjdk-8-jdk -y && apt-get clean

# ---------------------------------------------------------------------------------------------------------------------
# Install Cytomine python client
RUN git clone https://github.com/cytomine-uliege/Cytomine-python-client.git && \
    cd /Cytomine-python-client && git checkout tags/v2.3.0.poc.1 && pip install . && \
    rm -r /Cytomine-python-client

# ---------------------------------------------------------------------------------------------------------------------
# Install Neubias-W5-Utilities (annotation exporter, compute metrics, helpers,...)
RUN apt-get update && apt-get install libgeos-dev -y && apt-get clean
RUN git clone https://github.com/Neubias-WG5/neubiaswg5-utilities.git && \
    cd /neubiaswg5-utilities/ && git checkout tags/v0.7.0 && pip install .

# install utilities binaries
RUN chmod +x /neubiaswg5-utilities/bin/*
RUN cp /neubiaswg5-utilities/bin/* /usr/bin/

# cleaning
RUN rm -r /neubiaswg5-utilities

# ---------------------------------------------------------------------------------------------------------------------
# Install FIJI
# Install virtual X server
RUN apt-get update && apt-get install -y unzip xvfb libx11-dev libxtst-dev libxrender-dev

# Install Fiji.
RUN wget --no-check-certificate 'https://www.dropbox.com/s/b5jq7d87f0ubolr/Fiji.app_Trackmate_5_2_0.zip?dl=1'
RUN unzip Fiji.app_Trackmate_5_2_0.zip
RUN mv Fiji.app/ fiji

# create a sym-link with the name jars/ij.jar that is pointing to the current version jars/ij-1.nm.jar
RUN cd /fiji/jars && ln -s $(ls ij-1.*.jar) ij.jar

# Add fiji to the PATH
ENV PATH $PATH:/fiji

RUN mkdir -p /fiji/data

# Clean up
RUN rm fiji-linux64-20170530.zip

# ---------------------------------------------------------------------------------------------------------------------
# ImageJ plugin
# install FeatureJ
RUN cd /fiji/plugins && \
    wget -O imagescience.jar \
    https://imagescience.org/meijering/software/download/imagescience.jar

RUN cd /fiji/plugins && \
    wget -O FeatureJ_.jar \
    https://imagescience.org/meijering/software/download/FeatureJ_.jar
	
# ---------------------------------------------------------------------------------------------------------------------
# add the local files
ADD Trackmate_script.py /fiji/macros/Trackmate_script.py
ADD wrapper.py /app/wrapper.py

# set the entrypoint
ENTRYPOINT ["python", "/app/wrapper.py"]
