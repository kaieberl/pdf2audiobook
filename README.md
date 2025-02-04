# pdf2audiobook

**Update 17.09.2023:**  
Meta has released [Nougat](https://github.com/facebookresearch/nougat), an academic document PDF parser that supports LaTeX math and tables.
I have created a [new implementation](https://github.com/kaieberl/paper2speech) that uses Nougat instead of the Google Vision API and Vertex AI.

This repository is based on the pdf2audiobook project by Kaz Sato from Google.
It is updated to work with Google Vertex AI and includes some improvements and additional features.

Since the original documentations by [Kaz Sato](https://github.com/kazunori279/pdf2audiobook) and [Dale Markowitz](https://daleonai.com/pdf-to-audiobook) leave out some important steps that especially beginners to Google Cloud require, I decided to write a more in-depth documentation.

First, open `functions/app/main.py` in your IDE.
Google Cloud functions do not have a `main()` entry point, but a trigger function, in this case `p2a_gcs_trigger()`, which is invoked when the user uploads a new file to a specified Google Cloud bucket.
I recommend the following Medium article about [Google Cloud functions](https://medium.com/google-cloud/setup-and-invoke-cloud-functions-using-python-e801a8633096).

This script is invoked 3 times for a job.  
- First, with the user-provided pdf.
It is passed to the Vision API for text element extraction.
- The second time, when the document vision is finished extracting the text elements. 
The Vision API returns a json file, which is then passed to Vertex AI for labelling.
- The third time is when Vertex AI has finished labelling the text elements as body, header etc. Vertex AI returns csv files.
In this step, the ssml is generated from the text and synthesized as speech.

Why?  
The inference jobs might take a considerable amount of time to run.
This way, the cloud function does not need to wait and check if the files have been created already.

Make yourself familiar with the menu structure of Google Cloud.
At the top, there are some pinned items that you can customize.
Further down, you can find a Serverless section that contains Cloud Functions, and further down the Storage section with Cloud Storage and, way down, the Artificial Intelligence section with Vertex AI.
You might want to pin those entries.

## Annotation
1. Create a new bucket in Cloud Storage
2. Deploy the cloud function with trigger  
To do this, navigate to the Cloud Functions menu item and create a Python 3.8 function.
There, you create a `main.py` file and a `requirements.txt` file and paste the code.
To deploy, you can either use the graphical interface, or use the cloud console command:  
`gcloud functions deploy p2a_gcs_trigger --runtime python38 --trigger-bucket <bucket> --memory=2048MB --timeout=540`  
where `<bucket>` is the name of the bucket that you want to use for the trigger.
3. Upload a pdf file to the bucket that you want to label

After a minute or so, a csv file will appear in the bucket.
Download it and run my provided annotation tool `labeler_google.py`.
The script is made such that the text of the paragraph will be printed in green, and you have to press the corresponding key for the label.
You don't need to press enter. However, this functionality will only work in a console (e.g. the Mac system terminal or iTerm), but will give an error when run e.g. in PyCharm.
If you can't make it work, replace the line `label = getch()` by `line = input()` and remove `import termios`, `import tty` and the `getch()` function.

_Keep in mind that any existing csv with the same name will be overwritten, so change the csv name for every annotation._

Next, check e.g. in the PyCharm csv data view that all labels are filled and delete the other ones.

## Training process
You can read more about Vertex AI in this [documentation](https://codelabs.developers.google.com/vertex-p2p-predictions).
Create a new dataset in Vertex AI, consisting of your csv files.
Then, create a new AutoML model and start training.

**Note:**  
AutoML has a few requirements:
- You need to have at least 1000 _valid_ items in your dataset (lines in csv). You can also upload multiple csv files with a total of more than 1000 entries.
An item is invalid if an attribute is missing.
- Check the validity of your labels. `\r` symbols and `None` labels will give an error. For this purpose, you can use my `dataset_checker.py` script.

In any case, you will get an e-mail notification when training is finished, or an error message and why it has occurred.

## Usage
You don't need to deploy your model. Just copy the model id from the Vertex AI model overview and paste it into the `model_id` variable.
Set `ANNOTATION` to `False` and deploy the cloud function again.

You can get a list of your models with the command `gcloud ai models list`.

To convert a pdf, just drop it into the bucket.
You can also customize the voice and language in the `voice_map` variable.
```python3
voice_map = {
    'en': ('en-US', 'en-US-Neural2-J'),
    'de': ('de-DE', 'de-DE-Neural2-B'),
    'ja': ('ja-JP', 'ja-JP-Neural2-C')
}
```
Go to [https://cloud.google.com/text-to-speech](https://cloud.google.com/text-to-speech) to try out different voices and languages. Below the text box, there is a button to show the json request.
E.g. to add a Spanish voice, add 
```python3
'es': ('es-ES', 'es-ES-Standard-A'),
```
To use a British english voice, replace `'en': ('en-US', 'en-US-Neural2-J'),` by `'en': ('en-GB', 'en-GB-Neural2-B'),`.

## Testing Google Cloud functions
Since I couldn't get the arguments for the eventarc trigger to work (there seems to be not that much documentation on this topic), I used the following workaround to test the 3rd step (merge csv prediction files and generate speech)

```python3
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PROJECT_DIR, "<your_key_file>.json")


def p2a_debug(*args):
    p2a_gcs_trigger({"name": "prediction-ocr-model-2023_09_08T14_06_50_281Z/prediction.results-00019-of-00020.csv", "bucket": "BUCKET"}, None)
```
Change the file name and bucket name accordingly, depending on which part of the trigger function you want to test.
Place your key file in the same folder as `main.py` and name it `pdf2audiobook.json`.
Your bucket name is the display name that you entered for your bucket, e.g. `p2a-bucket`.
E.g. upload the previously generated prediction result files from step 2, and pass the name of the _last_ prediction file (e.g. `prediction.results-00019-of-00020.csv`).
Configure your IDE to run `--source=functions/app/main.py --target="p2a_debug" --signature-type=http --port=8080 --debug`.
This starts a web server on your local machine, port 8080.
You can simulate a file upload eventarc trigger event by running the provided `test.sh` script in a terminal.

## A note on costs
(may change)
- Cloud Storage: 0.026 USD per GB per month
- Cloud Functions: first 2 million invocations per month free, after that 0.40 USD per 1 million invocations
- Vertex AI: 0.10 USD per node hour (1 node = 1.8 GHz Intel Xeon v2 (Sandy Bridge) processor, 3.75 GB RAM)
- Cloud Vision: first 1000 units per month free, then 1.50 USD per 1000 units
- Cloud TTS: first 1 million characters free, then 4.00 USD per 1 million characters

So the only thing that might get expensive is the Vertex AI training.
For me, this was included in the 90-day trial, but else this would have cost me 20 USD (1h, upgraded node).

## Future work
- hold out figure descriptions until the current paragraph is finished
- include previous and successive element in labelling feature set
