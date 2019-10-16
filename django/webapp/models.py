from django.db import models


class Synagogue(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Member(models.Model):
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)
    first_name = models.TextField()
    last_name = models.TextField()
    can_get_aliya = models.BooleanField()
    aliya_name = models.TextField(blank=True)
    refuah_name = models.TextField()
    is_cohen = models.BooleanField()
    is_levi = models.BooleanField()
    date_of_birth = models.DateField(blank=True)
    born_after_shkiah = models.BooleanField()

    @property
    def full_name(self):
        return ' '.join(name for name in (self.first_name, self.last_name)
                        if name)

    def yichus(self):
        if self.is_cohen:
            return 'Cohen'
        elif self.is_levi:
            return 'Levi'
        else:
            return 'Yisrael'

    def __str__(self):
        return self.full_name
