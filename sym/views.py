from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from pathlib import Path
import pandas as pd
from symspellpy import SymSpell, Verbosity

# Create your views here.
def index(request):    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect("lookup")
    else:
        form = UploadFileForm()
    return render(request,'sym/index.html', {'form': form,})

def handle_uploaded_file(f):
    with open('name.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


MAX_EDIT_DISTANCE = 2
DICTIONARY_PATH = Path('kk.txt')

symspell = SymSpell(max_dictionary_edit_distance=MAX_EDIT_DISTANCE)
symspell.load_dictionary(DICTIONARY_PATH, term_index=0, count_index=1, encoding='utf-8')

def lookup(request):
    df = pd.read_json('name.json')
    data = {"message": [], 
            "language": [],
            "corrected": [],
            "correct": [],}
    for row in df.values:
        msg = str(row[3]['text'])
        if row[3]['type'] == 'message' and msg != '':
            data["message"].append(msg)
            data["language"].append("Kazakh")
            correct_msg = ""
            txt = msg.split()
            for word in txt:
                correct_word = lookup_word(word, Verbosity.TOP, MAX_EDIT_DISTANCE)
                if correct_word != None:
                    correct_msg = correct_msg + " " + correct_word
                else:
                    correct_msg = correct_msg + " " + word
            data["corrected"].append(correct_msg)
            if msg == correct_msg.strip():
                data['correct'].append("True")
            else:
                data['correct'].append("False")
    print(len(data['message']))
    data = zip(data['message'], data['language'], data['corrected'], data['correct'])
    return render(request, 'sym/lookup.html', {'data': data})

def lookup_word(word, verbosity, max_edit_distance):
    suggestions = symspell.lookup(word, verbosity, max_edit_distance)
    words_list = [item.term for item in suggestions]

    if verbosity == Verbosity.CLOSEST:
        return words_list

    if len(words_list) > 0:
        return words_list[0]

    return None