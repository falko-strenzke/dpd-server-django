from django.db import models


class Pali_Word(models.Model):
    pali_1 = models.CharField(max_length=255, unique=True, primary_key=True)
    pali_2 = models.CharField(max_length=255)
    pos = models.CharField(max_length=255)
    grammar = models.CharField(max_length=255)
    derived_from = models.CharField(max_length=255)
    verb = models.CharField(max_length=255)
    trans = models.CharField(max_length=255)
    plus_case = models.CharField(max_length=255)
    meaning_1 = models.TextField()
    meaning_2 = models.TextField()
    meaning_lit = models.TextField()
    sanskrit = models.CharField(max_length=255)
    root_key = models.CharField(max_length=255)
    root_sign = models.CharField(max_length=255)
    root_base = models.CharField(max_length=255)
    construction = models.CharField(max_length=255)
    derivative = models.CharField(max_length=255)
    suffix = models.CharField(max_length=255)
    phonetic = models.CharField(max_length=255)
    compound_type = models.CharField(max_length=255)
    compound_construction = models.CharField(max_length=255)
    non_root_in_comps = models.CharField(max_length=255)
    synonym = models.CharField(max_length=255)
    variant = models.CharField(max_length=255)
    stem = models.CharField(max_length=255)
    pattern = models.CharField(max_length=255)

    def simple_text_with_pali(self):
        return self.pali_1 + " – " + self.meaning_1


    def simple_html_with_pali(self):
        return dpd_html_rendering.make_meaning_html(self)


class Pali_Root(models.Model):
    """
    pali root information
    """
    root = models.CharField(max_length=255)
    root_in_comps = models.CharField(max_length=255)
    #root_has_verb = models.BooleanField(default=False)
    root_group = models.IntegerField()
    root_sign = models.CharField(max_length=255)
    root_meaning = models.CharField(max_length=255)
    sanskrit_root = models.CharField(max_length=255)
    sanskrit_root_meaning = models.CharField(max_length=255)
    sanskrit_root_class = models.CharField(max_length=255)
    root_example = models.TextField()
    dhatupatha_num = models.CharField(max_length=255)
    dhatupatha_root = models.CharField(max_length=255)
    dhatupatha_pali = models.CharField(max_length=255)
    dhatupatha_english = models.CharField(max_length=255)
    dhatumanjusa_num = models.CharField(max_length=255)
    dhatumanjusa_root = models.CharField(max_length=255)
    dhatumanjusa_pali = models.CharField(max_length=255)
    dhatumanjusa_english = models.CharField(max_length=255)
    dhatumala_root = models.CharField(max_length=255)
    dhatumala_pali = models.CharField(max_length=255)
    dhatumala_english = models.CharField(max_length=255)
    panini_root = models.CharField(max_length=255)
    panini_sanskrit = models.CharField(max_length=255)
    panini_english = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    matrix_test = models.CharField(max_length=255)
    root_info = models.CharField(max_length=255)
    root_matrix = models.CharField(max_length=255)


class Inflection_To_Headwords(models.Model):
    """
    For each inflected form give a comma separated list of headwords to which the form can be resolved
    """
    inflection = models.CharField(max_length=255)
    headwords = models.CharField(max_length=511)



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

    headword = models.ForeignKey(Pali_Word, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    prefix_pos = models.IntegerField()
    suffix_pos = models.IntegerField()
    is_phonetic_change = models.BooleanField(default=False)




class Construction_Element_Set(models.Model):
    """
    This table contains the set of all construction elements found in the construction of any headword. It is thus for instance suitable for providing auto completion for the search by construction.
    """
    text = models.CharField(max_length=255)



class Sandhi(models.Model):
    """
    For each inflected form give a comma separated list of known sandhi splits to which the form can be resolved
    """
    sandhi = models.CharField(max_length=255)

    """
    comma separted list of splits
    """
    split = models.TextField()


