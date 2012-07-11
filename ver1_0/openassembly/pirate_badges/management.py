from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from pirate_forum.templatetags.blobtags import get_models

if "pirate_badges" in settings.INSTALLED_APPS:
    from pirate_badges.models import create_badge_dimension
    import pirate_badges.models as badge_models
    from pirate_consensus.models import UpDownVote, RatingVote
    from pirate_flags.models import Flag
    from pirate_social.models import RelationshipEvent

    def create_badge_types(app, created_models, verbosity, **kwargs):
        #for each forum_blob model, there is an associated badge for content creation
        models = get_models()
        for model in models:
            contenttype = ContentType.objects.get_for_model(model)
            for x in range(25,125,25) + [5]: #badges for content creation of all models
                ht = "Badge for creation of x" + str(x) + " " + str(contenttype) + "s."
                create_badge_dimension(str(contenttype) + " x " + str(x), str(contenttype).lower() + " x " + str(x), ht, 'bronze', contenttype, x, 1)
        for model in (UpDownVote,RatingVote,Flag):
            contenttype = ContentType.objects.get_for_model(model)
            for x in range(25,125,50): #badges for voting on models
                ht = "Badge for your content being voted on with a " + str(contenttype) + " " + str(x) + " times."
                create_badge_dimension(str(contenttype) + " x " + str(x), str(contenttype).lower() + " x " + str(x), ht, 'silver', contenttype, x, 2)
        #for each vote type there is an associated badge related to vote counts
        for model in [RelationshipEvent]:
            contenttype = ContentType.objects.get_for_model(model)
            for x in range(25,125,50): #badges for tag creation
                ht = "Badge for tagging " + str(x) + " times. Taggin' helps Open Assembly run."
                create_badge_dimension("Tag x " + str(x), "tag x " + str(x), ht, 'gold', contenttype, x, 3)
        
        #badges for tagging content
        
        #create_badge_dimension(verbose_name, name, help_text, badge_type, ctype, test_int, test_func)

    signals.post_syncdb.connect(create_badge_types, sender=badge_models)
else:
    print "Skipping creation of pirate_badges, not installed"

