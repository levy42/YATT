## Hi there!

### use python 3.7+
### sorry for that, but you also need to do:

- pip install -r requirements.txt

- python -m spacy download en

(I was too lazy to write own text similarity algorithm)

    python main.py make-everything-ok-button test-data/sample-0-origin.html test-data/sample-1-evil-gemini.html
    
Hopefully you'll see:

```ElementProperties(title='Make-Button', xpath='/html/body/div/div/div[3]/div[1]/div/div[2]/div/a', tag='a', classes=['btn', 'test-link-ok'], href='#ok', onclick='javascript:window.okComplete(); return false;', text='\nMake everything OK\n', id=None)```