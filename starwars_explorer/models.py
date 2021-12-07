from django.db import models


class Collection(models.Model):
    filename = models.CharField(max_length=100)
    date = models.DateTimeField()
    total_count = models.IntegerField()
    

# tbd (if hosted in the cloud instead of local): 
# - change filename to process id
# - add status
# - storage of crawls with foreign key on process id also in db table