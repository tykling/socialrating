from team.models import Team


def team(request):
    """
    if we have a team_slug url component then get the matching Team object.
    Return context after adding team.
    """
    team = None
    if request.resolver_match and "team_slug" in request.resolver_match.kwargs:
        try:
            team = Team.objects.get(slug=request.resolver_match.kwargs["team_slug"])
        except Team.DoesNotExist:
            pass
    return {"team": team}
