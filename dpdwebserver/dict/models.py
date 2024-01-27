from django.db import models

# Create your models here.


class Headword(models.Model):
    """
    Table for headwords
    """
    headword = models.CharField(max_length=255, unique=True, primary_key=True)
    desc_html = models.TextField()


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
