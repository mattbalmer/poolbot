from .base import BaseCommand


class LeaderboardCommand(BaseCommand):
    """Returns a leadboard of players, ordered by their wins."""

    default_limit = 10
    command_term = 'leaderboard'
    url_path = 'api/player/'
    help_message = (
        'The leadboard command returns a table of users ranking by their raw '
        'win count.'
    )

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        leaderboard_url = self._generate_url()

        get_params = {
            'active': True,
            'ordering': '-elo'
        }
        response = self.poolbot.session.get(
            leaderboard_url,
            params=get_params,
        )

        if response.status_code == 200:
            limit = self._calculate_limit(message)
            return self.reply(self._generate_response(response.json(), limit))
        else:
            return self.reply('Unable to get leadboard data')

    def _calculate_limit(self, message):
        """Parse the message to see if an additional parameter was passed
        to limit the number of players shown in the leaderboard. If no arg
        is passed, or the arg cannot be cast to an integer, default to 10.
        """
        limit = self.default_limit
        args = self._command_args(message)
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass
        return limit

    def _generate_response(self, data, limit):
        """Parse the returned data and generate a string which takes the form
        of a leaderboard style table, with players ranked from 1 to X.
        """
        leaderboard_row_msg = '{ranking}. {name} [Elo Score: {elo}] ({wins} W / {losses} L)'
        leaderboard_table_rows = []

        for player in data:  # Go through list
            if player['total_win_count'] or player['total_loss_count']:  # See if user has played any games
                leaderboard_table_rows.append(leaderboard_row_msg.format(
                    ranking=len(leaderboard_table_rows) + 1,
                    name=player['name'],
                    wins=player['total_win_count'],
                    losses=player['total_loss_count'],
                    elo=player['elo'])
                )

        # finally only return the rows we actually want
        return ' \n'.join(leaderboard_table_rows[:limit])
