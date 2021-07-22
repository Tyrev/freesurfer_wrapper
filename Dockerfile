FROM freesurfer/freesurfer:7.1.1
COPY license.txt /usr/local/freesurfer/.license
COPY requirements.txt .

ENV VIRTUAL_ENV=/root/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SUBJECTS_DIR="/root/freesurfer_wrapper/FS_OUTPUTS"
ENV QC_DIR="/root/freesurfer_wrapper/QC"

RUN yum install -y python3
RUN mkdir env
RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -r requirements.txt

WORKDIR /root/freesurfer_wrapper
CMD ["/bin/bash"]