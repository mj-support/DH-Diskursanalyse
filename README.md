# DH-Diskursanalyse

## Getting Started

### Prepare Python environment

Install the python environment as follows:

```shell
$ git clone https://github.com/mj-support/DH-Diskursanalyse.git
$ cd DH-Diskursanalyse
$ conda env create -f environment.yml
$ conda activate Diskursanalyse
```

Run the following python scripts

1. ```scraping.py```: download protocols and extract text
2. ```agenda.py```: normalize text and extract agenda
3. ```speeches.py```: extract speeches based on the agenda and filter speeches about refugees

### Topic Modelling

1. ```preprocessing.py```: preprocess the speeches
2. ?TopicModelling?

### Sentiment Analysis

It is recommend to execute the sentiment analysis on a HPC-Cluster or a device with strong GPU-power. 
Additionally you have to install the ```mistral-inference```-library and download the LLM.
More information in ```sentiment_analysis.py```

1.
   - ```sbatch sentiment_batch.sh```: if you run the sentiment analysis on a cluster
   - ```sentiment_analysis.py```: if you run the sentiment analysis locally
2. ```llm_validation.py```: validate the results with human labels 
3. ```visualisation.py```: aggregate and visualize the resultes



