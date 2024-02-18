from django.db import models

# Create your models here.


class Headword(models.Model):
    """
    Table for headwords
    """

    headword = models.CharField(max_length=255, unique=True, primary_key=True)
    desc_html = models.TextField()

    """
    construction without phonetic change information
    """
    construction_text = models.TextField(default="")


class Construction_Element(models.Model):
    """
    A construction Element related to a single headword featuring information of the position in the
    construction and the type of element.  prefix_pos is counted from 1 starting from the first
    prefix  until the root. suffix_pos likewise is counted backwards starting from 1 at the last
    suffix until the root. If the word contains no root, both these counters run until the opposite
    end.
    prefix_pos and suffix_pos carry the value -1 at positions where they are not counted (i.e.,
    following the root in their respective counting direction)
    """

    headword = models.ForeignKey(Headword, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    prefix_pos = models.IntegerField()
    suffix_pos = models.IntegerField()
    is_phonetic_change = models.BooleanField(default=False)


class Inflected_Form(models.Model):
    """
    Table for inflected form
    """

    inflected_form = models.CharField(max_length=255)
    link_text = models.CharField(max_length=255)


class Deconstruction(models.Model):
    """
    Table for deconstructor dict of DPD
    """

    headword = models.CharField(max_length=255, unique=True, primary_key=True)
    desc_html = models.CharField(max_length=255)


class Grammar(models.Model):
    """
    Table for grammar dict of DPD
    """

    headword = models.CharField(max_length=255, unique=True, primary_key=True)
    desc_html = models.CharField(max_length=255)


class Construction_Element_Set(models.Model):
    """
    This table contains the set of all construction elements found in the construction of any headword. It is thus for instance suitable for providing auto completion for the search by construction.
    """
    text = models.CharField(max_length=255)
