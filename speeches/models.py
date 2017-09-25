from django.db import models
from .behaviors.models import Timestampable, Taggable, Versionable
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class PopoloDateTimeField(models.DateTimeField):
    """Converting datetime to popolo."""
    def get_popolo_value(self, value):
        return str(datetime.strftime(value, '%Y-%m-%d'))


class Person(Timestampable, models.Model):
    """Model for all people that are somehow connected to the parlament."""

    name = models.CharField(_('name'),
                            max_length=128,
                            help_text=_('A person\'s preferred full name'))

    name_parser = models.CharField(max_length=500,
                                   help_text='Name for parser.',
                                   blank=True, null=True)

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      help_text='Classification for sorting purposes.',
                                      blank=True,
                                      null=True)

    family_name = models.CharField(_('family name'),
                                   max_length=128,
                                   blank=True, null=True,
                                   help_text=_('One or more family names'))

    given_name = models.CharField(_('given name'),
                                  max_length=128,
                                  blank=True, null=True,
                                  help_text=_('One or more primary given names'))

    additional_name = models.CharField(_('additional name'),
                                       max_length=128,
                                       blank=True, null=True,
                                       help_text=_('One or more secondary given names'))

    honorific_prefix = models.CharField(_('honorific prefix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics preceding a person\'s name'))

    honorific_suffix = models.CharField(_('honorific suffix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics following a person\'s name'))

    patronymic_name = models.CharField(_('patronymic name'),
                                       max_length=128,
                                       blank=True, null=True,
                                       help_text=_('One or more patronymic names'))

    sort_name = models.CharField(_('sort name'),
                                 max_length=128,
                                 blank=True, null=True,
                                 help_text=_('A name to use in an lexicographically ordered list'))

    previous_occupation = models.TextField(_('previous occupation'),
                                           blank=True, null=True,
                                           help_text=_('The person\'s previous occupation'))

    education = models.TextField(_('education'),
                                 blank=True, null=True,
                                 help_text=_('The person\'s education'))

    education_level = models.TextField(_('education level'),
                                       blank=True, null=True,
                                       help_text=_('The person\'s education level'))

    mandates = models.IntegerField(_('mandates'),
                                   blank=True, null=True,
                                   help_text=_('Person\'s number of mandates, including the current one'))

    email = models.EmailField(_('email'),
                              blank=True, null=True,
                              help_text=_('A preferred email address'))

    gender = models.CharField(_('gender'),
                              max_length=128,
                              blank=True, null=True,
                              help_text=_('A gender'))

    birth_date = PopoloDateTimeField(_('date of birth'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of birth'))

    death_date = PopoloDateTimeField(_('date of death'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of death'))

    summary = models.CharField(_('summary'),
                               max_length=512,
                               blank=True, null=True,
                               help_text=_('A one-line account of a person\'s life'))

    biography = models.TextField(_('biography'),
                                 blank=True, null=True,
                                 help_text=_('An extended account of a person\'s life'))

    image = models.URLField(_('image'),
                            blank=True, null=True,
                            help_text=_('A URL of a head shot'))

    gov_url = models.ForeignKey('Link',
                                blank=True, null=True,
                                help_text='URL to gov website profile',
                                related_name='gov_link')

    gov_id = models.CharField(_('gov_id'),
                              max_length=255,
                              blank=True, null=True,
                              help_text='gov website id for the scraper')

    gov_picture_url = models.URLField(_('gov image url'),
                                      blank=True, null=True,
                                      help_text=_('URL to gov website pic'))

    voters = models.IntegerField(_('voters'),
                                 blank=True,
                                 null=True,
                                 help_text='number of votes cast for this person in their district')

    active = models.BooleanField(_('active'),
                                 default=True,
                                 help_text='a generic active or not toggle')

    image = models.ImageField(upload_to='images/', height_field=None, width_field=None, max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name + " " + str(self.id)


class Organization(Timestampable, models.Model):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """

    name = models.TextField(_('name'),
                             help_text=_('A primary name, e.g. a legally recognized name'))

    name_parser = models.CharField(max_length=500,
                                   help_text='Name for parser.',
                                   blank=True, null=True)

    # array of items referencing "http://popoloproject.com/schemas/other_name.json#"
    acronym = models.CharField(_('acronym'),
                                blank=True,
                                null=True,
                                max_length=128,
                                help_text=_('Organization acronym'))

    gov_id = models.TextField(_('Gov website ID'),
                              blank=True, null=True,
                              help_text=_('Gov website ID'))

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      blank=True, null=True,
                                      help_text=('An organization category, e.g. committee'))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey('Organization',
                               blank=True, null=True,
                               related_name='children',
                               help_text=_('The organization that contains this organization'))

    dissolution_date = PopoloDateTimeField(blank=True, null=True,
                                           help_text=_('A date of dissolution'))

    founding_date = PopoloDateTimeField(blank=True, null=True,
                                        help_text=_('A date of founding'))

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    description = models.TextField(blank=True, null=True,
                                   help_text='Organization description')

    is_coalition = models.IntegerField(blank=True, null=True,
                                       help_text='1 if coalition, -1 if not, 0 if it does not apply')

    url_name = 'organization-detail'

    def __str__(self):
        return self.name + " " + str(self.id)


class Speech(Versionable, Timestampable, models.Model):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey('Person',
                                help_text='Person making the speech')

    party = models.ForeignKey('Organization',
                              help_text='The party of the person making the speech',
                              null=True,
                              blank=True)

    content = models.TextField(help_text='Words spoken')

    video_id = models.TextField(help_text='Video id', blank=True, null=True)

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                help_text='Speech session',
                                related_name='speeches')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    start_time_stamp = models.BigIntegerField(blank=True, null=True,
                               				  help_text='Start time stamp')

    end_time_stamp = models.BigIntegerField(blank=True, null=True,
                                			help_text='End time stamp')


    def __str__(self):
        return self.speaker.name + " " + str(self.id)


class Session(Timestampable, models.Model):
    """Sessions that happened in parliament."""

    mandate = models.ForeignKey('Mandate',
                                blank=True, null=True,
                                help_text='The mandate of this milestone.')

    name = models.CharField(max_length=255,
                            blank=True, null=True,
                            help_text='Session name')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Gov website ID.')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='session',
                                     help_text='The organization in session')

    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    in_review = models.BooleanField(default=False,
                                    help_text='Is session in review?')

    def __str__(self):
        return self.name + ",  " + self.organization.name


class Link(Timestampable, models.Model):
    """
    A URL
    # max_length increased to account for lengthy Camera's URLS
    """

    url = models.URLField(_('url'),
                          max_length=350,
                          help_text=_('A URL'))

    note = models.CharField(_('note'),
                            max_length=256,
                            blank=True, null=True,
                            help_text=_('A note, e.g. \'Wikipedia page\''),)

    name = models.TextField(blank=True, null=True)

    date = models.DateField(blank=True, null=True)

    session = models.ForeignKey('Session', blank=True, null=True)

    organization = models.ForeignKey('Organization',
                                     blank=True,
                                     null=True,
                                     help_text='The organization of this link.',
                                     related_name='links')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person of this link.')

    def __str__(self):
        return self.url


class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True,
                                   null=True)

    def __str__(self):
        return self.description