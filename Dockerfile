FROM freesurfer/freesurfer:7.1.1
COPY license.txt /usr/local/freesurfer/.license

RUN yum install -y python3
RUN mkdir env
ENV VIRTUAL_ENV=/root/env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install pandas
ENV SUBJECTS_DIR="/root/freesurfer_wrapper/FS_OUTPUTS"

WORKDIR /root/freesurfer_wrapper
CMD ["/bin/bash"]