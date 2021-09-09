FROM freesurfer/freesurfer:7.1.1
COPY license.txt /usr/local/freesurfer/.license
COPY requirements.txt .
COPY scripts/parallel/ parallel/

ENV VIRTUAL_ENV=/root/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SUBJECTS_DIR="/root/freesurfer_wrapper/FS_OUTPUTS"
ENV QC_DIR="/root/freesurfer_wrapper/QC"

RUN yum install -y python3 make
RUN mkdir env
RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -r requirements.txt
RUN cd parallel/ && ./configure && make && make install

WORKDIR /root/freesurfer_wrapper
CMD ["/bin/bash"]