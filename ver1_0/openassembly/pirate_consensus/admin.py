from django.contrib import admin
from pirate_consensus.models import Consensus, UpDownVote, VideoVote, Rating, RankedVote, Spectrum
from pirate_consensus.models import ConfirmRankedVote, WeightedVote, RatingVote, Phase, PhaseLink, RankedDecision

admin.site.register(Consensus)
admin.site.register(UpDownVote)
admin.site.register(VideoVote)
admin.site.register(RankedVote)
admin.site.register(ConfirmRankedVote)
admin.site.register(WeightedVote)
admin.site.register(RatingVote)
admin.site.register(Spectrum)
admin.site.register(Rating)
admin.site.register(Phase)
admin.site.register(PhaseLink)
admin.site.register(RankedDecision)
