from django.contrib import admin
from .models import MonolingualCorpus, ParallelCorpus, CleanedMonolingualCorpus, CleanedParallelCorpus, UploadedFileIndex, UploadedFileInfo

admin.site.register(MonolingualCorpus)
admin.site.register(ParallelCorpus)
admin.site.register(CleanedMonolingualCorpus)
admin.site.register(CleanedParallelCorpus)
admin.site.register(UploadedFileIndex)
admin.site.register(UploadedFileInfo)

