FROM continuumio/miniconda3
COPY . .

RUN conda env create -n customerpp --file ./environment.yml
RUN conda init bash
# Override default shell to use bash
SHELL ["/bin/bash", "--login", "-c"]
RUN conda activate customerpp > ~/.bashrc
RUN conda list
EXPOSE 5000
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "customerpp", "python", "api.py"]
