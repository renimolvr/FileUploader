from collections import Counter

from django.db.models import Max
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import MonolingualCorpus, CleanedMonolingualCorpus, UploadedFileIndex
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .helper import process_csv, process_text

def home(request):
    return render(request, 'home.html')

def user_signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('upload_csv') 
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def upload_csv(request):
    starting_id = None
    ending_id = None
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_type = file.name.split('.')[-1].lower()
        
        existing_upload = UploadedFileIndex.objects.filter(uploaded_file_name=file.name).first()
        if existing_upload:
            MonolingualCorpus.objects.filter(id__range=(existing_upload.starting_id, existing_upload.ending_id)).delete()
            UploadedFileIndex.objects.filter(uploaded_file_name=file.name).delete()
     
        if file_type == 'csv':
            starting_id = (MonolingualCorpus.objects.aggregate(Max('id'))['id__max'] or 0) + 1
            process_csv(file, request.user)
            ending_id = (MonolingualCorpus.objects.aggregate(Max('id'))['id__max'] or 0)
            uploaded_file_index = UploadedFileIndex.objects.create(uploaded_file_name = file.name, 
                                                                   starting_id = starting_id, 
                                                                   ending_id = ending_id)
            
        elif file_type == 'txt':
            starting_id = (MonolingualCorpus.objects.aggregate(Max('id'))['id__max'] or 0) + 1
            process_text(file, request.user)
            ending_id = (MonolingualCorpus.objects.aggregate(Max('id'))['id__max'] or 0)
            uploaded_file_index = UploadedFileIndex.objects.create(uploaded_file_name = file.name, 
                                                                   starting_id = starting_id,
                                                                   ending_id = ending_id)
            
        else:
            print("Unsupported file type")
            
        return render(request, 'success.html', {'uploaded_file_info': uploaded_file_index})

    return render(request, 'upload.html')


def retrieve_corpus(request):
    if request.method == 'POST':
        corpus_id = request.POST.get('corpus_id')

        try:
            corpus = MonolingualCorpus.objects.get(pk=corpus_id)
            context = {
                'corpus': corpus,
            }
            return render(request, 'corpus_details.html', context)
        except (MonolingualCorpus.DoesNotExist, CleanedMonolingualCorpus.DoesNotExist):
            error_message = "Corpus with the provided ID does not exist."
            return print(error_message)
    return render(request, 'retrieve_corpus.html')

def word_frequency_table(request, uploaded_file_id):
    cleaned_corpus = CleanedMonolingualCorpus.objects.filter(uploaded_file_index_id=uploaded_file_id)
    words = []
    for corpus in cleaned_corpus:
        words.extend(corpus.cleaned_content.split())

    word_freq = Counter(words)

    context = {
        'word_freq': word_freq.items(),
    }
    return render(request, 'word_frequency_table.html', context)