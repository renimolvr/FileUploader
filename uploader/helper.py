import re
import pandas as pd

from django.db import transaction
from django.utils import timezone

from .models import MonolingualCorpus, CleanedMonolingualCorpus, UploadedFileInfo

def process_csv(file: str, user, lang: str = 'ml', chunk_size: int = 1000) -> None:
    uploaded_file_info = UploadedFileInfo.objects.create(user = user, 
                                        uploaded_file_name = file.name, 
                                        last_updated = timezone.now())
    monolingual_corpus_list = []
    reader = pd.read_csv(file, chunksize=chunk_size)

    for chunk in reader:
        for index, row in chunk.iterrows():
            content = ','.join(map(str, row.tolist()))
            monolingual_corpus_list.append(
                MonolingualCorpus(
                    username = user.username,
                    uploaded_file_index = uploaded_file_info,
                    language = lang,
                    content = content.strip(),
                    last_updated = timezone.now()
                )
            )

    with transaction.atomic():
        MonolingualCorpus.objects.bulk_create(monolingual_corpus_list)

    saved_monolingual_corpus = MonolingualCorpus.objects.filter(
        uploaded_file_index = uploaded_file_info,
        username = user.username
    )

    cleaned_monolingual_corpus_list = []
    for corpus in saved_monolingual_corpus:
        cleaned_content = clean_malayalam_text(corpus.content)
        if cleaned_content.strip():
            cleaned_monolingual_corpus_list.append(
                CleanedMonolingualCorpus(
                    username=user.username,
                    uploaded_file_index = uploaded_file_info,
                    cleaned_content=cleaned_content,
                    last_updated=timezone.now()
                )
            )

    with transaction.atomic():
        CleanedMonolingualCorpus.objects.bulk_create(cleaned_monolingual_corpus_list)

def process_text(file, user, lang: str = 'ml') -> None:
    uploaded_file_info = UploadedFileInfo.objects.create(user = user, 
                                        uploaded_file_name = file.name, 
                                        last_updated = timezone.now())
    content = file.read().decode('utf-8')
    lines = content.split('\n')
    monolingual_corpus_list = []
    cleaned_monolingual_corpus_list = []

    for line in lines:
        monolingual_corpus_list.append(
            MonolingualCorpus(
                username=user.username,
                uploaded_file_index = uploaded_file_info,
                language=lang,
                content=content.strip(),
                last_updated=timezone.now()
            )
        )
        
    with transaction.atomic():
        MonolingualCorpus.objects.bulk_create(monolingual_corpus_list)
        
    saved_monolingual_corpus = MonolingualCorpus.objects.filter(
        uploaded_file_index = uploaded_file_info,
        username=user.username
    )
    
    cleaned_monolingual_corpus_list = []
    for corpus in saved_monolingual_corpus:
        cleaned_content = clean_malayalam_text(corpus.content)
        if cleaned_content.strip():
            cleaned_monolingual_corpus_list.append(
                CleanedMonolingualCorpus(
                    username=user.username,
                    uploaded_file_index = uploaded_file_info,
                    cleaned_content=cleaned_content,
                    last_updated=timezone.now()
                )
            )

    with transaction.atomic():
        CleanedMonolingualCorpus.objects.bulk_create(cleaned_monolingual_corpus_list)

def clean_malayalam_text(text):
    cleaned_text = re.sub(r'[^\u0D00-\u0D7F\s]','', text)  
    return cleaned_text.strip()

