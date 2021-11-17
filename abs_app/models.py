from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
import secrets, requests, json
from django.db.models.signals import post_save


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    is_admin = models.BooleanField(default=False)
    is_qa = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)

    REQUIRED_FIELDS = []


class Application(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    teams_url = models.CharField(max_length=1500)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    token = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.token = secrets.token_hex(16)
        return super(Application, self).save()


class Version(models.Model):
    title = models.CharField(max_length=150)
    build_name = models.CharField(max_length=200, blank=True, null=True, unique=True)
    version = models.CharField(max_length=200, unique=True)
    build_notes = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(max_length=200, blank=True, null=True)
    application_token = models.ForeignKey(Application, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.title

def notify_teams_channel(sender, instance, created, *args, **kwargs):
    if created:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "[Sifarish] We have a new build!",
            "sections": [{
                "activityTitle": "[Sifarish] We have a new build!",
                "activitySubtitle": "Seems like our developers are on a rush! We have been served with another build to test!",
                "activityImage": "https://dev-sifarish-v2-api.ideabreed.net/api/media/nep_logo_TyWnpAe_orpOmKO.png",
                "facts": [{
                    "name": "Application Name",
                    "value": "Sifarish"
                }, {
                    "name": "Build Push Time",
                    "value": str(instance.created_at)
                }, {
                    "name": "Build Version Number",
                    "value": instance.version
                },{
                    "name": "Build Notes",
                    "value": instance.build_notes
                }],
                "markdown": True
            }],
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "Download Latest Build",
                "targets": [{
                    "os": "default",
                    "uri": "https://sifarish-v2.ideabreed.net/"
                }]
            },
            {
                "@type": "OpenUri",
                "name": "Previous Builds",
                "targets": [{
                    "os": "default",
                    "uri": "https://sifarish-v2.ideabreed.net/"
                }]
            }
            ]
        }
        res = requests.post(instance.application_token.teams_url, data=json.dumps(payload))

post_save.connect(notify_teams_channel, sender = Version, weak = False)